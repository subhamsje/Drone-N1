"""WebSocket hub for real-time fleet/UAV streaming to operators."""

import json
import logging
from typing import Any, Dict, Set

logger = logging.getLogger("websocket_hub")


class WebSocketHub:
    """Manages connected WebSocket clients and channel subscriptions."""

    def __init__(self):
        self._clients: Set[Any] = set()
        self._subscriptions: Dict[Any, Set[str]] = {}

    async def connect(self, websocket):
        await websocket.accept()
        self._clients.add(websocket)
        self._subscriptions[websocket] = set()
        logger.info("WS client connected — total=%d", len(self._clients))

    def disconnect(self, websocket):
        self._clients.discard(websocket)
        self._subscriptions.pop(websocket, None)

    def subscribe(self, websocket, channels: list):
        subs = self._subscriptions.setdefault(websocket, set())
        for ch in channels:
            subs.add(ch)

    async def broadcast(self, channel: str, payload: Dict[str, Any]):
        msg = json.dumps({"channel": channel, "data": payload})
        dead = []
        for ws in self._clients:
            subs = self._subscriptions.get(ws, set())
            if channel in subs or f"uav:{payload.get('uav_id', '')}" in subs or "all" in subs:
                try:
                    await ws.send_text(msg)
                except Exception:
                    dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def broadcast_snapshot(self, snapshot: Dict[str, Any]):
        uav_id = snapshot.get("uav_id", "unknown")
        await self.broadcast(f"uav:{uav_id}", snapshot)
        await self.broadcast("all", snapshot)


_hub = None


def get_ws_hub() -> WebSocketHub:
    global _hub
    if _hub is None:
        _hub = WebSocketHub()
    return _hub
