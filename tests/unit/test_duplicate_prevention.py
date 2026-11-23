"""
Unit tests for duplicate crossing prevention, debounce windows, and track pruning.
"""

import pytest
from backend.app.counting.line_counter import LineCounter


@pytest.fixture
def line_counter():
    # Horizontal gate line from (100, 300) to (500, 300)
    return LineCounter(
        gate_line=((100, 300), (500, 300)),
        debounce_seconds=2.0,
        min_distance_px=15.0,
        max_age_frames=10
    )


def test_single_crossing_event(line_counter):
    # Frame 0: Track 1 approaching line
    tracks_f0 = [{
        "track_id": 1,
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.90,
        "bbox": [280, 150, 320, 250],
        "center": [300, 250]
    }]
    events_f0 = line_counter.process_tracks(tracks_f0, frame_idx=0, timestamp=100.0)
    assert len(events_f0) == 0

    # Frame 1: Track 1 crosses line
    tracks_f1 = [{
        "track_id": 1,
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.91,
        "bbox": [280, 250, 320, 350],
        "center": [300, 350]
    }]
    events_f1 = line_counter.process_tracks(tracks_f1, frame_idx=1, timestamp=100.1)
    assert len(events_f1) == 1
    assert events_f1[0]["direction"] == "ENTRY"
    assert line_counter.total_entries == 1


def test_debounce_duplicate_suppression(line_counter):
    # Frame 0: Approaching
    line_counter.process_tracks([{
        "track_id": 2, "class_id": 2, "class_name": "car", "confidence": 0.95,
        "bbox": [250, 100, 350, 200], "center": [300, 200]
    }], frame_idx=0, timestamp=100.0)

    # Frame 1: Crosses line
    events1 = line_counter.process_tracks([{
        "track_id": 2, "class_id": 2, "class_name": "car", "confidence": 0.95,
        "bbox": [250, 250, 350, 350], "center": [300, 350]
    }], frame_idx=1, timestamp=100.1)
    assert len(events1) == 1

    # Frame 2: Oscillates back across line immediately (e.g. 0.5s later, within 2.0s debounce)
    events2 = line_counter.process_tracks([{
        "track_id": 2, "class_id": 2, "class_name": "car", "confidence": 0.94,
        "bbox": [250, 150, 350, 250], "center": [300, 250]
    }], frame_idx=2, timestamp=100.6)
    # Duplicate crossing MUST be suppressed!
    assert len(events2) == 0
    assert line_counter.total_entries == 1
    assert line_counter.total_exits == 0


def test_track_pruning_on_disappearance(line_counter):
    # Register track at frame 0
    line_counter.process_tracks([{
        "track_id": 5, "class_id": 0, "class_name": "person", "confidence": 0.88,
        "bbox": [100, 100, 140, 180], "center": [120, 180]
    }], frame_idx=0, timestamp=100.0)
    assert 5 in line_counter.tracks

    # Advance beyond max_age_frames (10) without track 5 appearing
    line_counter.process_tracks([], frame_idx=20, timestamp=110.0)
    # Track 5 should be pruned from memory
    assert 5 not in line_counter.tracks
