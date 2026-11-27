"""
Unit tests for DeepSORT multi-object tracking and Kalman filter kinematics.
Validates track ID persistence, occlusion recovery, lifecycle state transitions,
and strict CV interface contract compliance.
"""

import numpy as np
import pytest
from backend.app.detection.kalman_filter import KalmanFilter
from backend.app.detection.tracker_deepsort import (
    DeepSortTracker,
    Track,
    TrackState,
    bbox_to_z,
    z_to_bbox,
    compute_iou,
)
from backend.app.detection.detector import DetectionPipeline
from ai.src.inference import GateObjectDetector


def test_bbox_z_conversion():
    bbox = [100, 200, 160, 300]  # w=60, h=100, cx=130, cy=250, a=0.6
    z = bbox_to_z(bbox)
    assert np.isclose(z[0], 130.0)
    assert np.isclose(z[1], 250.0)
    assert np.isclose(z[2], 0.6)
    assert np.isclose(z[3], 100.0)

    recovered_bbox = z_to_bbox(z)
    assert recovered_bbox == bbox


def test_compute_iou():
    box1 = [0, 0, 100, 100]
    box2 = [50, 0, 150, 100]
    # Inter: 50x100 = 5000; Union: 10000 + 10000 - 5000 = 15000; IoU = 1/3
    iou = compute_iou(box1, box2)
    assert np.isclose(iou, 1.0 / 3.0)

    non_overlapping = [200, 200, 300, 300]
    assert compute_iou(box1, non_overlapping) == 0.0


def test_kalman_filter_predict_update():
    kf = KalmanFilter()
    z = np.array([200.0, 300.0, 0.5, 100.0])
    mean, cov = kf.initiate(z)

    assert mean.shape == (8,)
    assert cov.shape == (8, 8)
    assert np.allclose(mean[:4], z)

    # Predict
    pred_mean, pred_cov = kf.predict(mean, cov)
    assert pred_mean.shape == (8,)
    # Observation with slight movement
    z_next = np.array([205.0, 308.0, 0.5, 100.0])
    upd_mean, upd_cov = kf.update(pred_mean, pred_cov, z_next)

    # Uncertainty should be updated and velocities estimated
    assert upd_mean[4] > 0  # vx should be positive
    assert upd_mean[5] > 0  # vy should be positive


def test_deepsort_track_lifecycle_and_confirmation():
    tracker = DeepSortTracker(max_age=5, n_init=2)

    # Frame 1: Initial detection -> Tentative (since n_init=2)
    det_f1 = [{
        "track_id": -1,
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.88,
        "bbox": [100, 100, 150, 250],
        "center": [125, 250]
    }]
    tracks_f1 = tracker.update(det_f1)
    # Since n_init=2, not yet confirmed, so not emitted
    assert len(tracks_f1) == 0
    assert len(tracker.tracks) == 1
    assert tracker.tracks[0].state == TrackState.Tentative

    # Frame 2: Matched detection -> Transition to Confirmed
    det_f2 = [{
        "track_id": -1,
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.90,
        "bbox": [103, 105, 153, 255],
        "center": [128, 255]
    }]
    tracks_f2 = tracker.update(det_f2)
    assert len(tracks_f2) == 1
    assert tracks_f2[0]["track_id"] == 1
    assert tracker.tracks[0].state == TrackState.Confirmed


def test_deepsort_track_id_persistence_and_movement():
    tracker = DeepSortTracker(max_age=10, n_init=1)

    # Frame 1: Vehicle appears
    tracks_f1 = tracker.update([{
        "track_id": -1,
        "class_id": 2,
        "class_name": "car",
        "confidence": 0.95,
        "bbox": [200, 300, 320, 420],
        "center": [260, 420]
    }])
    assert len(tracks_f1) == 1
    car_id = tracks_f1[0]["track_id"]

    # Frame 2-5: Vehicle drives forward
    for step in range(1, 5):
        offset = step * 15
        tracks = tracker.update([{
            "track_id": -1,
            "class_id": 2,
            "class_name": "car",
            "confidence": 0.94,
            "bbox": [200, 300 + offset, 320, 420 + offset],
            "center": [260, 420 + offset]
        }])
        assert len(tracks) == 1
        assert tracks[0]["track_id"] == car_id, f"Track ID changed at step {step}"


def test_deepsort_occlusion_recovery():
    """
    Simulates a target temporarily occluded for 2 frames behind a gate structure.
    Kalman filter predicts its trajectory and successfully re-associates the ID.
    """
    tracker = DeepSortTracker(max_age=10, n_init=1)

    # Frame 1: Person enters
    t1 = tracker.update([{
        "track_id": -1,
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.92,
        "bbox": [300, 200, 360, 350],
        "center": [330, 350]
    }])
    original_id = t1[0]["track_id"]

    # Frame 2: Person walking downwards (cy moving 350 -> 370)
    tracker.update([{
        "track_id": -1,
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.93,
        "bbox": [302, 220, 362, 370],
        "center": [332, 370]
    }])

    # Frame 3 & 4: OCCLUSION! No detection emitted (e.g. blocked by gate pillar)
    tracker.update([])
    tracker.update([])

    # Frame 5: Person re-emerges near predicted location (cy ~ 430)
    reemerged = tracker.update([{
        "track_id": -1,
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.89,
        "bbox": [306, 280, 366, 430],
        "center": [336, 430]
    }])

    assert len(reemerged) == 1
    assert reemerged[0]["track_id"] == original_id, (
        f"Expected track ID {original_id} after occlusion recovery, got {reemerged[0]['track_id']}"
    )


def test_deepsort_prunes_stale_tracks():
    tracker = DeepSortTracker(max_age=3, n_init=1)

    tracker.update([{
        "track_id": -1,
        "class_id": 1,
        "class_name": "bicycle",
        "confidence": 0.85,
        "bbox": [50, 50, 90, 110],
        "center": [70, 110]
    }])
    assert len(tracker.tracks) == 1

    # Disappears for 4 frames (> max_age=3)
    for _ in range(4):
        tracker.update([])

    assert len(tracker.tracks) == 0


def test_cv_contract_schema_compliance():
    tracker = DeepSortTracker(n_init=1)
    res = tracker.update([{
        "track_id": -1,
        "class_id": 5,
        "class_name": "truck",
        "confidence": 0.912345,
        "bbox": [400, 150, 600, 450],
        "center": [500, 450]
    }])

    assert len(res) == 1
    item = res[0]
    assert isinstance(item["track_id"], int)
    assert item["track_id"] > 0
    assert item["class_id"] == 5
    assert item["class_name"] == "truck"
    assert isinstance(item["confidence"], float)
    assert item["confidence"] == 0.9123
    assert len(item["bbox"]) == 4
    assert item["bbox"][0] < item["bbox"][2]
    assert item["bbox"][1] < item["bbox"][3]
    # Check bottom-center centroid convention
    assert item["center"] == [(item["bbox"][0] + item["bbox"][2]) // 2, item["bbox"][3]]


def test_detection_pipeline_with_deepsort():
    detector = GateObjectDetector(yolo_model=None)
    pipeline = DetectionPipeline(detector=detector, tracker=DeepSortTracker(n_init=1))

    # Synthetic 720p frame
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    gate_line = ((100, 240), (540, 240))

    annotated_frame, tracked = pipeline.process_frame(dummy_frame, gate_line)
    assert annotated_frame.shape == (480, 640, 3)
    assert isinstance(tracked, list)
