"""
DeepSORT Multi-Object Tracking Engine.
Implements Kalman filter motion prediction, Track lifecycle management
(Tentative -> Confirmed -> Deleted), IoU and spatial association matching,
and strictly conforms to the agreed CV contract schema.
"""

from enum import Enum
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from backend.app.detection.kalman_filter import KalmanFilter


class TrackState(str, Enum):
    Tentative = "tentative"
    Confirmed = "confirmed"
    Deleted = "deleted"


def bbox_to_z(bbox: List[int]) -> np.ndarray:
    """
    Converts [x1, y1, x2, y2] to [cx, cy, a, h].
    where cx, cy is center, a is aspect ratio (w/h), h is height.
    """
    x1, y1, x2, y2 = bbox
    w = max(1.0, float(x2 - x1))
    h = max(1.0, float(y2 - y1))
    cx = float(x1) + w / 2.0
    cy = float(y1) + h / 2.0
    a = w / h
    return np.array([cx, cy, a, h], dtype=np.float64)


def z_to_bbox(mean: np.ndarray) -> List[int]:
    """
    Converts [cx, cy, a, h, ...] to [x1, y1, x2, y2].
    """
    cx, cy, a, h = mean[:4]
    w = a * h
    x1 = int(round(cx - w / 2.0))
    y1 = int(round(cy - h / 2.0))
    x2 = int(round(cx + w / 2.0))
    y2 = int(round(cy + h / 2.0))
    return [max(0, x1), max(0, y1), max(x1 + 1, x2), max(y1 + 1, y2)]


def compute_iou(bbox1: List[int], bbox2: List[int]) -> float:
    """Computes Intersection over Union (IoU) between two bounding boxes."""
    x1 = max(bbox1[0], bbox2[0])
    y1 = max(bbox1[1], bbox2[1])
    x2 = min(bbox1[2], bbox2[2])
    y2 = min(bbox1[3], bbox2[3])

    inter_w = max(0, x2 - x1)
    inter_h = max(0, y2 - y1)
    inter_area = inter_w * inter_h

    area1 = max(0, (bbox1[2] - bbox1[0])) * max(0, (bbox1[3] - bbox1[1]))
    area2 = max(0, (bbox2[2] - bbox2[0])) * max(0, (bbox2[3] - bbox2[1]))
    union_area = area1 + area2 - inter_area

    if union_area <= 0:
        return 0.0
    return float(inter_area) / float(union_area)


def linear_assignment(
    cost_matrix: np.ndarray, thresh: float
) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    """
    Bipartite matching solving linear sum assignment.
    Falls back to greedy matching if scipy is not installed.
    """
    if cost_matrix.size == 0:
        return [], list(range(cost_matrix.shape[0])), list(range(cost_matrix.shape[1]))

    try:
        from scipy.optimize import linear_sum_assignment
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
    except ImportError:
        # Robust greedy matching fallback
        matched_indices = []
        rows = cost_matrix.shape[0]
        cols = cost_matrix.shape[1]
        flat_order = np.argsort(cost_matrix, axis=None)
        used_rows = set()
        used_cols = set()
        for idx in flat_order:
            r = idx // cols
            c = idx % cols
            if r not in used_rows and c not in used_cols:
                if cost_matrix[r, c] <= thresh:
                    matched_indices.append((r, c))
                    used_rows.add(r)
                    used_cols.add(c)
        row_indices = [r for r, _ in matched_indices]
        col_indices = [c for _, c in matched_indices]

    matches = []
    unmatched_rows = list(range(cost_matrix.shape[0]))
    unmatched_cols = list(range(cost_matrix.shape[1]))

    for r, c in zip(row_indices, col_indices):
        if cost_matrix[r, c] <= thresh:
            matches.append((r, c))
            if r in unmatched_rows:
                unmatched_rows.remove(r)
            if c in unmatched_cols:
                unmatched_cols.remove(c)

    return matches, unmatched_rows, unmatched_cols


