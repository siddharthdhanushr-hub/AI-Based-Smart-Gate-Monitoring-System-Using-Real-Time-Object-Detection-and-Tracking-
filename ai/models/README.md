# Model Weights Storage & Distribution Guide
# AI-Based Smart Gate Monitoring System

## 1. Storage Policy
Model checkpoint binaries (`*.pt`, `*.onnx`, `*.engine`) exceed standard Git repository thresholds and are therefore excluded by `.gitignore`.

This directory houses lightweight metadata, download scripts, and model cards.

---

## 2. Models Catalog

| Model Identifier | Base Architecture | Training Dataset | Weight File | Location / Link |
|---|---|---|---|---|
| **`baseline-yolov8n`** | YOLOv8n (Nano) | MS COCO (Pretrained) | `yolov8n.pt` | Ultralytics CDN (auto-downloads on first load) |
| **`custom-gate-yolov8n-v1`** | YOLOv8n (Fine-tuned) | Campus Gate Dataset v1 | `best.pt` | Google Drive / Model Hub |

---

## 3. How to Obtain the Fine-Tuned Weights

Once custom Colab training is completed in `ai/notebooks/03_custom_training.ipynb`:
1. Download `best.pt` from Google Drive or Colab `runs/detect/train/weights/best.pt`.
2. Place the file at `ai/models/gate_yolov8n.pt`.
3. Set the backend configuration parameter:
   ```bash
   export GATE_MODEL_PATH="ai/models/gate_yolov8n.pt"
   ```
4. The system will automatically load the custom weights via `ModelLoader`.
