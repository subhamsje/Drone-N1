"""Mission intelligence service — facade for API and workflow."""

import logging
from typing import Any, Dict, Optional

from backend.intelligence.flight_stack.adapter import FlightStackAdapter
from backend.intelligence.mission.lifecycle import MissionLifecycleOrchestrator
from backend.intelligence.analytics import OperationalAnalytics
from backend.intelligence.fleet_intel import FleetIntelligenceLayer
from backend.intelligence.certification import CertificationEvidenceBuilder
from backend.intelligence.twin_bridge import DigitalTwinBridge
from backend.intelligence.real_world_intel import EnvironmentalIntelligence

logger = logging.getLogger("mission_intelligence")

class MissionIntelligenceService:
    def __init__(self, workflow):
        self._workflow = workflow
        kernel = workflow.bridge.os_kernel
        self.flight_stack = FlightStackAdapter(workflow.uav_id, kernel.px4)
        self.lifecycle = MissionLifecycleOrchestrator(
            kernel,
            self.flight_stack,
            workflow.uav_id,
            snapshot_provider=workflow.bridge.run_cycle,
        )
        self.analytics = OperationalAnalytics(workflow.fleet_id)
        self.fleet = FleetIntelligenceLayer(
            workflow.fleet_id,
            [workflow.uav_id, "UAV-101", "UAV-102", "UAV-103"],
        )
        self.certification = CertificationEvidenceBuilder(kernel.evidence_dag)
        self.twin_bridge = DigitalTwinBridge()
        self.environment = EnvironmentalIntelligence()

    async def on_snapshot(self, snapshot: Dict[str, Any]):
        self.analytics.ingest_snapshot(snapshot)
        threat = float(snapshot.get("risk", {}).get("value", 0))
        if threat > 0.75:
            self.fleet.propagate_threat(snapshot.get("uav_id", self._workflow.uav_id), threat)

    def geospatial_context(self, lat: float, lon: float, alt_m: float = 100.0) -> Dict[str, Any]:
        return self.lifecycle.geospatial.get_context(lat, lon, alt_m)

    def analytics_snapshot(self) -> Dict[str, Any]:
        active = sum(1 for m in self.lifecycle._missions.values() if m.phase.value in ("execute", "monitor"))
        return self.analytics.snapshot(active).to_dict()

    def fleet_snapshot(self, snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        per = {self._workflow.uav_id: snapshot} if snapshot else {}
        return self.fleet.fleet_status(per)
