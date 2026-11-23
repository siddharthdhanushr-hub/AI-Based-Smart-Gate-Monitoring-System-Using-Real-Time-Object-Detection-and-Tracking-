"""
Integration test for the end-to-end monitoring pipeline:
Detection -> Tracking -> Line Crossing -> Database Persistence -> Stats Update.
"""

import numpy as np
from backend.app.counting.line_counter import LineCounter
from backend.app.database import crud
from backend.app.detection.detector import SimpleCentroidTracker


def test_end_to_end_pipeline_simulation(db_session):
    # Setup gate line
    gate_line = ((100, 300), (500, 300))
    counter = LineCounter(gate_line=gate_line, debounce_seconds=1.0)
    tracker = SimpleCentroidTracker()

    # Step 1: Object detected in upper region at frame 0
    raw_detections_f0 = [{
        "track_id": -1,
        "class_id": 2,
        "class_name": "car",
        "confidence": 0.94,
        "bbox": [250, 100, 350, 200],
        "center": [300, 200]
    }]
    tracks_f0 = tracker.update(raw_detections_f0)
    assert len(tracks_f0) == 1
    assert tracks_f0[0]["track_id"] > 0
    assigned_track_id = tracks_f0[0]["track_id"]

    events_f0 = counter.process_tracks(tracks_f0, frame_idx=0, timestamp=1.0)
    assert len(events_f0) == 0  # Not crossed yet

    # Step 2: Object moves across the gate line at frame 1
    raw_detections_f1 = [{
        "track_id": -1,
        "class_id": 2,
        "class_name": "car",
        "confidence": 0.95,
        "bbox": [250, 250, 350, 350],
        "center": [300, 350]
    }]
    tracks_f1 = tracker.update(raw_detections_f1)
    assert len(tracks_f1) == 1
    assert tracks_f1[0]["track_id"] == assigned_track_id

    events_f1 = counter.process_tracks(tracks_f1, frame_idx=1, timestamp=1.1)
    assert len(events_f1) == 1
    crossing = events_f1[0]
    assert crossing["direction"] == "ENTRY"
    assert crossing["track_id"] == assigned_track_id

    # Step 3: Persist event into database
    db_event = crud.record_crossing_event(
        db=db_session,
        track_id=crossing["track_id"],
        class_id=crossing["class_id"],
        class_name=crossing["class_name"],
        direction=crossing["direction"],
        confidence=crossing["confidence"],
        bbox=crossing["bbox"],
        centroid=crossing["centroid"]
    )
    assert db_event.id is not None

    # Step 4: Verify realtime stats query reflects the pipeline event
    stats = crud.get_realtime_stats(db_session)
    assert stats["total_entries"] == 1
    assert stats["today"]["entries"] == 1
    assert stats["today"]["vehicle_entries"] == 1
    assert stats["by_class"]["car"]["entry"] == 1
