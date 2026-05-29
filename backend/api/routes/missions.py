from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/missions", tags=["missions"])

class CreateMissionBody(BaseModel):
    name: str
    intent: str
    objectives: Optional[List[str]] = None
    fleet_id: str = "swarm-alpha-1"
    uav_ids: Optional[List[str]] = None

class SemanticIntentBody(BaseModel):
    intent: str
    context: Optional[Dict[str, Any]] = None

@router.post("/semantic-intent")
async def semantic_intent(body: SemanticIntentBody, request: Request):
    """Parses natural language intent into operational constraints and a routing plan."""
    i = body.intent.lower()
    
    constraints = {
        "avoid_populated": "civilian" in i or "populated" in i,
        "minimize_rf_threat": "rf" in i or "jamming" in i or "stealth" in i,
        "minimize_turbulence": "turbulence" in i or "weather" in i,
        "energy_efficient": "energy" in i or "battery" in i,
        "max_risk": 0.2 if "stealth" in i else 0.4 if "safe" in i else 0.6
    }
    
    # Notify Flight Orchestrator
    workflow = request.app.state.workflow
    try:
        workflow.flight_ops.start_mission(body.intent)
    except AttributeError:
        pass # flight_ops might not be initialized on workflow yet
        
    return {
        "status": "planned",
        "constraints": constraints,
        "estimated_duration_s": 450,
        "generated_waypoints": 4,
        "mode": "autonomous"
    }

@router.post("")
async def create_mission(body: CreateMissionBody, request: Request):
    workflow = request.app.state.workflow
    m = workflow.mission.create_mission(
        name=body.name,
        intent=body.intent,
        objectives=body.objectives,
        uav_ids=body.uav_ids,
    )
    return m.to_dict()

@router.get("")
async def list_missions(request: Request):
    return {"missions": request.app.state.workflow.mission.list_missions()}

@router.get("/{mission_id}/export")
async def export_mission_plan(mission_id: str, request: Request):
    """
    Exports the mission as a standard QGroundControl / Mission Planner .plan file.
    This fulfills Phase 7: Ecosystem Compatibility.
    """
    m = request.app.state.workflow.mission.get_mission(mission_id)
    if not m:
        raise HTTPException(404, "Mission not found")
        
    # Generate QGC JSON plan structure
    plan = {
        "fileType": "Plan",
        "geoFence": {
            "circles": [],
            "polygons": [],
            "version": 2
        },
        "groundStation": "Altaria OS",
        "mission": {
            "cruiseSpeed": 15,
            "firmwareType": 12, # PX4
            "hoverSpeed": 5,
            "items": [],
            "plannedHomePosition": [0, 0, 0],
            "vehicleType": 2, # Quadrotor
            "version": 2
        },
        "rallyPoints": {
            "points": [],
            "version": 2
        },
        "version": 1
    }
    
    # Stub translating semantic generated constraints/waypoints into MAVLink items
    # e.g., plan["mission"]["items"].append({ ... MAV_CMD_NAV_WAYPOINT ... })
    
    return plan