class Track:
    """Represents a single tracked target with Kalman filter state."""

    def __init__(
        self,
        mean: np.ndarray,
        covariance: np.ndarray,
        track_id: int,
        class_id: int,
        class_name: str,
        confidence: float,
        n_init: int = 1,
        max_age: int = 30
    ):
        self.mean = mean
        self.covariance = covariance
        self.track_id = track_id
        self.class_id = class_id
        self.class_name = class_name
        self.confidence = confidence

        self.hits = 1
        self.age = 1
        self.time_since_update = 0
        self.n_init = n_init
        self.max_age = max_age

        self.state = TrackState.Confirmed if n_init <= 1 else TrackState.Tentative

    def predict(self, kf: KalmanFilter) -> None:
        """Propagate state forward using the Kalman filter."""
        self.mean, self.covariance = kf.predict(self.mean, self.covariance)
        self.age += 1
        self.time_since_update += 1

    def update(self, kf: KalmanFilter, detection: Dict[str, Any]) -> None:
        """Update Kalman filter state with new detection."""
        meas = bbox_to_z(detection["bbox"])
        self.mean, self.covariance = kf.update(self.mean, self.covariance, meas)
        self.confidence = float(detection.get("confidence", self.confidence))
        self.class_id = int(detection.get("class_id", self.class_id))
        self.class_name = str(detection.get("class_name", self.class_name))

        self.hits += 1
        self.time_since_update = 0

        if self.state == TrackState.Tentative and self.hits >= self.n_init:
            self.state = TrackState.Confirmed

    def mark_missed(self) -> None:
        """Mark track as missed in current frame."""
        if self.state == TrackState.Tentative:
            self.state = TrackState.Deleted
        elif self.time_since_update > self.max_age:
            self.state = TrackState.Deleted

    def is_confirmed(self) -> bool:
        return self.state == TrackState.Confirmed

    def is_deleted(self) -> bool:
        return self.state == TrackState.Deleted

    def to_tlbr(self) -> List[int]:
        """Returns [x1, y1, x2, y2]."""
        return z_to_bbox(self.mean)

    def to_contract_dict(self) -> Dict[str, Any]:
        """
        Formats track strictly conforming to agreed schema:
        {track_id, class_id, class_name, confidence, bbox, center}
        """
        bbox = self.to_tlbr()
        x1, y1, x2, y2 = bbox
        cx = int((x1 + x2) // 2)
        cy = int(y2)  # bottom-center ground base to eliminate parallax error

        return {
            "track_id": int(self.track_id),
            "class_id": int(self.class_id),
            "class_name": str(self.class_name),
            "confidence": round(float(self.confidence), 4),
            "bbox": [x1, y1, x2, y2],
            "center": [cx, cy]
        }


class DeepSortTracker:
    """
    Multi-Object Tracker combining 8D Kalman filtering and bipartite matching.
    """

    def __init__(
        self,
        max_age: int = 30,
        n_init: int = 1,
        max_iou_distance: float = 0.7
    ):
        self.max_age = max_age
        self.n_init = n_init
        self.max_iou_distance = max_iou_distance
        self.kf = KalmanFilter()
        self.tracks: List[Track] = []
        self._next_id = 1

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Updates tracks given current frame detections.
        Parameters:
            detections: List of dicts matching detection contract.
        Returns:
            List of active confirmed tracks formatted as contract dicts.
        """
        # Step 1: Predict new locations of existing tracks
        for track in self.tracks:
            track.predict(self.kf)

        # Step 2: Associate detections with existing tracks
        if not self.tracks or not detections:
            matched, unmatched_tracks, unmatched_dets = [], list(range(len(self.tracks))), list(range(len(detections)))
        else:
            cost_matrix = np.zeros((len(self.tracks), len(detections)), dtype=np.float64)
            for i, track in enumerate(self.tracks):
                track_box = track.to_tlbr()
                for j, det in enumerate(detections):
                    det_box = det["bbox"]
                    iou = compute_iou(track_box, det_box)
                    # Penalize class mismatch if classes differ
                    class_penalty = 0.0 if track.class_id == det.get("class_id", track.class_id) else 0.5
                    cost_matrix[i, j] = (1.0 - iou) + class_penalty

            matched, unmatched_tracks, unmatched_dets = linear_assignment(
                cost_matrix, thresh=self.max_iou_distance
            )

        # Step 3: Update matched tracks
        for track_idx, det_idx in matched:
            self.tracks[track_idx].update(self.kf, detections[det_idx])

        # Step 4: Handle unmatched tracks
        for track_idx in unmatched_tracks:
            self.tracks[track_idx].mark_missed()

        # Step 5: Handle unmatched detections by creating new tracks
        for det_idx in unmatched_dets:
            det = detections[det_idx]
            z = bbox_to_z(det["bbox"])
            mean, cov = self.kf.initiate(z)
            new_track = Track(
                mean=mean,
                covariance=cov,
                track_id=self._next_id,
                class_id=det.get("class_id", 0),
                class_name=det.get("class_name", "person"),
                confidence=det.get("confidence", 0.5),
                n_init=self.n_init,
                max_age=self.max_age
            )
            self._next_id += 1
            self.tracks.append(new_track)

        # Step 6: Prune deleted tracks
        self.tracks = [t for t in self.tracks if not t.is_deleted()]

        # Step 7: Return active confirmed tracks
        results = []
        for track in self.tracks:
            if track.is_confirmed() and track.time_since_update == 0:
                results.append(track.to_contract_dict())

        return results
