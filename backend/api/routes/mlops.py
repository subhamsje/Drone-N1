from fastapi import APIRouter
from pydantic import BaseModel

from backend.mlops.pipeline import MLOpsPipeline

router = APIRouter(prefix="/mlops", tags=["mlops"])

_pipeline = MLOpsPipeline()


class PromoteBody(BaseModel):
    model_id: str
    rollout_pct: float = 5.0


@router.get("/status")
async def mlops_status():
    return _pipeline.get_pipeline_status()


@router.post("/canary")
async def promote_canary(body: PromoteBody):
    ok = _pipeline.promote_to_canary(body.model_id, body.rollout_pct)
    return {"success": ok}


@router.post("/production")
async def promote_production(body: PromoteBody):
    ok = _pipeline.promote_to_production(body.model_id)
    return {"success": ok}
