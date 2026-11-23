"""
Unit tests for ModelLoader and common model loading interface.
"""

import pytest
from backend.app.detection.model_loader import ModelLoader
from ai.src.inference import ModelLoader as AIModelLoader, GateObjectDetector


def test_resolve_device():
    # When explicit device provided
    assert AIModelLoader.resolve_device("cpu") == "cpu"
    assert AIModelLoader.resolve_device("cuda:0") == "cuda:0"


def test_model_loader_fallback_handling():
    # Loading non-existent weights returns a safe detector instance with fallback
    detector = AIModelLoader.load_model(
        model_path="non_existent_weights_path.pt",
        confidence=0.5,
        iou=0.45,
        device="cpu"
    )
    assert isinstance(detector, GateObjectDetector)
    assert detector.conf == 0.5
    assert detector.iou == 0.45
    assert detector.device == "cpu"


def test_backend_model_loader_defaults():
    detector = ModelLoader.get_detector()
    assert isinstance(detector, GateObjectDetector)
    assert detector.conf >= 0.0
    assert detector.iou >= 0.0
