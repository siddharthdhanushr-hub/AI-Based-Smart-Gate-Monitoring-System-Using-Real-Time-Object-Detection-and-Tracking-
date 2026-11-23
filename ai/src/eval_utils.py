"""
Evaluation, metrics computation, and benchmarking utilities for YOLOv8 models.
"""

from typing import Dict, List, Tuple, Any, Optional
import time
import numpy as np


def compute_iou(boxA: List[float], boxB: List[float]) -> float:
    """
    Computes Intersection over Union (IoU) between two boxes [x1, y1, x2, y2].
    """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_w = max(0.0, xB - xA)
    inter_h = max(0.0, yB - yA)
    inter_area = inter_w * inter_h

    boxA_area = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxB_area = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    union_area = boxA_area + boxB_area - inter_area

    if union_area <= 0:
        return 0.0

    return inter_area / union_area


def compute_ap(recalls: np.ndarray, precisions: np.ndarray) -> float:
    """
    Computes Average Precision (AP) using standard 11-point or trapezoidal interpolation.
    """
    mrec = np.concatenate(([0.0], recalls, [1.0]))
    mpre = np.concatenate(([0.0], precisions, [0.0]))

    for i in range(len(mpre) - 2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i + 1])

    i = np.where(mrec[1:] != mrec[:-1])[0]
    ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return float(ap)


def benchmark_inference_speed(
    detector: Any,
    test_images: List[np.ndarray],
    warmup: int = 5,
    runs: int = 30
) -> Dict[str, float]:
    """
    Benchmarks model inference speed across warmup and measurement runs.
    Returns latency (ms/frame) and throughput (FPS).
    """
    if not test_images:
        return {"latency_ms": 0.0, "fps": 0.0}

    n_images = len(test_images)

    # Warmup
    for i in range(warmup):
        frame = test_images[i % n_images]
        _ = detector.detect(frame)

    latencies: List[float] = []
    for i in range(runs):
        frame = test_images[i % n_images]
        t0 = time.perf_counter()
        _ = detector.detect(frame)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000.0)

    mean_ms = float(np.mean(latencies))
    fps = 1000.0 / mean_ms if mean_ms > 0 else 0.0

    return {
        "latency_ms": round(mean_ms, 2),
        "fps": round(fps, 1),
        "min_ms": round(float(np.min(latencies)), 2),
        "max_ms": round(float(np.max(latencies)), 2)
    }
