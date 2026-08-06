"""Bounded Context API Router — Unifies Knowledge, Robotics, Edge, Collaboration, Mission Graph, Analytics & Simulation."""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/bounded-contexts", tags=["bounded-contexts"])

# Pydantic Schemas
class SearchKnowledgeBody(BaseModel):
    query: str

class SpatialPinBody(BaseModel):
    author: str
    text: str
    lat: float
    lon: float
    alt_m: float = 80.0

class CompileGraphBody(BaseModel):
    nodes: List[Dict[str, Any]]

class SimulateWeatherBody(BaseModel):
    scenario: str = "turbulent_wind"


@router.post("/knowledge/search")
async def search_knowledge_graph(body: SearchKnowledgeBody):
    from backend.knowledge import OperationalKnowledgeGraph
    kg = OperationalKnowledgeGraph()
    return kg.search(body.query)


@router.get("/robotics/vehicles")
async def get_multi_domain_vehicles():
    from backend.robotics import DomainVehicleType, MultiDomainTelemetryEnvelope
    env = MultiDomainTelemetryEnvelope("ROVER-01", DomainVehicleType.UGV)
    return {
        "active_vehicle": env.project_schema({"x": 10.0, "y": 20.0, "z": 0.0}),
        "supported_domains": [d.value for d in DomainVehicleType]
    }


@router.get("/edge/hardware")
async def get_edge_hardware_status():
    from backend.edge import JetsonEdgeManager
    mgr = JetsonEdgeManager()
    return mgr.get_hardware_status()


@router.get("/collaboration/pins")
async def get_spatial_pins():
    from backend.collaboration import SpatialCollaborationEngine
    engine = SpatialCollaborationEngine()
    return {"pins": engine.get_all_pins()}


@router.post("/collaboration/pins")
async def add_spatial_pin(body: SpatialPinBody):
    from backend.collaboration import SpatialCollaborationEngine
    engine = SpatialCollaborationEngine()
    return engine.add_pin(body.author, body.text, {"lat": body.lat, "lon": body.lon, "alt_m": body.alt_m})


@router.post("/mission/compile-graph")
async def compile_mission_graph(body: CompileGraphBody):
    from backend.mission import MissionGraphCompiler
    compiler = MissionGraphCompiler()
    return compiler.compile_graph(body.nodes)


@router.get("/analytics/economics")
async def get_mission_economics(duration_min: float = 14.5, battery_wh: float = 85.0):
    from backend.analytics import MissionEconomicsCalculator
    calc = MissionEconomicsCalculator()
    return calc.calculate_mission_cost(duration_min, battery_wh)


@router.post("/simulation/weather")
async def simulate_weather(body: SimulateWeatherBody):
    from backend.simulation import WeatherPhysicsSimulator
    sim = WeatherPhysicsSimulator()
    return sim.simulate_environment(body.scenario)
