"""
WebSocket Connection Manager for real-time telemetry dissemination.
"""

from typing import List, Dict, Any
import json
import logging
from fastapi import WebSocket

logger = logging.getLogger("gate_monitoring.websocket")


class ConnectionManager:
    """Manages active WebSocket connections from clients."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcasts a JSON message to all connected clients."""
        if not self.active_connections:
            return

        payload = json.dumps(message)
        stale_connections = []

        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending to WebSocket client: {e}")
                stale_connections.append(connection)

        for stale in stale_connections:
            self.disconnect(stale)


connection_manager = ConnectionManager()
