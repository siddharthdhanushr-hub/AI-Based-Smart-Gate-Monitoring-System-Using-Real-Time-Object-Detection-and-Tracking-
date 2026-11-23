# AI-Based Smart Gate Monitoring System Using Real-Time Object Detection and Tracking

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00599C.svg)](https://docs.ultralytics.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent edge/server surveillance solution engineered for campus, parking, and facility gate monitoring. The system integrates real-time object detection (YOLOv8) and multi-object tracking (DeepSORT) with a vector-based virtual gate crossing engine to provide real-time entry/exit counts, vehicle/pedestrian classification, SQLite event logging, and WebSocket live telemetry streaming to a modern dashboard.

---

## 1. System Architecture Overview

```mermaid
flowchart TD
    subgraph Capture["1. Video Capture Layer"]
        A1[Live Webcam / USB Camera] --> C[Camera Service]
        A2[Recorded CCTV / Video Files] --> C
    end

    subgraph Inference["2. Detection & Tracking Pipeline"]
        C -->|Frames| D[YOLOv8 Detector<br/>Baseline / Custom Weights]
        D -->|Detections [x1, y1, x2, y2, conf, cls]| T[DeepSORT / ByteTrack Tracker]
        T -->|Track IDs + Centroid Trajectory| G[Gate Line Crossing Engine]
    end

    subgraph Counting["3. Analytics & Persistence"]
        G -->|Cross Product Vector Direction| E[Event Processor]
        E -->|Entry / Exit Events| DB[(SQLite Database<br/>SQLAlchemy ORM)]
        E -->|Rolling Counts & Alerts| S[In-Memory Cache / Stats]
    end

    subgraph Backend["4. FastAPI Services"]
        DB --> API[FastAPI REST APIs]
        S --> API
        S --> WS[WebSocket Manager]
        C -->|Annotated MJPEG Feed| VStream[Video Streaming Endpoint]
    end

    subgraph Frontend["5. User Interface"]
        API --> UI[React + Tailwind Dashboard]
        WS --> UI
        VStream --> UI
    end
```

---

## 2. Key Features

- **Multi-Source Video Ingestion**: Supports live USB/webcam feeds and recorded MP4/AVI surveillance footage with dynamic source switching.
- **YOLOv8 Detection**: Optimized detection of 6 key gate classes: `person`, `bicycle`, `car`, `motorcycle`, `bus`, and `truck`.
- **Trajectory-Based Virtual Gate Crossing**: Directional entry/exit counting using signed 2D vector cross-product geometry with debouncing and track-history state tracking to eliminate double-counts and handle brief occlusion.
- **Unified Model Interface**: Allows seamless runtime swapping between the baseline `yolov8n.pt` and custom fine-tuned gate models without architectural changes.
- **FastAPI REST + WebSocket Backend**: High-performance asynchronous backend providing real-time stats, paginated event histories, hourly/daily traffic analytics, and an MJPEG video stream.
- **Reproducible Google Colab Training**: Fully reproducible notebooks for baseline benchmarking, gate dataset extraction and annotation validation, custom YOLOv8 fine-tuning, and side-by-side metric evaluation.

---

## 3. Team Responsibilities & Ownership

| Name | Role | Development Branch | Scope |
|---|---|---|---|
| **Siddharth Dhanush R** | **Team Lead, AI Training, Backend & Integration** | `feature/dhanush-ai-backend` | Colab training, dataset pipeline, model comparison, FastAPI backend, gate line engine, SQLite persistence, WebSocket, review & merge authority. |
| **Siddharth Chandrashekar** | **Computer Vision Engineer** | `feature/chandrashekar-computer-vision` | OpenCV frame capture, YOLO detection integration, DeepSORT tracking, persistent track IDs, annotated video rendering. |
| **Amith Gowda R** | **Frontend Engineer** | `feature/amith-dashboard` | React dashboard, Tailwind styling, live video canvas, KPI metric cards, hourly charts, activity logs, alert notifications. |

---

## 4. Repository Structure

```text
.
├── AGENTS.md                          # Team coordination rules, contracts, and git standards
├── README.md                          # Project documentation and getting started guide
├── requirements.txt                   # Complete project dependencies
│
├── docs/                              # Detailed engineering documentation
│   ├── project_architecture.md        # Deep dive into system components and data flow
│   ├── api_contract.md                # REST API and WebSocket message specifications
│   ├── setup_guide.md                 # Local installation and environment configuration
│   ├── integration_guide.md           # Instructions for connecting CV and UI modules
│   ├── testing_strategy.md            # Unit and integration testing protocols
│   └── team_responsibilities.md       # Ownership matrix and code review guidelines
│
├── backend/                           # FastAPI Backend Application
│   ├── requirements.txt
│   └── app/
│       ├── main.py                    # Application entrypoint & ASGI router
│       ├── core/config.py             # Application settings & environment config
│       ├── api/                       # API route definitions
│       │   ├── camera.py              # Start, stop, and switch camera feeds
│       │   ├── monitoring.py          # Real-time stats and event queries
│       │   ├── analytics.py           # Hourly and daily aggregated traffic trends
│       │   ├── alerts.py              # Security alerts and anomaly logs
│       │   ├── video.py               # MJPEG live video streaming route
│       │   └── websocket.py           # WebSocket endpoint (/ws/monitoring)
│       ├── detection/                 # Detector wrappers & common model loader
│       ├── counting/                  # Virtual gate line vector geometry & counter
│       ├── services/                  # Camera service, Event processor, WS connection manager
│       ├── database/                  # SQLAlchemy models, session, and CRUD repository
│       └── schemas/                   # Pydantic schemas (detection, event, stats, alert)
│
├── frontend/                          # React + Tailwind Dashboard (Amith Gowda R)
│   └── src/
│
├── ai/                                # AI Training & Experimentation Pipeline
│   ├── notebooks/
│   │   ├── 01_pretrained_baseline.ipynb   # Experiment A: YOLOv8n baseline benchmark
│   │   ├── 02_dataset_preparation.ipynb   # Frame sampling, annotation, split, data.yaml
│   │   ├── 03_custom_training.ipynb       # Experiment B: Custom fine-tuning on Colab GPU
│   │   └── 04_model_evaluation.ipynb      # Comparative evaluation (mAP, FPS, Confusion Matrix)
│   ├── dataset/data.yaml              # YOLO dataset configuration
│   ├── src/inference.py               # Shared inference utilities
│   ├── models/                        # Model storage instructions & checkpoints
│   ├── evaluation/results.csv         # Experiment metric comparison table
│   └── experiments/experiment_log.md  # Training history and parameter records
│
├── tests/                             # Automated Test Suite
│   ├── unit/                          # Isolated unit tests for detection, counting, DB, API
│   └── integration/                   # Pipeline and end-to-end integration tests
│
└── logs/                              # Audit & Developer Session Logs
    ├── team/                          # Individual member activity logs
    │   ├── dhanush.md
    │   ├── chandrashekar.md
    │   └── amith.md
    └── decisions/                     # Architecture Decision Records (ADRs)
        └── architecture_decisions.md
```

---

## 5. Quick Start Guide

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git
- Web browser (Chrome, Firefox, Edge)

### Backend Local Setup
```bash
# Clone repository and switch to development branch
git checkout feature/dhanush-ai-backend

# Create virtual environment using uv or python venv
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend application
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive API documentation is available at `http://localhost:8000/docs`.

### Running Unit and Integration Tests
```bash
pytest tests/ -v
```

---

## 6. AI Experimentation Workflow (Google Colab)

1. Open `ai/notebooks/01_pretrained_baseline.ipynb` in Google Colab to establish baseline inference speed and mAP on gate test samples.
2. Open `ai/notebooks/02_dataset_preparation.ipynb` to sample video frames at distinct intervals, validate YOLO label formats, and output non-overlapping train/val/test splits.
3. Open `ai/notebooks/03_custom_training.ipynb` with GPU accelerator enabled (T4 / V100) to fine-tune `yolov8n.pt` for 50 epochs.
4. Open `ai/notebooks/04_model_evaluation.ipynb` to run standardized comparative benchmarks between the baseline and fine-tuned model. Record findings in `ai/experiments/experiment_log.md` and `ai/evaluation/results.csv`.
