# Gatewatch Smart Gate Monitoring Dashboard

Responsive React/Vite dashboard for the Smart Gate Monitoring System.

## Run locally

Requirements: Node.js 20.19+ or 22.12+.

```powershell
npm install
Copy-Item .env.example .env.local
npm run dev
```

In a second terminal at the backend repository root, start FastAPI:

```powershell
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open the Vite URL printed in the terminal. The backend's OpenAPI page is at `http://localhost:8000/docs`. Run `npm test`, `npm run lint`, and `npm run build` to validate frontend changes.

## Demo and backend configuration

The app starts in demo mode. Demo values are clearly identified as sample data and are not live camera detections.

| Variable | Purpose |
| --- | --- |
| `VITE_DEMO_MODE` | Set to `false` to use the FastAPI backend. |
| `VITE_API_BASE_URL` | Backend origin; defaults to `http://localhost:8000`. |
| `VITE_WEBSOCKET_URL` | Optional WebSocket URL; defaults to the API host's `/ws/monitoring`. |
| `VITE_CAMERA_STREAM_URL` | Optional override for the backend's MJPEG stream URL. |
| `VITE_CAMERA_SOURCE` | Source passed to `/api/camera/start`; defaults to webcam `0`. |

Restart Vite after changing `.env.local`.

The production adapter follows [the API contract](../docs/api_contract.md): it loads stats, paginated events (up to the API's 200-event limit per request), daily/hourly analytics, and alerts; listens for `STATS_UPDATE`, `GATE_CROSSING`, and `SYSTEM_ALERT` WebSocket messages; and uses the MJPEG stream. Overlays are displayed only when the backend includes them in the stream. Activity history can load subsequent API pages. Start/stop controls update the UI only after the backend confirms the operation. Stream retry reloads the configured browser stream and does not issue a camera-control request.

The backend contract reports gate crossings, not total per-frame detections, so total people/vehicle detection cards are shown as unavailable in backend mode. Analytics use the available entry/exit and per-class crossing counts rather than relabeling them as detections. The backend has no mark-read operation; production alerts therefore expose their backend Open/Resolved status without a local read action.

REST failures are shown in the dashboard with a retry action. The browser camera is considered connected only after the MJPEG image loads. Hardware-dependent stream playback and end-to-end operation require a running backend and camera; they are not covered by the frontend build checks.
