"""
Detector and Tracking wrapper implementing the agreed CV interface contract.
Provides both standard YOLO detection and a centroid-association tracker
for local testing before DeepSORT integration.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from ai.src.inference import GateObjectDetector
from backend.app.detection.tracker_deepsort import DeepSortTracker


class SimpleCentroidTracker:
    """
    Lightweight Euclidean distance centroid tracker for local testing
    and seamless integration testing before Chandrashekar's DeepSORT module lands.
    """

    def __init__(self, max_disappeared: int = 15, max_distance: float = 200.0):
        self.next_id = 1
        self.objects: Dict[int, Tuple[int, int]] = {}
        self.disappeared: Dict[int, int] = {}
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not detections:
            # Increment disappeared for all existing objects
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    del self.objects[obj_id]
                    del self.disappeared[obj_id]
            return []

        input_centroids = [d["center"] for d in detections]

        if not self.objects:
            # Register all incoming detections
            tracked: List[Dict[str, Any]] = []
            for i, d in enumerate(detections):
                obj_id = self.next_id
                self.next_id += 1
                self.objects[obj_id] = tuple(input_centroids[i])
                self.disappeared[obj_id] = 0
                d_copy = dict(d)
                d_copy["track_id"] = obj_id
                tracked.append(d_copy)
            return tracked

        # Match existing centroids to input centroids
        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        # Compute Euclidean distance matrix
        dists = np.zeros((len(object_centroids), len(input_centroids)))
        for i, (ox, oy) in enumerate(object_centroids):
            for j, (ix, iy) in enumerate(input_centroids):
                dists[i, j] = np.hypot(ox - ix, oy - iy)

        rows = dists.min(axis=1).argsort()
        cols = dists.argmin(axis=1)[rows]

        used_rows = set()
        used_cols = set()
        tracked = []

        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue
            if dists[row, col] > self.max_distance:
                continue

            obj_id = object_ids[row]
            self.objects[obj_id] = tuple(input_centroids[col])
            self.disappeared[obj_id] = 0

            d_copy = dict(detections[col])
            d_copy["track_id"] = obj_id
            tracked.append(d_copy)

            used_rows.add(row)
            used_cols.add(col)

        # Handle unmatched existing objects
        unused_rows = set(range(len(object_centroids))) - used_rows
        for row in unused_rows:
            obj_id = object_ids[row]
            self.disappeared[obj_id] += 1
            if self.disappeared[obj_id] > self.max_disappeared:
                del self.objects[obj_id]
                del self.disappeared[obj_id]

        # Register new objects
        unused_cols = set(range(len(input_centroids))) - used_cols
        for col in unused_cols:
            obj_id = self.next_id
            self.next_id += 1
            self.objects[obj_id] = tuple(input_centroids[col])
            self.disappeared[obj_id] = 0

            d_copy = dict(detections[col])
            d_copy["track_id"] = obj_id
            tracked.append(d_copy)

        return tracked


class DetectionPipeline:
    """Combines YOLO detector and object tracker."""

    def __init__(self, detector: GateObjectDetector, tracker: Optional[Any] = None):
        self.detector = detector
        self.tracker = tracker if tracker is not None else DeepSortTracker()

    def process_frame(
        self,
        frame: np.ndarray,
        gate_line: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
    ) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Runs detection and tracking on a frame.
        Returns:
            annotated_frame: np.ndarray
            tracked_objects: List of dictionaries matching Chandrashekar's contract.
        """
        detections = self.detector.detect(frame)
        tracked_objects = self.tracker.update(detections)
        annotated_frame = self.detector.annotate_frame(frame, tracked_objects, gate_line)
        return annotated_frame, tracked_objects
