from fastapi import APIRouter, Request

router = APIRouter(prefix="/fleet", tags=["fleet"])


@router.get("/{fleet_id}/health")
async def fleet_health(fleet_id: str, request: Request):
    workflow = request.app.state.workflow
    if workflow.fleet_id != fleet_id:
        return {"fleet_id": fleet_id, "status": "unknown"}
    summary = workflow.fleet.get_fleet_summary()
    state = request.app.state.repo.get_uav_state(workflow.uav_id)
    fleet_data = workflow.fleet.evaluate_from_snapshot(state or {})
    return {"fleet_id": fleet_id, "summary": summary, "health": fleet_data}
