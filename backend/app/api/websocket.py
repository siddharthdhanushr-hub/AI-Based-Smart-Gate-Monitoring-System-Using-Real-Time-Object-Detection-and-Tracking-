"""
WebSocket endpoint for real-time monitoring telemetry.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.services.connection_manager import connection_manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/monitoring")
async def websocket_monitoring_endpoint(websocket: WebSocket):
    """
    WebSocket channel broadcasting real-time gate crossings, KPI updates, and alerts.
    """
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "PING":
                await websocket.send_text("PONG")
            elif data == "CLOSE":
                break
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        connection_manager.disconnect(websocket)
