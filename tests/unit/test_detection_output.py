"""
Unit tests validating detection/tracking output against Chandrashekar's contract.
"""

import pytest
from pydantic import ValidationError
from backend.app.schemas.detection import DetectionItem


def test_valid_detection_item(sample_detection_payload):
    item = DetectionItem(**sample_detection_payload)
    assert item.track_id == 12
    assert item.class_id == 0
    assert item.class_name == "person"
    assert item.confidence == 0.92
    assert item.bbox == [100, 120, 240, 400]
    assert item.center == [170, 400]


def test_invalid_confidence_out_of_bounds():
    payload = {
        "track_id": 1,
        "class_id": 0,
        "class_name": "person",
        "confidence": 1.5,  # Invalid: > 1.0
        "bbox": [10, 10, 50, 50],
        "center": [30, 50]
    }
    with pytest.raises(ValidationError):
        DetectionItem(**payload)


def test_invalid_bbox_length():
    payload = {
        "track_id": 1,
        "class_id": 2,
        "class_name": "car",
        "confidence": 0.85,
        "bbox": [10, 10, 50],  # Invalid: 3 elements instead of 4
        "center": [30, 50]
    }
    with pytest.raises(ValidationError):
        DetectionItem(**payload)


def test_invalid_class_id_range():
    payload = {
        "track_id": 1,
        "class_id": 10,  # Invalid: exceeds 5
        "class_name": "airplane",
        "confidence": 0.85,
        "bbox": [10, 10, 50, 50],
        "center": [30, 50]
    }
    with pytest.raises(ValidationError):
        DetectionItem(**payload)
