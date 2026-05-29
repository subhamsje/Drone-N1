from fastapi import APIRouter, Request

router = APIRouter(prefix="/inference", tags=["inference"])


@router.get("/models")
async def list_models(request: Request):
    kernel = request.app.state.workflow.bridge.os_kernel
    return {"models": kernel.inference.stats["models"], "stats": kernel.inference.stats}


@router.get("/predictions")
async def latest_predictions(request: Request):
    snap = request.app.state.repo.get_uav_state(request.app.state.workflow.uav_id)
    return {"inference": snap.get("inference") if snap else None}
