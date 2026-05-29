from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/uavs", tags=["telemetry"])


@router.get("")
async def list_uavs(request: Request):
    repo = request.app.state.repo
    return {"uavs": repo.list_uavs()}


@router.get("/{uav_id}/state")
async def get_uav_state(uav_id: str, request: Request):
    repo = request.app.state.repo
    state = repo.get_uav_state(uav_id)
    if not state:
        raise HTTPException(404, f"UAV {uav_id} not found")
    return state


@router.get("/{uav_id}/history")
async def get_history(uav_id: str, request: Request, limit: int = 100):
    repo = request.app.state.repo
    return {"uav_id": uav_id, "history": repo.get_history(uav_id, limit)}


@router.post("/{uav_id}/telemetry")
async def ingest_telemetry(uav_id: str, payload: Dict[str, Any], request: Request):
    workflow = request.app.state.workflow
    payload["uav_id"] = uav_id
    await workflow.telemetry.ingest_snapshot(payload)
    request.app.state.repo.upsert_snapshot(uav_id, payload)
    return {"accepted": True, "uav_id": uav_id}
