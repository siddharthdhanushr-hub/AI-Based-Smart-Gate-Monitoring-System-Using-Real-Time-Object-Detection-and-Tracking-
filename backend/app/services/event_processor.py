"""
Event Processor and Monitoring Orchestrator.
Coordinates camera ingestion, detection, tracking, line crossing logic,
database persistence, and WebSocket broadcasting.
"""

from typing import Optional, Tuple
import asyncio
import time
import logging
from datetime import datetime, timezone
from backend.app.core.config import settings
from backend.app.database.session import SessionLocal
from backend.app.database.crud import record_crossing_event, log_system_alert, get_realtime_stats
from backend.app.detection.model_loader import ModelLoader
from backend.app.detection.detector import DetectionPipeline
from backend.app.counting.line_counter import LineCounter
from backend.app.services.camera_service import camera_service
from backend.app.services.connection_manager import connection_manager

logger = logging.getLogger("gate_monitoring.processor")


class MonitoringProcessor:
    """Manages continuous detection, tracking, counting, and notification cycle."""

    def __init__(self):
        detector = ModelLoader.get_detector()
        self.pipeline = DetectionPipeline(detector)
        self.counter = LineCounter(
            gate_line=(settings.GATE_LINE_P1, settings.GATE_LINE_P2),
            debounce_seconds=settings.DEBOUNCE_SECONDS,
            min_distance_px=settings.MIN_CROSSING_DISTANCE_PX,
            max_age_frames=settings.TRACK_MAX_AGE_FRAMES
        )
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.frame_index = 0
        self.gate_line = (settings.GATE_LINE_P1, settings.GATE_LINE_P2)

    def set_gate_line(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> None:
        self.gate_line = (p1, p2)
        self.counter.update_gate_line(p1, p2)

    async def start(self) -> None:
        """Starts monitoring pipeline background loop."""
        if self.is_running:
            return
        self.is_running = True
        camera_service.start()
        self.task = asyncio.create_task(self._processing_loop())
        logger.info("MonitoringProcessor loop launched.")

    async def stop(self) -> None:
        """Stops monitoring pipeline."""
        self.is_running = False
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        camera_service.stop()
        logger.info("MonitoringProcessor loop stopped.")

    async def _processing_loop(self) -> None:
        """Main asynchronous processing loop."""
        last_heartbeat = time.time()

        while self.is_running:
            try:
                frame = camera_service.get_latest_frame()
                if frame is None:
                    await asyncio.sleep(0.02)
                    continue

                # Run detection and tracking
                annotated_frame, tracked_objects = self.pipeline.process_frame(frame, self.gate_line)
                now_ts = time.time()

                # Process line crossing
                events = self.counter.process_tracks(tracked_objects, self.frame_index, now_ts)
                self.frame_index += 1

                # If crossing events occurred, persist and broadcast immediately
                if events:
                    db = SessionLocal()
                    try:
                        for ev in events:
                            db_event = record_crossing_event(
                                db=db,
                                track_id=ev["track_id"],
                                class_id=ev["class_id"],
                                class_name=ev["class_name"],
                                direction=ev["direction"],
                                confidence=ev["confidence"],
                                bbox=ev["bbox"],
                                centroid=ev["centroid"]
                            )

                            # Broadcast live event over WebSocket
                            ws_message = {
                                "type": "GATE_CROSSING",
                                "payload": {
                                    "event_id": db_event.event_id,
                                    "track_id": ev["track_id"],
                                    "class_name": ev["class_name"],
                                    "direction": ev["direction"],
                                    "confidence": ev["confidence"],
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                }
                            }
                            await connection_manager.broadcast(ws_message)
                    finally:
                        db.close()

                # Periodic stats update broadcast (every 1 second)
                if (now_ts - last_heartbeat) >= 1.0:
                    last_heartbeat = now_ts
                    db = SessionLocal()
                    try:
                        stats = get_realtime_stats(db)
                        ws_heartbeat = {
                            "type": "STATS_UPDATE",
                            "payload": {
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "total_entries": stats["total_entries"],
                                "total_exits": stats["total_exits"],
                                "current_tracked_objects": len(tracked_objects),
                                "camera_fps": round(camera_service.fps, 1)
                            }
                        }
                        await connection_manager.broadcast(ws_heartbeat)
                    finally:
                        db.close()

                await asyncio.sleep(0.01)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(0.1)


monitoring_processor = MonitoringProcessor()
