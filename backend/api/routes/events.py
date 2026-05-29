from typing import Optional

from fastapi import APIRouter, Request

from backend.events.bus import get_event_bus
from backend.events.schemas import EventType

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
async def query_events(
    request: Request,
    uav_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
):
    bus = get_event_bus()
    repo = request.app.state.repo
    et = EventType(event_type) if event_type else None
    events = bus.get_history(uav_id=uav_id, event_type=et, limit=limit)
    return {
        "events": [e.to_dict() for e in events],
        "stored": repo.query_events(uav_id=uav_id, limit=limit),
    }
