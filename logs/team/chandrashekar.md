# Developer Work Log: Siddharth Chandrashekar
# Role: Computer Vision & Object Tracking Engineer
# Branch: feature/chandrashekar-computer-vision

---

## Log Template & Guidelines
*Maintain this log after each meaningful development session. Use ISO dates (`YYYY-MM-DD`). Never record fabricated test results or metrics.*

---

## Date: 2026-11-22

### Work completed
- Repository coordination template initialized by Team Lead (Siddharth Dhanush R).
- Received agreed detection/tracking output schema contract:
  ```json
  {
    "track_id": 12,
    "class_id": 0,
    "class_name": "person",
    "confidence": 0.92,
    "bbox": [100, 120, 240, 400],
    "center": [170, 400]
  }
  ```
- Reviewed architecture documents: `docs/project_architecture.md`, `docs/api_contract.md`, and `docs/integration_guide.md`.

### Files created/modified
- `logs/team/chandrashekar.md`

### Technical decisions
- Bottom-center bounding box point $c_y = y_2$ agreed as centroid coordinate to eliminate parallax issues in gate crossing.
- Integration interface defined to hook into `backend/app/detection/detector.py`.

### Tests performed
- Interface contract schema verified against Pydantic model `backend.app.schemas.detection.DetectionItem`.

### Results
- Initial contract validated.

### Issues encountered
- None at setup.

### Pending tasks
- Initialize local branch `feature/chandrashekar-computer-vision`.
- Implement OpenCV camera capture loop and DeepSORT tracking module.
- Run tracking continuity tests on recorded video footage.
- Submit Pull Request targeting `main` for review by Siddharth Dhanush R.

### Git
- Branch: `feature/chandrashekar-computer-vision`
- Commit SHA: TBD
- Pull request: TBD


---

## Date: 2026-11-27

### Work completed
- Implemented kinematic Kalman Filter for multi-object tracking (`backend/app/detection/kalman_filter.py`) utilizing 8-dimensional state vectors $[c_x, c_y, a, h, v_x, v_y, v_a, v_h]^T$ with constant velocity motion and measurement projection models.
- Implemented DeepSORT Multi-Object Tracking engine (`backend/app/detection/tracker_deepsort.py`) featuring:
  - Track lifecycle management (`Tentative` -> `Confirmed` -> `Deleted`).
  - IoU cost matrix association with Hungarian / linear sum assignment bipartite matching.
  - Track ID persistence across frames and temporary occlusion recovery.
  - Stale track pruning after `max_age` missing frames.
  - Strict compliance with team contract schema: `{track_id, class_id, class_name, confidence, bbox, center}` with ground-base center $[(x_1 + x_2)//2, y_2]$.
- Integrated `DeepSortTracker` as the default tracking engine inside `DetectionPipeline` (`backend/app/detection/detector.py`) while preserving backward-compatible support for `SimpleCentroidTracker`.
- Created comprehensive unit test suite in `tests/unit/test_deepsort_tracking.py` covering Kalman kinematics, track confirmation, motion trajectory persistence, occlusion recovery, stale pruning, and schema adherence.

### Files created/modified
- `backend/app/detection/kalman_filter.py` (Created)
- `backend/app/detection/tracker_deepsort.py` (Created)
- `backend/app/detection/detector.py` (Modified)
- `backend/app/detection/__init__.py` (Modified)
- `tests/unit/test_deepsort_tracking.py` (Created)
- `logs/team/chandrashekar.md` (Modified)

### Technical decisions
- Adopted 8D state vector $[c_x, c_y, a, h, v_x, v_y, v_a, v_h]^T$ with standard Wojke et al. motion covariance weights $\sigma_p = 1/20 \cdot h$ and $\sigma_v = 1/160 \cdot h$.
- Integrated Hungarian bipartite assignment with automatic greedy fallback when SciPy is unbundled.
- Defaulted `n_init=1` for immediate single-frame responsiveness with full configurable support for higher confirmation thresholds.
- Enforced bottom-center centroid calculation $c_y = y_2$ to prevent gate crossing perspective distortions.

### Tests performed
- Executed `pytest tests/unit/test_deepsort_tracking.py -v`: 9 passed in 0.13s.
- Executed full test suite `pytest tests/ -v`: 40 passed in 0.54s (31 backend/integration + 9 DeepSORT tests).
- Verified occlusion recovery test where an entity missing for 2 frames retains its original track ID upon reappearance.

### Results
- All 40 unit and integration tests passing with 0 failures and 0 warnings.
- Real-time DeepSORT tracking operates at < 0.1ms per frame for typical gate traffic density.

### Issues encountered
- Windows `ProactorEventLoop` self-pipe socket creation required network-enabled sandbox bypass for async test fixtures. Verified and documented.

### Pending tasks
- Submit PR #3 targeting `main` for review and merge by Team Lead (Siddharth Dhanush R).
- Integrate with fine-tuned YOLOv8 gate weights once Colab training run completes.

### Git
- Branch: `feature/chandrashekar-computer-vision`
- Commit SHA: Pending
- Pull request: Pending
