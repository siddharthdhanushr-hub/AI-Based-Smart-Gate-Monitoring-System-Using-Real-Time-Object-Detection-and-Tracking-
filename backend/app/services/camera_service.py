"""
Camera capture service with support for webcams, recorded video files,
and synthetic frame generation for headless/testing environments.
"""

from typing import Optional, Tuple, Generator
import cv2
import numpy as np
import os
import time
import threading
import logging
from backend.app.core.config import settings

logger = logging.getLogger("gate_monitoring.camera")


class CameraService:
    """Manages video frame ingestion and thread-safe frame access."""

    def __init__(self):
        self.source_type = "webcam"
        self.source_value = settings.DEFAULT_CAMERA_SOURCE
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.current_frame: Optional[np.ndarray] = None
        self.annotated_frame: Optional[np.ndarray] = None
        self.lock = threading.Lock()
        self.worker_thread: Optional[threading.Thread] = None
        self.fps = 0.0
        self.frame_count = 0
        self.is_synthetic = False

    def start(self, source: Optional[str] = None) -> bool:
        """Starts video ingestion thread."""
        with self.lock:
            if self.is_running:
                return True

            self.current_frame = None
            self.annotated_frame = None
            if source is not None:
                self.source_value = str(source)
                self.source_type = "file" if (os_is_file := not source.isdigit()) else "webcam"

            self._open_capture()
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.worker_thread.start()
            logger.info(f"Camera service started with source: {self.source_value} (synthetic={self.is_synthetic})")
            return True

    def stop(self) -> bool:
        """Stops video ingestion."""
        with self.lock:
            self.is_running = False

        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.5)

        with self.lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.current_frame = None
            self.annotated_frame = None
            logger.info("Camera service stopped.")
            return True

    def switch_source(self, source_type: str, source_value: str) -> bool:
        """Dynamically switches camera source."""
        was_running = self.is_running
        self.stop()
        self.source_type = source_type
        self.source_value = source_value
        if was_running:
            return self.start(source_value)
        return True

    def _open_capture(self) -> None:
        """Attempts to open physical/file source or falls back to synthetic frames."""
        self.is_synthetic = False
        try:
            val_str = str(self.source_value).strip().lower()
            if val_str in ("synthetic", "simulation", "sim"):
                self.is_synthetic = True
                self.cap = None
                return

            if self.source_value.isdigit():
                idx = int(self.source_value)
                self.cap = cv2.VideoCapture(idx)
            else:
                video_path = self.source_value
                if not os.path.isabs(video_path) and not os.path.exists(video_path):
                    candidate = os.path.join(os.getcwd(), video_path)
                    if os.path.exists(candidate):
                        video_path = candidate
                self.cap = cv2.VideoCapture(video_path)

            if not self.cap.isOpened():
                logger.warning(f"Unable to open video source {self.source_value}. Falling back to synthetic stream.")
                self.is_synthetic = True
                self.cap = None
        except Exception as e:
            logger.warning(f"Error opening capture: {e}. Falling back to synthetic stream.")
            self.is_synthetic = True
            self.cap = None

    def _generate_synthetic_frame(self, frame_idx: int) -> np.ndarray:
        """Generates a realistic test gate frame with moving entities for verification."""
        w, h = settings.FRAME_WIDTH, settings.FRAME_HEIGHT
        frame = np.full((h, w, 3), 40, dtype=np.uint8)  # Dark asphalt background

        # Draw road / gate lane boundaries
        cv2.line(frame, (200, 0), (200, h), (100, 100, 100), 2)
        cv2.line(frame, (w - 200, 0), (w - 200, h), (100, 100, 100), 2)
        cv2.putText(frame, "GATE ACCESS LANE", (w // 2 - 120, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        # Draw synthetic moving car
        y_pos = int((frame_idx * 4) % (h + 100)) - 50
        x_pos = w // 2 - 60
        if 0 <= y_pos <= h:
            cv2.rectangle(frame, (x_pos, y_pos), (x_pos + 120, y_pos + 80), (180, 80, 50), -1)
            cv2.putText(frame, "TEST VEHICLE", (x_pos, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Status text
        cv2.putText(
            frame, f"FEED: SYNTHETIC (NO CAMERA ATTACHED) | FRAME: {frame_idx}",
            (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1
        )
        return frame

    def _capture_loop(self) -> None:
        """Continuous background capture loop."""
        prev_time = time.time()
        while self.is_running:
            frame = None
            if not self.is_synthetic and self.cap is not None:
                ret, raw = self.cap.read()
                if ret:
                    frame = raw
                    # Check for dark frame or shutter block on physical webcam
                    if self.source_type == "webcam" and np.mean(raw) < 5.0:
                        cv2.rectangle(frame, (10, 10), (frame.shape[1] - 10, 75), (25, 25, 25), -1)
                        cv2.rectangle(frame, (10, 10), (frame.shape[1] - 10, 75), (0, 140, 255), 2)
                        cv2.putText(
                            frame, "[!] WEBCAM PRIVACY SHUTTER CLOSED / PERMISSION BLOCKED",
                            (25, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 2
                        )
                        cv2.putText(
                            frame, "Uncover camera or select Sample Gate Video in Dashboard",
                            (25, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1
                        )
                else:
                    # If recorded video reached end, loop it
                    if self.source_type == "file":
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, raw = self.cap.read()
                        if ret:
                            frame = raw
                    else:
                        logger.warning("Frame read failed. Switching to synthetic fallback.")
                        self.is_synthetic = True

            if frame is None or self.is_synthetic:
                frame = self._generate_synthetic_frame(self.frame_count)
                time.sleep(0.033)  # Emulate ~30 FPS

            # Calculate FPS
            now = time.time()
            dt = now - prev_time
            if dt > 0:
                self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)
            prev_time = now
            self.frame_count += 1

            with self.lock:
                self.current_frame = frame

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Thread-safe retrieval of latest frame."""
        with self.lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None

    def set_annotated_frame(self, frame: np.ndarray) -> None:
        """Publishes an inference-annotated frame for the MJPEG stream."""
        with self.lock:
            self.annotated_frame = frame.copy()

    def get_latest_stream_frame(self) -> Optional[np.ndarray]:
        """Returns the newest annotated frame, or the raw frame before inference starts."""
        with self.lock:
            frame = self.annotated_frame if self.annotated_frame is not None else self.current_frame
            return frame.copy() if frame is not None else None

    def get_mjpeg_stream(self) -> Generator[bytes, None, None]:
        """Generator yielding MJPEG multipart byte frames."""
        while self.is_running:
            frame = self.get_latest_stream_frame()
            if frame is None:
                time.sleep(0.03)
                continue

            success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if not success:
                continue

            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )
            time.sleep(0.03)


camera_service = CameraService()
