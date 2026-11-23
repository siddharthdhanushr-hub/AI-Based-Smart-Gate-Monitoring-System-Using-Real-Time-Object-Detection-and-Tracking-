"""
Model loader interface for backend detection service.
Wraps ai.src.inference.ModelLoader with application settings integration.
"""

from typing import Optional, Any
import os
from backend.app.core.config import settings
from ai.src.inference import ModelLoader as AIModelLoader, GateObjectDetector


class ModelLoader:
    """Provides a consistent model loading gateway for the backend."""

    @classmethod
    def get_detector(
        cls,
        model_path: Optional[str] = None,
        confidence: Optional[float] = None,
        iou: Optional[float] = None,
        device: Optional[str] = None
    ) -> GateObjectDetector:
        """
        Loads the detector using configured defaults or explicit overrides.
        """
        path = model_path or settings.MODEL_PATH
        conf = confidence if confidence is not None else settings.CONFIDENCE_THRESHOLD
        iou_val = iou if iou is not None else settings.IOU_THRESHOLD
        dev = device or settings.INFERENCE_DEVICE

        return AIModelLoader.load_model(
            model_path=path,
            confidence=conf,
            iou=iou_val,
            device=dev
        )
