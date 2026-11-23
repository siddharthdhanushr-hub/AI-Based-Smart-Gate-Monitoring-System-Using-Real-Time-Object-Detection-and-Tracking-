# API & WebSocket Contract Specification
# AI-Based Smart Gate Monitoring System

This document outlines the authoritative REST API and WebSocket communication contract provided by the FastAPI backend for the React Dashboard (Amith Gowda R) and test harnesses.

---

## 1. General Principles
- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api`
- **Content-Type**: `application/json` (except video streaming which is `multipart/x-mixed-replace; boundary=frame`)
- **Status Codes**: Standard HTTP codes (`200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `500 Internal Server Error`).

---

## 2. REST API Endpoints

### 2.1. Camera Controls

#### `POST /api/camera/start`
Starts the video capture and real-time inference loop.

- **Request Body**: (Optional)
```json
{
  "source": "0",
  "gate_line": {
    "p1": [100, 350],
    "p2": [1180, 350]
  }
}
```
- **Response `200 OK`**:
```json
{
  "status": "success",
  "message": "Camera monitoring loop started",
  "active_source": "0",
  "is_running": true,
  "started_at": "2026-11-22T20:00:00Z"
}
```

---

#### `POST /api/camera/stop`
Gracefully stops video capture and monitoring loop.

- **Request Body**: None
- **Response `200 OK`**:
```json
{
  "status": "success",
  "message": "Camera monitoring loop stopped",
  "is_running": false,
  "stopped_at": "2026-11-22T20:05:00Z"
}
```

---

#### `POST /api/camera/source`
Changes the active camera input source without restarting the web service.

- **Request Body**:
```json
{
  "source_type": "webcam",
  "source_value": "0"
}
```
*(For recorded video, set `"source_type": "file"` and `"source_value": "ai/dataset/sample_gate.mp4"`)*

- **Response `200 OK`**:
```json
{
  "status": "success",
  "source_type": "webcam",
  "source_value": "0",
  "message": "Camera source switched successfully"
}
```

---

### 2.2. Live Video Feed

#### `GET /api/video/stream`
Returns an MJPEG stream of live frames with the virtual gate line; detection boxes, track IDs, and class names are included when the configured detector model is loaded.
The stream uses raw capture frames until the monitoring inference loop publishes its first annotated frame.

- **Response Headers**:
  - `Content-Type: multipart/x-mixed-replace; boundary=frame`
- **Usage in React**:
```jsx
<img 
  src="http://localhost:8000/api/video/stream" 
  alt="Live Annotated Gate Stream" 
  className="w-full h-auto rounded-lg shadow-md"
/>
```

---

### 2.3. Monitoring Statistics & Events

