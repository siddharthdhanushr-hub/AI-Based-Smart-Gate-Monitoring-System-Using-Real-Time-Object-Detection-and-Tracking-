# AI Model Experiment Log
# AI-Based Smart Gate Monitoring System

This document provides a strict audit trail of all AI training, benchmarking, and fine-tuning experiments conducted for the Smart Gate Monitoring System.

---

## Experiment Registry

### Experiment A: Pretrained YOLOv8n Baseline Evaluation
- **Experiment ID**: `EXP-001-BASELINE`
- **Date**: `2026-11-22`
- **Objective**: Establish baseline detection precision, recall, mAP, and inference latency using pretrained `yolov8n.pt` weights on campus gate footage.
- **Model Architecture**: Ultralytics YOLOv8n (Nano, 3.2M parameters)
- **Starting Weights**: `yolov8n.pt` (COCO pretrained)
- **Notebook**: `ai/notebooks/01_pretrained_baseline.ipynb`
- **Target Classes**: `person (0)`, `bicycle (1)`, `car (2)`, `motorcycle (3)`, `bus (5)`, `truck (7)`
- **Execution Environment**: Google Colab (Python 3.10+, PyTorch 2.x, T4 GPU)
- **Status**: Pipeline prepared; awaiting Colab execution by team lead.
- **Actual Parameters**:
  - Image size: `640`
  - Confidence threshold: `0.35`
  - IoU threshold: `0.50`
- **Observations & Findings**:
  - *Pending execution of `01_pretrained_baseline.ipynb` on Google Colab.*

---

### Experiment B: Custom YOLOv8n Fine-Tuning on Gate Dataset
- **Experiment ID**: `EXP-002-FINETUNE`
- **Date**: `2026-11-22` (Configured)
- **Objective**: Fine-tune YOLOv8n on annotated campus gate images to improve detection under occlusion, glare, and angled camera perspectives.
- **Model Architecture**: Ultralytics YOLOv8n
- **Starting Weights**: `yolov8n.pt`
- **Dataset**: `ai/dataset/data.yaml` (6 classes, non-overlapping recording splits)
- **Notebook**: `ai/notebooks/03_custom_training.ipynb`
- **Target Hyperparameters**:
  - `epochs`: 50
  - `imgsz`: 640
  - `batch`: 16 (auto-fallback to 8 if VRAM < 12GB)
  - `optimizer`: Auto (SGD / AdamW)
  - `lr0`: 0.01
  - `patience`: 10
  - `save`: True
- **Execution Environment**: Google Colab with GPU
- **Status**: Pipeline & notebook prepared; awaiting full annotation and Colab training run.
- **Checkpoints**: `best.pt` target location $\rightarrow$ `ai/models/gate_yolov8n.pt`
- **Observations & Findings**:
  - *Pending execution of `03_custom_training.ipynb`.*
