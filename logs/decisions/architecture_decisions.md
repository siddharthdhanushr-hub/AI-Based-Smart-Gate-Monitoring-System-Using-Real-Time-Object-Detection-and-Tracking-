# Architecture Decision Records (ADRs)
# AI-Based Smart Gate Monitoring System

---

## ADR-001: Decoupled Multi-Layer Architecture
- **Date**: 2026-11-22
- **Status**: Accepted
- **Context**: The system integrates real-time video capture, deep learning inference, object tracking, event counting, database storage, and a live web dashboard. Coupling CV code directly with web endpoints would impair maintainability and prevent parallel development across the 3 teammates.
- **Decision**: Decouple the system into 4 distinct layers:
  1. Capture & Video Service Layer.
  2. Detection & Tracking Layer (YOLOv8 + DeepSORT).
  3. Directional Gate Counting & Event Processing Layer.
  4. Web Application Layer (FastAPI REST + WebSocket).
- **Consequences**: Enables Chandrashekar (CV) and Amith (Frontend) to develop against strict typed contracts without touching each other's codebases.

---

## ADR-002: Vector Cross-Product Geometry for Virtual Gate Line Crossing
- **Date**: 2026-11-22
- **Status**: Accepted
- **Context**: Detecting whether an object entered or exited a gate is prone to errors if based on bounding box overlap or simple 1D coordinate checks ($y > y_{\text{line}}$), especially when the gate line is angled or objects move diagonally.
- **Decision**: Represent the virtual gate line as a directed 2D line segment $\vec{L} = P_2 - P_1$. When an object's bottom-center trajectory segment intersects $\vec{L}$, compute the signed cross-product determinant:
  $$d = (x_2 - x_1)(y_b - y_1) - (y_2 - y_1)(x_b - x_1)$$
  A transition from negative to positive classifies as **ENTRY**, and positive to negative classifies as **EXIT**.
- **Consequences**: Mathematically robust across any arbitrary 2D line orientation and angle.

---

## ADR-003: Idempotent Debounce State Machine for Duplicate Prevention
- **Date**: 2026-11-22
- **Status**: Accepted
- **Context**: People and vehicles pausing or jittering near the virtual gate line can trigger dozens of false crossings within a few frames.
- **Decision**: Implement a track-level debounce state machine:
  1. Once a track crosses the line, lock further crossings for that track ID for `debounce_seconds` (default: 3.0s).
  2. Enforce a minimum Euclidean displacement (`min_distance_px` = 15px) before allowing subsequent crossings.
  3. Prune tracks that disappear for more than `max_age_frames` (30 frames).
- **Consequences**: Completely eliminates double-counting while preserving tracking continuity across brief occlusions.

---

## ADR-004: Recording-Level Dataset Partitioning
- **Date**: 2026-11-22
- **Status**: Accepted
- **Context**: Splitting consecutive CCTV video frames randomly into train, validation, and test sets causes extreme data leakage because frame $N$ and frame $N+1$ share identical background, lighting, and object positions.
- **Decision**: Enforce dataset splitting strictly at the **whole recording session / video file level**. Entire videos are assigned to either Train, Val, or Test, guaranteeing zero visual leakage.
- **Consequences**: Produces scientifically honest, generalizable evaluation metrics on held-out test data.

---

## ADR-005: Unified Model Loading Gateway (`ModelLoader`)
- **Date**: 2026-11-22
- **Status**: Accepted
- **Context**: The team lead must benchmark both baseline `yolov8n.pt` (Experiment A) and custom-trained gate weights (Experiment B). The downstream backend and CV pipeline should not require code modifications when swapping weights.
- **Decision**: Build `ModelLoader.load_model(model_path, ...)` which encapsulates model weights, hardware device selection (`cuda` vs `cpu`), and target class filtering.
- **Consequences**: Clean runtime substitution via environment variable `GATE_MODEL_PATH`.

---

## ADR-006: Asynchronous WebSocket Telemetry and MJPEG Video Ingestion
- **Date**: 2026-11-22
- **Status**: Accepted
- **Context**: The React dashboard requires continuous real-time video and immediate metric updates when crossings occur.
- **Decision**: Provide live video through a standard HTTP multipart MJPEG stream (`/api/video/stream`) and telemetry via an ASGI WebSocket channel (`/ws/monitoring`).
- **Consequences**: Zero third-party streaming server dependencies; standard browser HTML5 `<img>` tag and WebSocket API natively supported.


---

## ADR-007: DeepSORT Multi-Object Tracking with 8D Kalman Kinematics
- **Date**: 2026-11-27
- **Status**: Accepted
- **Context**: Basic centroid Euclidean distance tracking experiences track ID swaps and loss during rapid vehicle acceleration, pedestrian crossing clusters, or temporary visual occlusions (such as a vehicle passing behind a campus gate pillar).
- **Decision**: Implement DeepSORT multi-object tracking utilizing an 8-dimensional Kalman filter kinematic model $[c_x, c_y, a, h, v_x, v_y, v_a, v_h]^T$ with:
  1. Constant velocity motion prediction and measurement covariance projection.
  2. Bipartite data association via Hungarian / linear sum assignment with IoU cost and class consistency penalties.
  3. Formal track state machine (`Tentative` -> `Confirmed` -> `Deleted`).
  4. Track persistence across occlusions for up to `max_age` (30) missing frames.
  5. Strict schema conformance emitting ground-contact base coordinates $c = [(x_1 + x_2)//2, y_2]$.
- **Consequences**: Eliminates track identity fragmentation; allows robust gate line crossing calculations even during temporary frame dropouts or object occlusions.

---

## ADR-008: Hardware Privacy Shutter Detection and Multi-Source Ingestion
- **Date**: 2026-11-27
- **Status**: Accepted
- **Context**: In laptop and desktop environments, physical privacy shutters or OS permission restrictions cause camera capture drivers to emit black frames with hardware lock icons. This causes confusion if users cannot distinguish between system errors and physical shutter closures.
- **Decision**:
  1. Provide dynamic source switching across Physical Webcam (`0`), Campus Gate CCTV Video (`ai/dataset/sample_gate.mp4`), and Synthetic Simulation (`simulation`) directly accessible through REST (`POST /api/camera/source`) and the React dashboard.
  2. Implement automated dark-frame detection ($E[\text{pixel}] < 5.0$) in `CameraService` when reading from physical webcams, rendering an informative on-screen warning banner advising the user to uncover the camera or select the recorded gate video.
- **Consequences**: Eliminates black-screen confusion; permits seamless testing and demonstration on any workstation regardless of camera hardware availability.
