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


class RoboticsCommandBody(BaseModel):
    vehicle_id: str = "ROVER-01"
    vehicle_type: str = "UGV_GROUND_ROVER"
    command: str = "DRIVE_VELOCITY"
    params: Dict[str, Any] = {"linear_x": 1.5, "angular_z": 0.2}


@router.get("/robotics/vehicles")
async def get_multi_domain_vehicles():
    from backend.robotics import DomainVehicleType, MultiDomainTelemetryEnvelope
    env = MultiDomainTelemetryEnvelope("ROVER-01", DomainVehicleType.UGV)
    return {
        "active_vehicle": env.project_schema({"x": 10.0, "y": 20.0, "z": 0.0}),
        "supported_domains": [d.value for d in DomainVehicleType]
    }


@router.post("/robotics/command")
async def dispatch_robotics_command(body: RoboticsCommandBody):
    from backend.robotics import DomainVehicleType, RoboticsAdapterFactory
    vtype = DomainVehicleType(body.vehicle_type)
    adapter = RoboticsAdapterFactory.get_adapter(body.vehicle_id, vtype)
    
    if hasattr(adapter, "execute_command"):
        return adapter.execute_command(body.command, body.params)
    elif hasattr(adapter, "drive_velocity"):
        return adapter.drive_velocity(body.params.get("linear_x", 1.0), body.params.get("angular_z", 0.0))
    elif hasattr(adapter, "transition_flight_mode"):
        return adapter.transition_flight_mode(body.params.get("target_mode", "FIXED_WING"))
    elif hasattr(adapter, "control_thrust_rudder"):
        return adapter.control_thrust_rudder(body.params.get("thrust", 80.0), body.params.get("rudder", 0.0))
    return {"status": "DISPATCHED", "vehicle_id": body.vehicle_id}


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


class SignCommandBody(BaseModel):
    command: str = "TAKEOFF"
    params: Dict[str, Any] = {"altitude_m": 120.0}
    operator_id: str = "Capt.Vance"


@router.post("/security/sign-command")
async def sign_command(body: SignCommandBody):
    from backend.security import EcdsaCommandSigner
    signer = EcdsaCommandSigner()
    return signer.sign_command(body.command, body.params, body.operator_id)


@router.post("/security/verify-command")
async def verify_command(signed_package: Dict[str, Any]):
    from backend.security import EcdsaCommandSigner
    signer = EcdsaCommandSigner()
    valid = signer.verify_signature(signed_package)
    return {"verified": valid, "uav_id": signed_package.get("uav_id")}


@router.get("/security/audit-package")
async def get_compliance_audit_package(mission_id: str = "MSN-901"):
    from backend.security import ComplianceAuditExporter
    exporter = ComplianceAuditExporter()
    return exporter.generate_audit_package(mission_id)


@router.get("/security/soc-status")
async def get_soc_status():
    from backend.security import ZeroTrustSocMonitor
    soc = ZeroTrustSocMonitor()
    return soc.get_soc_threat_metrics()


class InjectFaultBody(BaseModel):
    fault_type: str = "MOTOR_RAMP"
    severity: float = 0.6
    target_unit: str = "Altaria-Alpha"


@router.post("/simulation/inject-fault")
async def inject_fault(body: InjectFaultBody):
    from backend.simulation import FaultInjectionEngine
    engine = FaultInjectionEngine()
    return engine.inject_fault(body.fault_type, body.severity, body.target_unit)


@router.post("/simulation/clear-faults")
async def clear_faults():
    from backend.simulation import FaultInjectionEngine
    engine = FaultInjectionEngine()
    return engine.clear_all_faults()


class HandoverBody(BaseModel):
    target_gcs: str = "GCS-BETA-LONDON"
    uav_id: str = "Altaria-Alpha"

class FailoverBody(BaseModel):
    target_link: str = "STARLINK_SATELLITE"


@router.get("/execution/hitl-telemetry")
async def get_hitl_telemetry():
    from backend.execution import HitlHardwareBridge
    bridge = HitlHardwareBridge()
    return bridge.get_hardware_telemetry()


@router.get("/collaboration/federation-mesh")
async def get_federation_mesh():
    from backend.collaboration import MultiOperatorFederationMesh
    mesh = MultiOperatorFederationMesh()
    return {"mesh_nodes": mesh.get_mesh_topology()}


@router.post("/collaboration/handover")
async def initiate_operator_handover(body: HandoverBody):
    from backend.collaboration import MultiOperatorFederationMesh
    mesh = MultiOperatorFederationMesh()
    return mesh.initiate_handover(body.target_gcs, body.uav_id)


@router.get("/intelligence/webrtc-stream")
async def get_webrtc_stream_metadata():
    from backend.intelligence import RtspWebRtcStreamer
    streamer = RtspWebRtcStreamer()
    return streamer.get_stream_metadata()


@router.get("/execution/network-status")
async def get_network_status():
    from backend.execution import MultiLinkNetworkFailover
    failover = MultiLinkNetworkFailover()
    return failover.get_network_status()


@router.post("/execution/network-failover")
async def execute_network_failover(body: FailoverBody):
    from backend.execution import MultiLinkNetworkFailover
    failover = MultiLinkNetworkFailover()
    return failover.trigger_failover(body.target_link)


@router.post("/simulation/weather")
async def simulate_weather(body: SimulateWeatherBody):
    from backend.simulation import WeatherPhysicsSimulator
    sim = WeatherPhysicsSimulator()
    return sim.simulate_environment(body.scenario)
