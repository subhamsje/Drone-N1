"""
Altaria N1 Backend API Gateway
FastAPI entry point — REST, WebSocket, metrics, autonomous cognitive loop.
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backend.config import BACKEND_CONFIG
from backend.api.routes import (
    health, telemetry, recovery, fleet, missions, events, stream,
    cognition, inference, edge, mlops, execution, validation, platform, intelligence,
)
from backend.api.websocket_hub import get_ws_hub
from backend.pipeline.autonomous_workflow import AutonomousWorkflowEngine
from backend.storage.repositories import get_state_repository
from backend.observability.metrics import get_metrics
from backend.events.bus import get_event_bus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("altaria.api")


def operating_geo_lat(snapshot, live_tel):
    if live_tel and live_tel.get("lat") is not None:
        return float(live_tel["lat"])
    from backend.api.operating_projection import project_aircraft_snapshot
    return project_aircraft_snapshot(snapshot, live_tel)["geo"]["lat"]


def operating_geo_lon(snapshot, live_tel):
    if live_tel and live_tel.get("lon") is not None:
        return float(live_tel["lon"])
    from backend.api.operating_projection import project_aircraft_snapshot
    return project_aircraft_snapshot(snapshot, live_tel)["geo"]["lon"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = BACKEND_CONFIG
    workflow = AutonomousWorkflowEngine()
    repo = get_state_repository()
    hub = get_ws_hub()
    metrics = get_metrics()
    bus = get_event_bus()

    app.state.workflow = workflow
    app.state.repo = repo
    app.state.hub = hub
    app.state.metrics = metrics

    async def on_snapshot(snapshot):
        import time
        from backend.api.cognition_projection import project_channel_payloads
        from backend.api.operating_projection import project_operating_state

        t0 = time.monotonic()
        intel = workflow.intelligence
        live_tel = None
        try:
            live_tel = await intel.flight_stack.get_live_telemetry()
        except Exception:
            pass
        operating = project_operating_state(
            snapshot,
            intelligence_missions=intel.lifecycle.list_missions(),
            fleet_intel=intel.fleet_snapshot(snapshot),
            live_telemetry=live_tel,
            geospatial=intel.geospatial_context(
                operating_geo_lat(snapshot, live_tel),
                operating_geo_lon(snapshot, live_tel),
            ),
            analytics=intel.analytics_snapshot(),
            edge_status=workflow.edge.get_status(),
            flight_stack=intel.flight_stack.status(),
        )
        snapshot["operating_state"] = operating
        repo.upsert_snapshot(snapshot.get("uav_id", cfg.cognitive.uav_id), snapshot)
        await hub.broadcast("operating_state", operating)
        await hub.broadcast("cognition", operating["cognition"])
        await hub.broadcast_snapshot(snapshot)
        for channel, payload in project_channel_payloads(snapshot).items():
            if payload:
                await hub.broadcast(channel, payload)
        latency = (time.monotonic() - t0) * 1000
        metrics.record_cycle(
            snapshot.get("uav_id", cfg.cognitive.uav_id),
            latency,
            float(snapshot.get("risk", {}).get("value", 0)),
        )
        if snapshot.get("anomaly", {}).get("is_anomaly"):
            metrics.record_ingest(snapshot.get("uav_id", cfg.cognitive.uav_id))

    workflow.bridge.on_snapshot(on_snapshot)

    cognitive_task = None
    if cfg.enable_cognitive_loop:
        cognitive_task = asyncio.create_task(
            workflow.start(interval_ms=cfg.cognitive.loop_ms)
        )
        logger.info("Cognitive loop started @ %dms", cfg.cognitive.loop_ms)

    yield

    workflow.stop()
    if cognitive_task:
        cognitive_task.cancel()
        try:
            await cognitive_task
        except asyncio.CancelledError:
            pass
    logger.info("Backend shutdown complete")


def create_app() -> FastAPI:
    cfg = BACKEND_CONFIG.api
    app = FastAPI(
        title="Altaria N1 Cognitive Backend",
        description="AI-native autonomous UAV reliability, recovery, and fleet cognition platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = cfg.api_prefix
    app.include_router(health.router, prefix=prefix)
    app.include_router(telemetry.router, prefix=prefix)
    app.include_router(recovery.router, prefix=prefix)
    app.include_router(fleet.router, prefix=prefix)
    app.include_router(missions.router, prefix=prefix)
    app.include_router(events.router, prefix=prefix)
    app.include_router(stream.router)
    app.include_router(cognition.router, prefix=prefix)
    app.include_router(inference.router, prefix=prefix)
    app.include_router(edge.router, prefix=prefix)
    app.include_router(mlops.router, prefix=prefix)
    app.include_router(execution.router, prefix=prefix)
    app.include_router(validation.router, prefix=prefix)
    app.include_router(platform.router, prefix=prefix)
    app.include_router(intelligence.router, prefix=prefix)

    @app.get("/metrics")
    async def prometheus_metrics():
        body, ctype = get_metrics().export()
        return Response(content=body, media_type=ctype)

    @app.get("/")
    async def root():
        return {
            "service": "altaria-n1-cognitive-os",
            "version": "8.0.0",
            "os": "altaria_os",
            "docs": "/docs",
            "websocket": BACKEND_CONFIG.api.ws_path,
            "api": BACKEND_CONFIG.api.api_prefix,
        }

    return app


app = create_app()


def main():
    import uvicorn
    cfg = BACKEND_CONFIG.api
    uvicorn.run(
        "backend.api.app:app",
        host=cfg.host,
        port=cfg.port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
