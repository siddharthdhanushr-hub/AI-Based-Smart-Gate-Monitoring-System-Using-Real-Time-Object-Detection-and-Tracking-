# AI Model Training & Evaluation Pipeline
# AI-Based Smart Gate Monitoring System

This directory houses the dataset preparation pipelines, Google Colab training workflows, experiment tracking, and model evaluation modules for the Smart Gate Monitoring System.

---

## 1. Directory Structure

```text
ai/
├── README.md                      # Pipeline guide and instructions
├── notebooks/                     # Google Colab Jupyter Notebooks
│   ├── 01_pretrained_baseline.ipynb   # Experiment A: Baseline YOLOv8n evaluation
│   ├── 02_dataset_preparation.ipynb   # Frame sampling, split isolation, data.yaml
│   ├── 03_custom_training.ipynb       # Experiment B: GPU fine-tuning (50 epochs)
│   └── 04_model_evaluation.ipynb      # Comparative benchmarking & validation
├── dataset/                       # Dataset configuration and metadata
│   ├── data.yaml                  # YOLOv8 dataset configuration
│   └── README.md                  # Annotation protocol and class definitions
├── models/                        # Model storage instructions & checkpoints
│   └── README.md                  # Instructions for downloading weights
├── src/                           # Python inference & evaluation utilities
│   ├── __init__.py
│   ├── inference.py               # Unified ModelLoader and GateObjectDetector
│   ├── dataset_utils.py           # Frame sampling and label validation
│   └── eval_utils.py              # Metric calculation and plotting helpers
├── evaluation/                    # Comparison records
│   ├── results.csv                # Tabular comparison metrics
│   └── evaluation_report.md       # Comparative findings report
└── experiments/                   # Experiment audit trail
    └── experiment_log.md          # Chronological record of training runs
```

---

## 2. Target Classes & COCO Alignment

The model focuses on 6 essential gate monitoring classes:

| Class ID | Class Name | Description | COCO Equivalent ID |
|---|---|---|---|
| `0` | `person` | Pedestrian, security guard, student, faculty | `0` |
| `1` | `bicycle` | Bicycles and manual cycles | `1` |
| `2` | `car` | Sedans, hatchbacks, SUVs, taxis | `2` |
| `3` | `motorcycle` | Two-wheelers, scooters, motorbikes | `3` |
| `4` | `bus` | College buses, public transit, shuttles | `5` |
| `5` | `truck` | Delivery vans, heavy trucks, maintenance | `7` |

---

## 3. Google Colab Execution Workflow

1. Open **Google Colab** and mount your Google Drive if saving models directly.
2. Select runtime with GPU accelerator (`Runtime` $\rightarrow$ `Change runtime type` $\rightarrow$ `T4 GPU`).
3. Upload and execute `notebooks/01_pretrained_baseline.ipynb` to establish benchmark latency and metrics.
4. Execute `notebooks/02_dataset_preparation.ipynb` to process gate footage, generate non-leaking splits, and format YOLO labels.
5. Execute `notebooks/03_custom_training.ipynb` to run fine-tuning on the gate dataset.
6. Run `notebooks/04_model_evaluation.ipynb` on the held-out test split to generate side-by-side comparison tables and confusion matrices.
7. Record observed metrics in `evaluation/results.csv` and `experiments/experiment_log.md`.
