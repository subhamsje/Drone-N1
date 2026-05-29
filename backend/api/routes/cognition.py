
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/cognition", tags=["cognition"])


class AutonomyModeBody(BaseModel):
    mode: str  # MANUAL | ASSISTED | SUPERVISED | AUTONOMOUS | SURVIVAL


class MissionIntentBody(BaseModel):
    intent: str


@router.get("/state")
async def cognition_state(request: Request):
    snap = request.app.state.repo.get_uav_state(request.app.state.workflow.uav_id)
    if not snap:
        raise HTTPException(404, "No cognitive state yet")
    return {
        "sensor_trust": snap.get("sensor_trust"),
        "cognition": snap.get("cognition"),
        "survival": snap.get("survival"),
        "inference": snap.get("inference"),
        "vision": snap.get("vision"),
        "autonomy_mode": snap.get("autonomy_mode"),
    }


@router.post("/autonomy-mode")
async def set_autonomy_mode(body: AutonomyModeBody, request: Request):
    from altaria_os.autonomy_modes import AutonomyMode
    request.app.state.workflow.bridge.os_kernel.autonomy.set_mode(AutonomyMode(body.mode))
    return {"autonomy_mode": body.mode}


@router.post("/mission-intent")
async def set_mission_intent(body: MissionIntentBody, request: Request):
    request.app.state.workflow.bridge.os_kernel.set_mission_intent(body.intent)
    return {"intent": body.intent, "constraints": request.app.state.workflow.bridge.os_kernel.routing.parse_semantic_intent(body.intent)}


@router.get("/survival")
async def survival_plan(request: Request):
    snap = request.app.state.repo.get_uav_state(request.app.state.workflow.uav_id)
    return {"survival": snap.get("survival") if snap else None}
