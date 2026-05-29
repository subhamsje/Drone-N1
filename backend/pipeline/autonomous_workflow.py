"""Autonomous event-driven workflow — Tier-1 OS-integrated nervous system."""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from backend.config import BACKEND_CONFIG
from backend.events.bus import get_event_bus
from backend.events.schemas import DomainEvent, EventType
from backend.events.topics import Topic
from backend.ros2_bridge.node import AltariaROS2Node
from backend.ros2_bridge.telemetry_adapter import ROS2TelemetryAdapter
from backend.ros2_bridge.gazebo_bridge import GazeboCounterfactualBridge
from backend.services.recovery_service import RecoveryOrchestrator
from backend.services.telemetry_ingestion import TelemetryIngestionService
from backend.services.fleet_service import FleetCoordinationService
from backend.services.cyber_service import CybersecurityService
from backend.services.mission_service import MissionGovernanceService
from backend.operations.flight_orchestrator import FlightOperationsOrchestrator
from backend.edge.runtime import EdgeRuntime
from backend.storage.repositories import get_state_repository
from backend.observability.metrics import get_metrics
from backend.intelligence.service import MissionIntelligenceService
from backend.services.security_service import SecurityService
from backend.services.cognition_service import CognitionService

logger = logging.getLogger("autonomous_workflow")


class AutonomousWorkflowEngine:
    """
    Central nervous system:
    ROS2 Telemetry → Ingest → Inference events → Survival → Gazebo Validation → Recovery → Fleet
    """

    def __init__(self):
        cfg = BACKEND_CONFIG.cognitive
        self.uav_id = cfg.uav_id
        self.fleet_id = cfg.fleet_id

        # Replace Python stubs with ROS2/Gazebo Infrastructure
        self.ros_node = AltariaROS2Node(self.uav_id)
        self.ros_telemetry = ROS2TelemetryAdapter(self.ros_node)
        self.gazebo_bridge = GazeboCounterfactualBridge(self.ros_node)
        
        # Restore bridge for backward compatibility
        from backend.services.cognitive_bridge import CognitiveBridge
        self.bridge = CognitiveBridge(cfg.uav_id)
        self.cognition = self.bridge._cognition

        self.telemetry = TelemetryIngestionService(cfg.uav_id)
        self.security = SecurityService(self.uav_id)
        self.recovery = RecoveryOrchestrator(cfg.uav_id, self.telemetry.gateway)
        self.fleet = FleetCoordinationService(cfg.fleet_id, cfg.uav_id)
        self.cyber = CybersecurityService(cfg.uav_id)
        self.mission = MissionGovernanceService(cfg.fleet_id)
        self.flight_ops = FlightOperationsOrchestrator(cfg.uav_id, cfg.fleet_id)
        self.edge = EdgeRuntime(cfg.uav_id, device="jetson_orin")
        self.intelligence = MissionIntelligenceService(self)
        self._repo = get_state_repository()
        self._bus = get_event_bus()
        self._metrics = get_metrics()
        self._running = False

        self.bridge.on_snapshot(self._on_snapshot)
        self._kernel_initialized = False

    async def _ensure_kernel(self):
        if not self._kernel_initialized:
            await self.bridge.os_kernel.initialize_execution()
            self._kernel_initialized = True

    async def _on_snapshot(self, snapshot: Dict[str, Any]):
        await self._ensure_kernel()
        t0 = time.monotonic()
        snapshot["uav_id"] = self.uav_id

        self.edge.buffer_telemetry(snapshot)
        await self.intelligence.on_snapshot(snapshot)
        await self.telemetry.ingest_snapshot(snapshot)
        await self.cyber.publish_threat(snapshot)
        await self.fleet.publish_fleet_health(snapshot)
        
        # Advance flight operations intelligence
        ops_metrics = self.flight_ops.ingest_cycle(snapshot)
        snapshot["operational_intelligence"] = ops_metrics

        # Survival-driven recovery uses OS survival plan
        survival = snapshot.get("survival", {})
        if survival.get("urgency") in ("IMMEDIATE", "HIGH"):
            await self._bus.publish(
                DomainEvent.create(
                    EventType.RECOVERY_STARTED,
                    self.uav_id,
                    {"source": "survival_engine", "plan": survival},
                ),
                Topic.RECOVERY_WORKFLOW,
            )

        for mid in list(self.mission._missions.keys()):
            await self.mission.evaluate_reroute(snapshot, mid)

        await self.recovery.process_snapshot(snapshot)

        # Execute real PX4 commands when OS queued survival execution
        kernel = self.bridge.os_kernel
        exec_result = await kernel.execute_pending_recovery()
        if exec_result:
            self._repo.append_event({
                "uav_id": self.uav_id,
                "event_type": "execution.mavsdk",
                "result": exec_result,
            })

        inference = snapshot.get("inference", {})
        if inference.get("crash_probability", 0) > 0.7:
            self._metrics.record_recovery(self.uav_id, "predicted_crash")

        self._repo.append_event({
            "uav_id": self.uav_id,
            "event_type": "cognitive.os.cycle",
            "cycle": snapshot.get("cycle"),
            "risk": snapshot.get("risk", {}).get("value"),
            "survival_strategy": survival.get("strategy"),
            "autonomy_mode": snapshot.get("autonomy_mode"),
        })

        latency = (time.monotonic() - t0) * 1000
        self._metrics.record_cycle(
            self.uav_id, latency, float(snapshot.get("risk", {}).get("value", 0))
        )

    async def start(self, interval_ms: Optional[int] = None):
        interval = interval_ms or BACKEND_CONFIG.cognitive.loop_ms
        self._running = True
        logger.info(
            "Altaria OS workflow — uav=%s fleet=%s edge=%s [ROS2 Enabled]",
            self.uav_id, self.fleet_id, self.edge.get_status()["device"],
        )
        self.ros_node.start()
        await self.bridge.start_loop(interval)

    def start_background(self):
        asyncio.create_task(self.start())

    def stop(self):
        self._running = False
        self.ros_node.stop()
        self.bridge.stop()

    async def run_single_cycle(self) -> Dict[str, Any]:
        return await self.bridge.run_cycle()
