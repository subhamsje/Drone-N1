from fastapi import APIRouter, Request

router = APIRouter(prefix="/platform", tags=["platform"])


@router.get("/status")
async def platform_status(request: Request):
    k = request.app.state.workflow.bridge.os_kernel
    snap = request.app.state.repo.get_uav_state(k.uav_id)
    return {
        "os_version": snap.get("os_version") if snap else "8.0.0",
        "flight_hour_intelligence": snap.get("flight_hour_intelligence") if snap else None,
        "hardware_cognition": snap.get("hardware_cognition") if snap else None,
        "operational_certification": snap.get("operational_certification") if snap else None,
        "planetary_airspace": snap.get("planetary_airspace") if snap else None,
        "embodied_evolution": snap.get("embodied_evolution") if snap else None,
        "collective_intelligence": snap.get("collective_intelligence") if snap else None,
        "strategic_doctrine": snap.get("strategic_doctrine") if snap else None,
        "mission_evidence_dag": snap.get("mission_evidence_dag") if snap else None,
        "embodied_learning": snap.get("embodied_learning") if snap else None,
        "foundation_world_model": snap.get("foundation_world_model") if snap else None,
        "embodied_cognition": snap.get("embodied_cognition") if snap else None,
        "world_model": snap.get("world_model") if snap else None,
        "autonomous_operations": snap.get("autonomous_operations") if snap else None,
        "operational_trust": snap.get("operational_trust") if snap else None,
        "mixed_criticality": snap.get("mixed_criticality") if snap else None,
        "meta_cognition": snap.get("meta_cognition") if snap else None,
        "planetary_intelligence": snap.get("planetary_intelligence") if snap else None,
        "enterprise_roi": snap.get("enterprise_roi") if snap else None,
        "evolution": snap.get("evolution") if snap else None,
        "cognition_fabric": k.cognition_fabric.get_fabric_status(),
        "planetary_federation": k.planetary_federation.get_planetary_status(),
    }


@router.get("/world-model")
async def world_model(request: Request):
    snap = request.app.state.repo.get_uav_state(request.app.state.workflow.uav_id)
    return {"world_model": snap.get("world_model") if snap else None}


@router.get("/meta-cognition")
async def meta_cognition(request: Request):
    snap = request.app.state.repo.get_uav_state(request.app.state.workflow.uav_id)
    return {"meta_cognition": snap.get("meta_cognition") if snap else None}


@router.get("/mission-replay")
async def mission_replay(request: Request):
    k = request.app.state.workflow.bridge.os_kernel
    return k.mission_replay.get_replay()


@router.get("/formal-certification")
async def formal_cert(request: Request):
    k = request.app.state.workflow.bridge.os_kernel
    return k.formal_cert.export_certification_bundle()


@router.get("/explanation")
async def get_explanation(request: Request):
    snap = request.app.state.repo.get_uav_state(request.app.state.workflow.uav_id)
    return {"explanation": snap.get("explanation") if snap else None}


@router.get("/compliance")
async def compliance(request: Request):
    k = request.app.state.workflow.bridge.os_kernel
    return k.certification.export_evidence_pack()


@router.get("/knowledge-graph")
async def knowledge_graph(request: Request):
    k = request.app.state.workflow.bridge.os_kernel
    return {
        "stats": k.knowledge_graph.get_stats(),
        "turbulence_hotspots": k.knowledge_graph.query_turbulence_hotspots(),
    }


@router.get("/dashboard/executive-metrics")
async def executive_metrics(request: Request):
    """
    Retrieves high-level operational metrics (Flight Hours, Success Rates) 
    from the ClickHouse Telemetry Lake for the Phase 11 Operational Dashboard.
    """
    from backend.telemetry_lake.clickhouse_client import ClickHouseLake
    from backend.config import BACKEND_CONFIG
    
    # In production, this would be an injected singleton dependency
    lake = ClickHouseLake(BACKEND_CONFIG.telemetry_lake_url if hasattr(BACKEND_CONFIG, 'telemetry_lake_url') else "clickhouse://default:@localhost:9000/altaria")
    metrics = await lake.get_executive_metrics()
    return metrics


@router.get("/logs")
async def get_system_logs(request: Request, limit: int = 50):
    """
    Retrieves live system event history for the Evidence Center.
    """
    from backend.events.bus import get_event_bus
    bus = get_event_bus()
    history = bus.get_history(limit=limit)
    return [e.to_dict() for e in history]
