import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.api.websocket_hub import get_ws_hub

router = APIRouter(tags=["stream"])


@router.websocket("/ws/v1/stream")
async def websocket_stream(websocket: WebSocket):
    hub = get_ws_hub()
    await hub.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
                channels = msg.get("channels") or msg.get("subscribe", ["all"])
                hub.subscribe(websocket, channels if isinstance(channels, list) else ["all"])
                await websocket.send_text(json.dumps({"type": "subscribed", "channels": channels}))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "message": "invalid json"}))
    except WebSocketDisconnect:
        hub.disconnect(websocket)