#### `GET /api/monitoring/stats`
Returns aggregated real-time statistics (total counts, today's counts, and category breakdown).
The `is_active` field reflects whether the monitoring inference loop is currently running.

- **Query Parameters**: None
- **Response `200 OK`**:
```json
{
  "timestamp": "2026-11-22T20:10:00Z",
  "is_active": true,
  "total_entries": 142,
  "total_exits": 98,
  "net_inside": 44,
  "today": {
    "entries": 85,
    "exits": 61,
    "people_entries": 52,
    "people_exits": 38,
    "vehicle_entries": 33,
    "vehicle_exits": 23
  },
  "by_class": {
    "person": { "entry": 52, "exit": 38 },
    "bicycle": { "entry": 4, "exit": 3 },
    "car": { "entry": 21, "exit": 14 },
    "motorcycle": { "entry": 6, "exit": 5 },
    "bus": { "entry": 1, "exit": 1 },
    "truck": { "entry": 1, "exit": 0 }
  }
}
```

---

#### `GET /api/monitoring/events`
Returns paginated list of gate crossing events.

- **Query Parameters**:
  - `limit` (int, default `50`, max `200`)
  - `offset` (int, default `0`)
  - `direction` (str, optional: `"ENTRY"`, `"EXIT"`)
  - `class_name` (str, optional: `"person"`, `"car"`, etc.)
- **Response `200 OK`**:
```json
{
  "total_count": 240,
  "limit": 50,
  "offset": 0,
  "events": [
    {
      "id": 1,
      "event_id": "evt_9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "track_id": 14,
      "class_id": 2,
      "class_name": "car",
      "direction": "ENTRY",
      "confidence": 0.9412,
      "bbox": [210, 180, 520, 460],
      "centroid": [365, 460],
      "timestamp": "2026-11-22T20:09:42Z",
      "snapshot_path": "/snapshots/evt_9b1deb4d.jpg"
    }
  ]
}
```

---

### 2.4. Historical Analytics

#### `GET /api/analytics/daily`
Returns daily aggregated counts for historical charts.

- **Query Parameters**:
  - `days` (int, default `7`, max `30`)
- **Response `200 OK`**:
```json
{
  "days": 7,
  "data": [
    {
      "date": "2026-11-22",
      "entries": 85,
      "exits": 61,
      "people": 90,
      "vehicles": 56
    },
    {
      "date": "2026-11-21",
      "entries": 120,
      "exits": 115,
      "people": 145,
      "vehicles": 90
    }
  ]
}
```

---

#### `GET /api/analytics/hourly`
Returns hourly breakdown of traffic for peak hour analysis.

- **Query Parameters**:
  - `date` (str, optional, format: `YYYY-MM-DD`, default: today)
- **Response `200 OK`**:
```json
{
  "date": "2026-11-22",
  "hourly_distribution": [
    { "hour": "08:00", "entries": 24, "exits": 2, "people": 18, "vehicles": 8 },
    { "hour": "09:00", "entries": 45, "exits": 5, "people": 32, "vehicles": 18 },
    { "hour": "17:00", "entries": 6, "exits": 38, "people": 25, "vehicles": 19 }
  ]
}
```

---

### 2.5. Alerts & Anomalies

#### `GET /api/alerts`
Retrieves security and operational alerts.

- **Query Parameters**:
  - `limit` (int, default `20`)
  - `unread_only` (bool, default `false`)
- **Response `200 OK`**:
```json
{
  "total": 3,
  "alerts": [
    {
      "id": 1,
      "alert_type": "COUNTERFLOW",
      "severity": "WARNING",
      "message": "Vehicle track #28 moved in reverse against one-way exit gate",
      "timestamp": "2026-11-22T19:45:12Z",
      "metadata": { "track_id": 28, "class_name": "car" }
    }
  ]
}
```

---

## 3. WebSocket Real-Time Telemetry

- **Endpoint**: `/ws/monitoring`
- **Protocol**: Standard WebSocket (JSON frames)

### 3.1. Messages Emitted by Server

#### A. Periodic Heartbeat / Stats Summary (Every 1000ms)
```json
{
  "type": "STATS_UPDATE",
  "payload": {
    "timestamp": "2026-11-22T20:12:01Z",
    "total_entries": 143,
    "total_exits": 98,
    "current_tracked_objects": 4,
    "camera_fps": 28.4
  }
}
```

#### B. Immediate Gate Crossing Event (Emitted instantaneously upon line crossing)
```json
{
  "type": "GATE_CROSSING",
  "payload": {
    "event_id": "evt_c84a87b3",
    "track_id": 15,
    "class_name": "person",
    "direction": "ENTRY",
    "confidence": 0.9125,
    "timestamp": "2026-11-22T20:12:03Z"
  }
}
```

#### C. Alert Notification
```json
{
  "type": "SYSTEM_ALERT",
  "payload": {
    "severity": "CRITICAL",
    "alert_type": "CAMERA_DISCONNECTED",
    "message": "Video input feed frame dropped repeatedly",
    "timestamp": "2026-11-22T20:12:10Z"
  }
}
```
