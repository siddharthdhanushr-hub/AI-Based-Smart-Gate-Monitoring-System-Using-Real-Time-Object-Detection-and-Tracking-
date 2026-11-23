# Dataset Preparation & Annotation Protocol
# AI-Based Smart Gate Monitoring System

This document describes the dataset collection, annotation guidelines, and non-overlapping split strategy for the gate monitoring environment.

---

## 1. Data Collection Sources & Privacy Rules

- **Source 1**: Authorized college gate CCTV recordings (fixed angle, covering ingress and egress gate lanes).
- **Source 2**: Open-access surveillance datasets adhering strictly to commercial/academic usage licenses.
- **Privacy Compliance**:
  - Footage is gathered exclusively under institution authorization for security/monitoring research.
  - Raw uncurated video footage containing identifiable individuals or license plates is excluded from public git commits via `.gitignore`.
  - Processed frames are downscaled and used strictly for object detection training.

---

## 2. Frame Sampling & Temporal Leakage Prevention

> **CRITICAL RULE**: Do not split neighboring or consecutive frames from the same video file across train and test sets!

Consecutive CCTV video frames (e.g., frame 100 and frame 101) have nearly identical backgrounds and object positions. If frame 100 is placed in the training set and frame 101 in the test set, the evaluation will exhibit extreme data leakage, resulting in falsely inflated accuracy metrics.

### Correct Splitting Strategy:
- Split datasets by **independent recording sessions or whole video files**:
  - `Video_01.mp4`, `Video_02.mp4`, `Video_03.mp4` $\rightarrow$ **Training Set** (~70%)
  - `Video_04.mp4` $\rightarrow$ **Validation Set** (~15%)
  - `Video_05.mp4` $\rightarrow$ **Held-out Test Set** (~15%)
- Sample frames at a fixed stride (e.g., every 30 frames / 1 frame per second) to reduce sample redundancy.

---

## 3. Annotation Specifications

- **Format**: YOLO Darknet format (`.txt` per `.jpg` image).
- Each text line contains: `<class_id> <x_center> <y_center> <width> <height>` (all values normalized between `0.0` and `1.0`).
- **Target Classes**:
  - `0`: `person`
  - `1`: `bicycle`
  - `2`: `car`
  - `3`: `motorcycle`
  - `4`: `bus`
  - `5`: `truck`

---

## 4. Current Status & Blocker Record

- **Status**: Pipeline and validation scripts established.
- **Gate Footage Availability**: Awaiting final handover of high-definition authorized college gate CCTV recordings.
- **Immediate Action**: Experiment A (Pretrained Baseline) is benchmarked using authorized sample clips to establish baseline performance metrics while gate footage annotation proceeds.
