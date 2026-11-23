# Sample Data & Test Fixtures
# AI-Based Smart Gate Monitoring System

This directory holds lightweight sample fixtures and metadata used for testing the detection, tracking, and counting engine.

---

## 1. Directory Usage
- Keep large CCTV video files out of this folder (excluded via `.gitignore`).
- Store small synthetic test clips, frame arrays, or bounding box annotations here for automated test runners.

---

## 2. Generating Synthetic Test Video
You can generate a test video using OpenCV:
```python
import cv2
import numpy as np

out = cv2.VideoWriter("sample_gate.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 30, (1280, 720))
for i in range(120):
    frame = np.full((720, 1280, 3), 40, dtype=np.uint8)
    cv2.circle(frame, (640, int(i * 6)), 20, (0, 255, 0), -1)
    out.write(frame)
out.release()
```
