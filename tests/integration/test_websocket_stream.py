"""
Integration test for WebSocket communication channel and ConnectionManager.
"""

import asyncio
from unittest.mock import AsyncMock
from backend.app.services.connection_manager import ConnectionManager


def test_websocket_manager_lifecycle_and_broadcast():
    """Tests connection registration, message broadcasting, and clean disconnect."""
    async def _test():
        manager = ConnectionManager()
        mock_ws = AsyncMock()

        # Step 1: Connect
        await manager.connect(mock_ws)
        assert len(manager.active_connections) == 1
        mock_ws.accept.assert_awaited_once()

        # Step 2: Broadcast
        payload = {
            "type": "GATE_CROSSING",
            "payload": {
                "track_id": 14,
                "class_name": "car",
                "direction": "ENTRY"
            }
        }
        await manager.broadcast(payload)
        mock_ws.send_text.assert_awaited_once()

        # Step 3: Disconnect
        manager.disconnect(mock_ws)
        assert len(manager.active_connections) == 0

    asyncio.run(_test())


def test_websocket_manager_handles_stale_disconnect():
    """Tests automatic eviction of disconnected / broken websocket clients during broadcast."""
    async def _test():
        manager = ConnectionManager()
        broken_ws = AsyncMock()
        broken_ws.send_text.side_effect = ConnectionResetError("Client dropped abruptly")

        await manager.connect(broken_ws)
        assert len(manager.active_connections) == 1

        # Broadcast should catch exception and clean up stale connection
        await manager.broadcast({"type": "STATS_UPDATE", "payload": {}})
        assert len(manager.active_connections) == 0

    asyncio.run(_test())
