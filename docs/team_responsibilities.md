# Team Responsibilities & Ownership Matrix
# AI-Based Smart Gate Monitoring System

## 1. Project Organization

```text
Siddharth Dhanush R (Team Lead)
├── Overall Architecture & Integration Authority
├── AI Training & Evaluation (Google Colab)
├── FastAPI Backend & SQLite Database
└── Gate Line Vector Counting Engine
      │
      ├── Siddharth Chandrashekar (Computer Vision Engineer)
      │     └── OpenCV, YOLOv8 Integration, DeepSORT Tracking, Tracking IDs
      │
      └── Amith Gowda R (Frontend Engineer)
            └── React, Tailwind CSS, Live Stream Canvas, Dashboard Analytics
```

---

## 2. Detailed Member Scope

### 2.1. Siddharth Dhanush R (Team Lead & Backend)
- **Branch**: `feature/dhanush-ai-backend`
- **Ownership**:
  - Global project coordination, system architecture, and repository health.
  - Review and approval authority on all Pull Requests targeting `main`.
  - Development of Google Colab notebooks (`01_pretrained_baseline.ipynb` through `04_model_evaluation.ipynb`).
  - Dataset preparation pipeline (frame extraction, split isolation, YOLO format validation).
  - Common model loading interface (`ModelLoader`).
  - FastAPI application structure, configuration, and middleware.
  - Vector-based virtual gate crossing algorithm and duplicate debounce state machine.
  - SQLite database schemas, migrations, and SQLAlchemy repository layer.
  - REST API routes and ASGI WebSocket hub.
  - End-to-end integration and release packaging.

### 2.2. Siddharth Chandrashekar (Computer Vision Engineer)
- **Branch**: `feature/chandrashekar-computer-vision`
- **Ownership**:
  - Camera capture abstraction (OpenCV `cv2.VideoCapture`).
  - Integration of YOLOv8 object detector into the frame loop.
  - Integration of DeepSORT (or ByteTrack) multi-object tracking.
  - Generation and maintenance of persistent track IDs.
  - Formatting tracking outputs according to the agreed contract.
  - Drawing visual overlays (boxes, IDs, confidence, gate line) on video frames.
  - Unit tests for tracking persistence and occlusion handling.

### 2.3. Amith Gowda R (Frontend Engineer)
- **Branch**: `feature/amith-dashboard`
- **Ownership**:
  - Modern, responsive React dashboard built with Vite and Tailwind CSS.
  - Real-time video player consuming the `/api/video/stream` MJPEG feed.
  - Live KPI cards: Total entries, exits, active people, and active vehicles.
  - Interactive activity log table with search and filtering capabilities.
  - Hourly and daily trend charts (Chart.js / Recharts).
  - System alerts drawer / notifications.
  - WebSocket client consuming `/ws/monitoring`.

---

## 3. Collaboration Protocol & Code Review Checklist

1. **Before pushing**:
   - Run local unit tests and ensure all pass.
   - Run `git status` and verify that no credentials, large weights, or raw videos are staged.
   - Update individual work log (`logs/team/<name>.md`).
2. **Pull Request Submission**:
   - Open PR with base `main` and head `feature/<name>-<module>`.
   - Provide summary, files changed, and test execution evidence.
   - Tag **Siddharth Dhanush R** for review.
3. **Review & Merge Policy**:
   - No direct commits to `main`.
   - Only Siddharth Dhanush R has merge rights.
   - Approvals require verified passing tests and documentation alignment.
