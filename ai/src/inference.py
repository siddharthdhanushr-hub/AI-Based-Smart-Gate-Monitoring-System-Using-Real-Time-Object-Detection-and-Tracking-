"""
Model inference and common loader interface for YOLOv8 gate detection.
Provides GateObjectDetector and ModelLoader ensuring compatibility across
pretrained baseline and custom fine-tuned weights.
"""

from typing import Dict, List, Any, Optional, Tuple
import os
import numpy as np

# Canonical gate classes mapping
GATE_CLASSES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    4: "bus",
    5: "truck"
}

# Mapping from COCO 80-class format to Gate 6-class format
COCO_TO_GATE_MAP = {
    0: (0, "person"),
    1: (1, "bicycle"),
    2: (2, "car"),
    3: (3, "motorcycle"),
    5: (4, "bus"),
    7: (5, "truck")
}


class ModelLoader:
    """Loads YOLOv8 models safely with device and path validation."""

    @staticmethod
    def resolve_device(preferred_device: Optional[str] = None) -> str:
        """Determines whether CUDA GPU is available or falls back to CPU."""
        if preferred_device:
            return preferred_device
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda:0"
        except ImportError:
            pass
        return "cpu"

    @classmethod
    def load_model(
        cls,
        model_path: str = "yolov8n.pt",
        confidence: float = 0.40,
        iou: float = 0.50,
        device: Optional[str] = None
    ) -> Any:
        """
        Loads Ultralytics YOLO model.
        Falls back to a MockDetector if Ultralytics or weights are unavailable in test environments.
        """
        selected_device = cls.resolve_device(device)
        try:
            from ultralytics import YOLO
            # If path is local and doesn't exist, check standard model folder
            if not os.path.exists(model_path) and not model_path.endswith(".pt"):
                fallback_path = os.path.join("ai", "models", f"{model_path}.pt")
                if os.path.exists(fallback_path):
                    model_path = fallback_path

            model = YOLO(model_path)
            return GateObjectDetector(
                yolo_model=model,
                confidence_threshold=confidence,
                iou_threshold=iou,
                device=selected_device,
                model_name=os.path.basename(model_path)
            )
        except Exception as e:
            # For environments without ultralytics installed or offline testing
            return GateObjectDetector(
                yolo_model=None,
                confidence_threshold=confidence,
                iou_threshold=iou,
                device="cpu",
                model_name=f"fallback-mock-{model_path}",
                fallback_reason=str(e)
            )


class GateObjectDetector:
    """Encapsulates object detection, class filtering, and contract compliance."""

    def __init__(
        self,
        yolo_model: Any,
        confidence_threshold: float = 0.40,
        iou_threshold: float = 0.50,
        device: str = "cpu",
        model_name: str = "yolov8n.pt",
        fallback_reason: Optional[str] = None
    ):
        self.model = yolo_model
        self.conf = confidence_threshold
        self.iou = iou_threshold
        self.device = device
        self.model_name = model_name
        self.fallback_reason = fallback_reason

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Performs object detection on a BGR numpy frame.
        Filters to the 6 target classes and returns structured detection objects.
        """
        if self.model is None or frame is None:
            return []

        h, w = frame.shape[:2]
        results = self.model.predict(
            source=frame,
            conf=self.conf,
            iou=self.iou,
            device=self.device,
            verbose=False
        )

        detections: List[Dict[str, Any]] = []
        if not results:
            return detections

        first_res = results[0]
        boxes = first_res.boxes

        if boxes is None or len(boxes) == 0:
            return detections

        for box in boxes:
            raw_cls = int(box.cls[0].item())
            conf_val = float(box.conf[0].item())
            xyxy = box.xyxy[0].tolist()

            # Normalize coordinates within frame boundaries
            x1 = max(0, min(w - 1, int(round(xyxy[0]))))
            y1 = max(0, min(h - 1, int(round(xyxy[1]))))
            x2 = max(0, min(w - 1, int(round(xyxy[2]))))
            y2 = max(0, min(h - 1, int(round(xyxy[3]))))

            # Resolve class mapping
            class_id: Optional[int] = None
            class_name: Optional[str] = None

            if raw_cls in COCO_TO_GATE_MAP:
                class_id, class_name = COCO_TO_GATE_MAP[raw_cls]
            elif raw_cls in GATE_CLASSES:
                class_id = raw_cls
                class_name = GATE_CLASSES[raw_cls]
            else:
                # Class outside target gate monitoring taxonomy
                continue

            # Centroid convention: (midpoint x, bottom-center y for floor plane)
            cx = (x1 + x2) // 2
            cy = y2

            detection_dict = {
                "track_id": -1,  # Raw detection before tracking association
                "class_id": class_id,
                "class_name": class_name,
                "confidence": round(conf_val, 4),
                "bbox": [x1, y1, x2, y2],
                "center": [cx, cy]
            }
            detections.append(detection_dict)

        return detections

    def annotate_frame(
        self,
        frame: np.ndarray,
        tracked_objects: List[Dict[str, Any]],
        gate_line: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None
    ) -> np.ndarray:
        """Renders bounding boxes, labels, centroids, and the virtual gate line on the frame."""
        import cv2

        annotated = frame.copy()

        # Draw gate line if provided
        if gate_line:
            p1, p2 = gate_line
            cv2.line(annotated, p1, p2, (0, 0, 255), 3)  # Red line
            cv2.circle(annotated, p1, 5, (0, 255, 255), -1)
            cv2.circle(annotated, p2, 5, (0, 255, 255), -1)
            cv2.putText(
                annotated, "GATE LINE",
                (p1[0] + 10, p1[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
            )

        # Draw detections / tracks
        for obj in tracked_objects:
            x1, y1, x2, y2 = obj["bbox"]
            track_id = obj.get("track_id", -1)
            class_name = obj.get("class_name", "obj")
            conf = obj.get("confidence", 0.0)
            cx, cy = obj.get("center", ((x1 + x2) // 2, y2))

            # Bounding box
            color = (0, 255, 0) if track_id != -1 else (255, 200, 0)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Centroid point
            cv2.circle(annotated, (cx, cy), 4, (0, 0, 255), -1)

            # Label text
            id_str = f"#{track_id} " if track_id != -1 else ""
            label = f"{id_str}{class_name} {conf:.2f}"
            t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            cv2.rectangle(annotated, (x1, y1 - 20), (x1 + t_size[0], y1), color, -1)
            cv2.putText(
                annotated, label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
            )

        return annotated
