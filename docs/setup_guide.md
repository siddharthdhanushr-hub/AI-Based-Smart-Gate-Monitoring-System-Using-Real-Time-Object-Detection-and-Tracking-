# Developer & System Setup Guide
# AI-Based Smart Gate Monitoring System

This document outlines instructions for setting up the local development environment, configuring Python runtimes, running tests, and executing Google Colab experiments.

---

## 1. Prerequisites
- **Operating System**: Windows 10/11, macOS, or Ubuntu 20.04+
- **Python**: Version 3.10, 3.11, or 3.12 (64-bit)
- **Git**: Installed and configured with your GitHub credentials
- **Hardware**:
  - Development / Backend: Multi-core CPU, 8GB+ RAM, standard webcam or sample video files.
  - Deep Learning Training: Google Colab environment with GPU accelerator (NVIDIA T4 or higher).

---

## 2. Local Repository Setup

```bash
# 1. Clone the repository
git clone https://github.com/siddharthdhanushr-hub/AI-Based-Smart-Gate-Monitoring-System-Using-Real-Time-Object-Detection-and-Tracking-.git
cd AI-Based-Smart-Gate-Monitoring-System-Using-Real-Time-Object-Detection-and-Tracking-

# 2. Checkout your assigned development branch
# For Dhanush:
git checkout feature/dhanush-ai-backend
# For Chandrashekar:
git checkout feature/chandrashekar-computer-vision
# For Amith:
git checkout feature/amith-dashboard

# 3. Create virtual environment
python -m venv .venv

# 4. Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (cmd):
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt
```

---

## 3. Running the FastAPI Backend

```bash
# Start backend on localhost:8000 with auto-reload
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Interactive OpenAPI Swagger docs: `http://localhost:8000/docs`
- Redoc documentation: `http://localhost:8000/redoc`
- Video Stream test: `http://localhost:8000/api/video/stream`

---

## 4. Google Colab Training Workflow

Colab notebooks reside in `ai/notebooks/`:
- `01_pretrained_baseline.ipynb`: Benchmark YOLOv8n baseline on sample gate images.
- `02_dataset_preparation.ipynb`: Extract frames, format YOLO labels, generate non-leaking splits.
- `03_custom_training.ipynb`: Train YOLOv8n on GPU with gate dataset.
- `04_model_evaluation.ipynb`: Direct comparison between baseline and custom model.

### Steps to Run on Colab:
1. Open Google Colab (`https://colab.research.google.com`).
2. Upload the desired notebook from `ai/notebooks/`.
3. In Colab, select **Runtime** $\rightarrow$ **Change runtime type** $\rightarrow$ Hardware accelerator: **GPU** (T4).
4. Run cells sequentially.
5. Export results and download checkpoint weights (`best.pt`) to Google Drive.
6. Commit notebook outputs and lightweight metrics back to your feature branch.
