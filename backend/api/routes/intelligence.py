"""Mission intelligence API — above autopilot, below operator UI."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


class PlanMissionBody(BaseModel):
    intent: str
    lat: float = 12.97
    lon: float = 77.59
    alt_m: float = 100.0
    waypoints: Optional[List[Dict[str, Any]]] = None
    use_copilot: bool = True


class AdvanceMissionBody(BaseModel):
    phase: Optional[str] = None
    operator: str = "operator"


class CopilotBody(BaseModel):
    message: str
    lat: float = 12.97
    lon: float = 77.59
    alt_m: float = 100.0
    waypoints: Optional[List[Dict[str, Any]]] = None


class TwinScenarioBody(BaseModel):
    scenario: str = "calm"


def _intel(request: Request):
    svc = getattr(request.app.state.workflow, "intelligence", None)
    if not svc:
        raise HTTPException(503, "Mission intelligence not initialized")
    return svc


@router.get("/status")
async def intelligence_status(request: Request):
    svc = _intel(request)
    return {
        "flight_stack": svc.flight_stack.status(),
        "analytics": svc.analytics_snapshot(),
        "fleet": svc.fleet_snapshot(),
        "active_missions": len(svc.lifecycle._missions),
    }


@router.post("/missions/plan")
async def plan_mission(body: PlanMissionBody, request: Request):
    svc = _intel(request)
    result = await svc.lifecycle.plan(
        body.intent,
        {"lat": body.lat, "lon": body.lon, "alt_m": body.alt_m},
        body.waypoints,
        body.use_copilot,
    )
    svc.certification.record_mission_lineage(result["mission_id"], "plan", {"intent": body.intent})
    return result


@router.get("/missions")
async def list_intelligence_missions(request: Request):
    return {"missions": _intel(request).lifecycle.list_missions()}


@router.get("/missions/{mission_id}")
async def get_intelligence_mission(mission_id: str, request: Request):
    m = _intel(request).lifecycle.get_mission(mission_id)
    if not m:
        raise HTTPException(404, "Mission not found")
    return m


@router.post("/missions/{mission_id}/advance")
async def advance_mission(mission_id: str, body: AdvanceMissionBody, request: Request):
    svc = _intel(request)
    result = await svc.lifecycle.advance(mission_id, body.phase, body.operator)
    if result.get("success"):
        phase = body.phase or result.get("mission", {}).get("phase", "unknown")
        svc.certification.record_mission_lineage(mission_id, phase, result.get("phase_result", {}))
    return result


@router.post("/copilot")
async def copilot_generate(body: CopilotBody, request: Request):
    svc = _intel(request)
    geo = svc.geospatial_context(body.lat, body.lon, body.alt_m)
    pkg = svc.lifecycle.copilot.generate_mission_package(
        body.message,
        {"lat": body.lat, "lon": body.lon, "alt_m": body.alt_m},
        geo,
        body.waypoints,
    )
    return pkg


@router.get("/geospatial")
async def geospatial_context(request: Request, lat: float, lon: float, alt_m: float = 100.0):
    return _intel(request).geospatial_context(lat, lon, alt_m)


@router.get("/analytics")
async def operational_analytics(request: Request):
    return _intel(request).analytics_snapshot()


@router.get("/fleet")
async def fleet_intelligence(request: Request):
    snap = request.app.state.repo.get_uav_state(request.app.state.workflow.uav_id)
    return _intel(request).fleet_snapshot(snap)


@router.post("/twin/scenario")
async def load_twin_scenario(body: TwinScenarioBody, request: Request):
    svc = _intel(request)
    scenario = svc.twin_bridge.load_scenario(body.scenario)
    return {"scenario": scenario.to_dict(), "hints": svc.twin_bridge.gazebo_launch_hint()}


@router.get("/certification/export")
async def export_certification(request: Request):
    svc = _intel(request)
    return svc.certification.export_audit_package(svc.lifecycle.list_missions())
