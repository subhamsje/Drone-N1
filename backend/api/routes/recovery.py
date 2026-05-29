
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/recovery", tags=["recovery"])


class RecoveryTriggerRequest(BaseModel):
    uav_id: str
    policy: str = "EMERGENCY_LAND"
    reason: str = "operator_override"


@router.post("/trigger")
async def trigger_recovery(body: RecoveryTriggerRequest, request: Request):
    workflow = request.app.state.workflow
    wf = await workflow.recovery.trigger_manual(body.policy, body.reason)
    return {"workflow": wf.to_dict() if wf else None}


@router.get("/active")
async def active_recoveries(request: Request):
    workflow = request.app.state.workflow
    return {"workflows": workflow.recovery.get_active_workflows()}
