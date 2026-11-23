# Frontend Dashboard Specifications & Guidelines
# Assigned to: Amith Gowda R (Frontend Engineer)
# Branch: feature/amith-dashboard

Welcome Amith! This folder houses the React + Tailwind CSS smart surveillance dashboard.

---

## 1. Tech Stack
- **Framework**: React 18+ (Vite recommended)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React / Heroicons
- **Charts**: Recharts / Chart.js
- **Live Video**: HTML5 Image element with MJPEG stream URL

---

## 2. API & Stream Connection Endpoints

The FastAPI backend runs on `http://localhost:8000`:

| Resource | Protocol | URL | Description |
|---|---|---|---|
| **Live Stream** | HTTP MJPEG | `http://localhost:8000/api/video/stream` | Annotated live video feed |
| **Realtime Stats** | HTTP GET | `http://localhost:8000/api/monitoring/stats` | Cumulative and today counts |
| **Event History** | HTTP GET | `http://localhost:8000/api/monitoring/events` | Paginated crossing events |
| **Daily Analytics** | HTTP GET | `http://localhost:8000/api/analytics/daily?days=7` | Daily movement trends |
| **Hourly Analytics** | HTTP GET | `http://localhost:8000/api/analytics/hourly` | 24-hour peak hour curve |
| **Alerts** | HTTP GET | `http://localhost:8000/api/alerts` | Security and system notifications |
| **Camera Start** | HTTP POST | `http://localhost:8000/api/camera/start` | Start camera monitoring |
| **Camera Stop** | HTTP POST | `http://localhost:8000/api/camera/stop` | Stop camera monitoring |
| **Camera Switch** | HTTP POST | `http://localhost:8000/api/camera/source` | Switch to webcam or file |
| **WebSocket** | WS | `ws://localhost:8000/ws/monitoring` | Real-time push updates |

---

## 3. Recommended Page Layouts

1. **Overview Dashboard**:
   - Top Bar: Camera connection status, current FPS, active source name.
   - 4 KPI Stat Cards: Total Entries, Total Exits, People on Site, Vehicles on Site.
   - Center Left: Live Video feed (`/api/video/stream`).
   - Center Right: Real-time crossing activity log (updates via WebSocket `GATE_CROSSING`).
   - Bottom: Hourly traffic distribution bar chart.
2. **Live Monitoring Page**:
   - Fullscreen video player with detection overlays.
   - Camera source selector (switch between webcam and recorded video files).
   - Start / Stop control buttons.
3. **Analytics Page**:
   - Date range selector.
   - Daily entry vs. exit comparison chart.
   - Category breakdown (People vs. Cars vs. Motorcycles vs. Buses vs. Trucks).
4. **Alerts & Anomaly Drawer**:
   - Unread alerts counter, severity badges (INFO, WARNING, CRITICAL).

---

## 4. Frontend Development Rules
- Do NOT calculate detections in JavaScript — all AI is computed in Python by the backend.
- During early UI construction, you may use mock data, provided it is clearly marked as mock data in code. Replace all mock data before PR submission.
- Maintain your activity log at `logs/team/amith.md`.
