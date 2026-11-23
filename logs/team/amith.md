# Developer Work Log: Amith Gowda R
# Role: Frontend & Dashboard Engineer
# Branch: feature/amith-dashboard

---

## Log Template & Guidelines
*Maintain this log after each meaningful development session. Use ISO dates (`YYYY-MM-DD`). Never record fabricated test results or metrics.*

---

## Date: 2026-11-22

### Work completed
- Repository coordination template initialized by Team Lead (Siddharth Dhanush R).
- Received backend REST API and WebSocket specifications (`docs/api_contract.md`).
- Reviewed dashboard component requirements in `frontend/src/README.md`.

### Files created/modified
- `logs/team/amith.md`
- `frontend/src/README.md`

### Technical decisions
- Decided to structure dashboard with React (Vite) and Tailwind CSS.
- Video feed will consume standard `/api/video/stream` MJPEG route.
- Live telemetry and crossing events will subscribe to WebSocket `/ws/monitoring`.

### Tests performed
- Verified API schema compatibility against backend specifications.

### Results
- Endpoints and contracts documented and ready for consumption.

### Issues encountered
- None at setup.

### Pending tasks
- Initialize branch `feature/amith-dashboard`.
- Initialize React + Vite project in `frontend/`.
- Build Overview Dashboard, Live Stream player, and Analytics charts.
- Connect WebSocket and test live counter updates.
- Submit Pull Request targeting `main` for review by Siddharth Dhanush R.

### Git
- Branch: `feature/amith-dashboard`
- Commit SHA: TBD
- Pull request: TBD

---

## Date: 2026-11-23

### Work completed
- Initialized the React/Vite dashboard in the repository's `frontend/` directory.
- Integrated the REST endpoints and response fields from `docs/api_contract.md` for monitoring stats, paginated events, daily/hourly analytics, and alerts.
- Added contract-backed WebSocket handling for `STATS_UPDATE`, `GATE_CROSSING`, and `SYSTEM_ALERT`, including reconnect backoff and duplicate event protection.
- Connected the backend MJPEG stream and backend-confirmed camera start/stop controls.
- Added activity pagination/loading, report CSV export, real analytics ranges, and production alert filters that do not imply unsupported read actions.
- Preserved clearly marked demo mode and documented the backend's lack of per-frame detection totals.
- Removed UI claims that the camera stream is annotated; the stream currently displays overlays only if supplied by the backend.
- Fixed the mobile live-camera panel's minimum height so its 16:9 layout does not cause horizontal overflow.
- Added frontend tests for REST error handling, API normalization, and WebSocket reconnection.
- Connected the inference loop's annotated frames to a separate camera buffer used by the MJPEG stream, preserving raw frames for detection input.
- Updated `/api/monitoring/stats` to report the monitoring processor's real running state instead of a constant `true`.
- Installed the repository-listed CPU inference runtime in the ignored `.venv` and loaded the default YOLO weights for physical-camera validation.

### Files created/modified
- `frontend/`
- `backend/app/api/monitoring.py`
- `backend/app/database/crud.py`
- `backend/app/services/camera_service.py`
- `backend/app/services/event_processor.py`
- `docs/api_contract.md`
- `tests/integration/test_monitoring_pipeline.py`
- `tests/unit/test_api_endpoints.py`
- `tests/unit/test_camera_service.py`
- `logs/team/amith.md`

### Tests performed
- `npm test`: 8 passed.
- `npm run lint`: passed.
- `npm run build`: passed; Vite reports a bundle-size advisory for the chart-heavy entry chunk.
- Full backend suite `pytest tests/ -q`: 31 passed (using an in-memory SQLite URL).
- Live-mode browser smoke test: REST endpoints loaded, WebSocket connected, Today/30-day analytics selections worked, camera start/stop worked, and the MJPEG image loaded at 640x480.
- Physical-camera inference: no synthetic fallback; YOLO detected a person and the tracker retained track ID 1 across three frames. The annotated MJPEG stream decoded at 640x480.
- Live API smoke test: REST start returned active, stats reported `is_active: true`, WebSocket broadcast `STATS_UPDATE`, MJPEG decoded at 640x480, and stop returned inactive status.
- Backend tests verify that stats status follows the processor state, annotated frames are published, and MJPEG prefers annotated frames while retaining raw-frame fallback.
- Responsive check: all routes had no horizontal overflow at 320px and 390px; live monitoring also passed at 768px and 1440px. Mobile navigation and camera fullscreen were verified.

### Results
- Frontend REST/WebSocket adapters follow the documented contract. Production endpoints are configurable through `.env.local`; demo mode remains the default.
- Responsive mobile navigation, dashboard rendering, disconnected camera state, demo alert actions, and live backend connection were smoke-tested in the browser.

### Issues encountered
- The shared browser tab could not be refreshed through browser automation (CDP timed out); backend REST, WebSocket, and MJPEG were verified directly.
- Production API has no mark-read endpoint; production alerts show Open/Resolved state without a mark-read control.

### Pending tasks
- Review the frontend changes with the team lead and submit a PR targeting `main`.

### Git
- Branch: `feature/amith-dashboard`
- Commit SHA: TBD
- Pull request: TBD
