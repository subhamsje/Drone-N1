from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/validation", tags=["validation"])


class IndustryModeBody(BaseModel):
    mode: str


@router.get("/probabilistic-safety")
async def probabilistic_safety(request: Request):
    snap = request.app.state.repo.get_uav_state(request.app.state.workflow.uav_id)
    return {"probabilistic_safety": snap.get("probabilistic_safety") if snap else None}


@router.get("/operations")
async def operations_metrics(request: Request):
    snap = request.app.state.repo.get_uav_state(request.app.state.workflow.uav_id)
    return {"operations": snap.get("operations") if snap else None}


@router.post("/industry-mode")
async def set_industry_mode(body: IndustryModeBody, request: Request):
    request.app.state.workflow.bridge.os_kernel.set_industry_mode(body.mode)
    return {"mode": body.mode}


@router.get("/meta-learning")
async def meta_learning(request: Request):
    return request.app.state.workflow.bridge.os_kernel.meta_learning.get_fleet_intelligence_export()


@router.get("/federation")
async def federation(request: Request):
    k = request.app.state.workflow.bridge.os_kernel
    return {"zones": k.federation.list_zones(), "home_zone": k.federation.home_zone}
