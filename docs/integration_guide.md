# Module Integration Guide
# AI-Based Smart Gate Monitoring System

This guide provides technical specifications for integrating the modules created by **Siddharth Chandrashekar** (Computer Vision & DeepSORT Tracking) and **Amith Gowda R** (React Frontend & Dashboard) with the core backend architecture developed by **Siddharth Dhanush R**.

---

## 1. Computer Vision Integration (Chandrashekar $\rightarrow$ Dhanush)

### 1.1. Integration Touchpoint
Chandrashekar's tracking module plugs into `backend/app/detection/detector.py` and `backend/app/services/camera_service.py`.

### 1.2. Python Interface Contract
The tracking module must expose a callable tracking processor adhering to this signature:

```python
from typing import List, Dict, Any, Tuple
import numpy as np

class ObjectTracker:
    def update(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Processes a raw BGR frame, runs detection, updates DeepSORT tracks,
        and returns the annotated frame and list of active track dictionaries.

        Returns:
            annotated_frame: np.ndarray (BGR image with boxes, IDs, and labels drawn)
            tracked_objects: List of dictionaries matching the required contract:
                [
                    {
                        "track_id": int,
                        "class_id": int,
                        "class_name": str,
                        "confidence": float,
                        "bbox": [x1, y1, x2, y2],
                        "center": [cx, cy]
                    }, ...
                ]
        """
        ...
```

### 1.3. Centroid Convention
- $c_x = (x_1 + x_2) // 2$
- $c_y = y_2$ (the bottom-center coordinate represents contact with the ground plane, drastically reducing parallax errors in virtual line crossings).

---

## 2. Frontend Integration (Amith $\rightarrow$ Dhanush)

### 2.1. Connecting to the Live Video Feed
Amith can embed the real-time annotated video stream directly in any React component:

```jsx
import React, { useState } from 'react';

export const LiveVideoCard = () => {
  const [streamError, setStreamError] = useState(false);

  return (
    <div className="bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-700">
      <h2 className="text-lg font-semibold text-white mb-2">Live Gate Stream</h2>
      {streamError ? (
        <div className="h-96 flex items-center justify-center bg-gray-900 rounded text-red-400">
          Stream unavailable. Check backend service.
        </div>
      ) : (
        <img
          src="http://localhost:8000/api/video/stream"
          alt="Live Stream"
          className="w-full h-auto rounded-lg"
          onError={() => setStreamError(true)}
        />
      )}
    </div>
  );
};
```

### 2.2. Connecting to WebSocket Telemetry
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/monitoring");

ws.onopen = () => {
  console.log("Connected to Gate Monitoring WebSocket");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  switch (message.type) {
    case "STATS_UPDATE":
      updateKpiCards(message.payload);
      break;
    case "GATE_CROSSING":
      prependActivityLog(message.payload);
      triggerAudioChime();
      break;
    case "SYSTEM_ALERT":
      displayAlertBanner(message.payload);
      break;
  }
};
```

---

## 3. End-to-End Pipeline Verification Procedure

1. Launch backend: `uvicorn backend.app.main:app --port 8000`.
2. Open React dashboard on `http://localhost:5173`.
3. Verify live video stream renders with overlay line and tracking boxes.
4. Simulate crossing (or walk in front of webcam).
5. Verify:
   - WebSocket message arrives in frontend console.
   - Entry/Exit count increments immediately on KPI card.
   - Event row appears in recent activity table.
   - Database record is persisted (`sqlite3 backend/app/gate_monitoring.db "SELECT * FROM monitoring_events;"`).
