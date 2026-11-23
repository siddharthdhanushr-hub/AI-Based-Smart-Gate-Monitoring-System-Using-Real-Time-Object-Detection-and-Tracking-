"""
Gate line crossing detector and directional entry/exit counter.
Maintains trajectory history per track ID, debounces jitter, and handles tracking gaps.
"""

from typing import Dict, List, Tuple, Any, Optional
import time
from backend.app.counting.gate_geometry import GateLine, Point


class TrackState:
    """Internal state tracking for an individual object."""

    def __init__(self, track_id: int, initial_point: Point, class_name: str, class_id: int, frame_idx: int):
        self.track_id = track_id
        self.class_name = class_name
        self.class_id = class_id
        self.positions: List[Point] = [initial_point]
        self.last_seen_frame = frame_idx
        self.last_crossed_time: Optional[float] = None
        self.last_crossed_direction: Optional[str] = None
        self.last_crossed_point: Optional[Point] = None

    def add_position(self, pt: Point, frame_idx: int, max_history: int = 30) -> None:
        self.positions.append(pt)
        if len(self.positions) > max_history:
            self.positions.pop(0)
        self.last_seen_frame = frame_idx


class LineCounter:
    """
    Evaluates tracks against a virtual gate line.
    Emits crossing events while eliminating duplicates and handling track loss.
    """

    def __init__(
        self,
        gate_line: Tuple[Tuple[int, int], Tuple[int, int]],
        debounce_seconds: float = 3.0,
        min_distance_px: float = 15.0,
        max_age_frames: int = 30
    ):
        self.gate_line = GateLine(gate_line[0], gate_line[1])
        self.debounce_seconds = debounce_seconds
        self.min_distance_px = min_distance_px
        self.max_age_frames = max_age_frames

        self.tracks: Dict[int, TrackState] = {}
        self.total_entries = 0
        self.total_exits = 0
        self.class_counts: Dict[str, Dict[str, int]] = {
            "person": {"entry": 0, "exit": 0},
            "bicycle": {"entry": 0, "exit": 0},
            "car": {"entry": 0, "exit": 0},
            "motorcycle": {"entry": 0, "exit": 0},
            "bus": {"entry": 0, "exit": 0},
            "truck": {"entry": 0, "exit": 0}
        }

    def update_gate_line(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> None:
        """Dynamically reconfigures the virtual gate line."""
        self.gate_line = GateLine(p1, p2)

    def process_tracks(
        self,
        tracked_objects: List[Dict[str, Any]],
        frame_idx: int,
        timestamp: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Processes tracked objects for the current frame.
        Returns a list of newly triggered gate crossing event dictionaries.
        """
        now = timestamp if timestamp is not None else time.time()
        crossing_events: List[Dict[str, Any]] = []

        seen_track_ids = set()

        for obj in tracked_objects:
            track_id = obj.get("track_id", -1)
            if track_id < 0:
                # Raw untracked detection - cannot compute trajectory
                continue

            seen_track_ids.add(track_id)
            cx, cy = obj.get("center", (0, 0))
            curr_pt = Point(cx, cy)
            class_name = obj.get("class_name", "unknown").lower()
            class_id = obj.get("class_id", 0)
            confidence = obj.get("confidence", 0.0)
            bbox = obj.get("bbox", [0, 0, 0, 0])

            if track_id not in self.tracks:
                self.tracks[track_id] = TrackState(track_id, curr_pt, class_name, class_id, frame_idx)
                continue

            track = self.tracks[track_id]
            prev_pt = track.positions[-1]
            track.add_position(curr_pt, frame_idx)

            # Check if trajectory segment [prev_pt, curr_pt] crosses gate line
            direction = self.gate_line.classify_movement_direction(prev_pt, curr_pt)

            if direction is not None:
                # Check debounce conditions
                is_duplicate = False

                if track.last_crossed_time is not None:
                    time_since_cross = now - track.last_crossed_time
                    if time_since_cross < self.debounce_seconds:
                        is_duplicate = True

                if not is_duplicate and track.last_crossed_point is not None:
                    dist_from_last = curr_pt.distance_to(track.last_crossed_point)
                    if dist_from_last < self.min_distance_px:
                        is_duplicate = True

                if not is_duplicate:
                    # Register valid crossing
                    track.last_crossed_time = now
                    track.last_crossed_direction = direction
                    track.last_crossed_point = curr_pt

                    if direction == "ENTRY":
                        self.total_entries += 1
                        if class_name in self.class_counts:
                            self.class_counts[class_name]["entry"] += 1
                    else:
                        self.total_exits += 1
                        if class_name in self.class_counts:
                            self.class_counts[class_name]["exit"] += 1

                    event_data = {
                        "track_id": track_id,
                        "class_id": class_id,
                        "class_name": class_name,
                        "direction": direction,
                        "confidence": confidence,
                        "bbox": bbox,
                        "centroid": [curr_pt.to_tuple()[0], curr_pt.to_tuple()[1]],
                        "timestamp": now
                    }
                    crossing_events.append(event_data)

        # Prune stale tracks that have left the frame
        stale_ids = [
            tid for tid, state in self.tracks.items()
            if (frame_idx - state.last_seen_frame) > self.max_age_frames
        ]
        for tid in stale_ids:
            del self.tracks[tid]

        return crossing_events
