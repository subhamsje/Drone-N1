"""Mission lifecycle orchestrator — Plan through Learn."""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, TYPE_CHECKING

from backend.intelligence.mission.copilot import MissionCopilot
from backend.intelligence.geospatial.engine import PlanetaryGeospatialEngine
from engines.predictive_world_model import PredictiveWorldModelEngine

if TYPE_CHECKING:
    from backend.intelligence.flight_stack.adapter import FlightStackAdapter
    from altaria_os.kernel import CognitiveOSKernel

logger = logging.getLogger("mission_lifecycle")


class MissionPhase(str, Enum):
    PLAN = "plan"
    SIMULATE = "simulate"
    VALIDATE = "validate"
    APPROVE = "approve"
    UPLOAD = "upload"
    EXECUTE = "execute"
    MONITOR = "monitor"
    ADAPT = "adapt"
    RECOVER = "recover"
    REPLAY = "replay"
    LEARN = "learn"


PHASE_ORDER = [
    MissionPhase.PLAN,
    MissionPhase.SIMULATE,
    MissionPhase.VALIDATE,
    MissionPhase.APPROVE,
    MissionPhase.UPLOAD,
    MissionPhase.EXECUTE,
    MissionPhase.MONITOR,
]


@dataclass
class MissionLifecycleRecord:
    mission_id: str
    phase: MissionPhase
    intent: str
    plan: Optional[Dict[str, Any]] = None
    simulation: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    approved_by: Optional[str] = None
    approved_at: Optional[float] = None
    upload_result: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    evidence_ids: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "phase": self.phase.value,
            "intent": self.intent,
            "plan": self.plan,
            "simulation": self.simulation,
            "validation": self.validation,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "upload_result": self.upload_result,
            "execution_result": self.execution_result,
            "evidence_ids": self.evidence_ids,
            "created_at": self.created_at,
            "audit_trail": self.audit_trail[-50:],
        }


class MissionLifecycleOrchestrator:
    """Single workflow object — no manual tool switching."""

    def __init__(
        self,
        kernel: "CognitiveOSKernel",
        flight_stack: "FlightStackAdapter",
        uav_id: str,
        snapshot_provider: Optional[Callable[[], Awaitable[Dict[str, Any]]]] = None,
    ):
        self.kernel = kernel
        self.flight_stack = flight_stack
        self.uav_id = uav_id
        self._snapshot_provider = snapshot_provider
        self.copilot = MissionCopilot()
        self.geospatial = PlanetaryGeospatialEngine()
        self.world_model = PredictiveWorldModelEngine()
        self._missions: Dict[str, MissionLifecycleRecord] = {}

    def _audit(self, record: MissionLifecycleRecord, event: str, detail: Dict[str, Any]):
        record.audit_trail.append({"ts": time.time(), "event": event, **detail})

    def list_missions(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self._missions.values()]

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        m = self._missions.get(mission_id)
        return m.to_dict() if m else None

    async def plan(
        self,
        intent: str,
        origin: Dict[str, float],
        waypoints: Optional[List[Dict[str, Any]]] = None,
        use_copilot: bool = True,
    ) -> Dict[str, Any]:
        geo = self.geospatial.get_context(origin["lat"], origin["lon"], origin.get("alt_m", 100))
        if use_copilot:
            pkg = self.copilot.generate_mission_package(intent, origin, geo, waypoints)
            plan_dict = pkg["plan"]
            resolved_intent = pkg["resolved_intent"]
            summary = pkg["operator_summary"]
        else:
            from backend.intelligence.mission.semantic_planner import SemanticMissionPlanner
            plan = SemanticMissionPlanner().plan_from_intent(intent, origin, geo, waypoints)
            plan_dict = plan.to_dict()
            resolved_intent = intent
            summary = f"Planned {len(plan.waypoints)} waypoints"

        mid = str(uuid.uuid4())[:12]
        record = MissionLifecycleRecord(
            mission_id=mid,
            phase=MissionPhase.PLAN,
            intent=resolved_intent,
            plan=plan_dict,
        )
        self._audit(record, "plan_created", {"summary": summary})
        self.kernel.set_mission_intent(resolved_intent)
        self._missions[mid] = record
        return {**record.to_dict(), "operator_summary": summary}

    async def advance(
        self,
        mission_id: str,
        phase: Optional[str] = None,
        operator: str = "operator",
    ) -> Dict[str, Any]:
        record = self._missions.get(mission_id)
        if not record:
            return {"success": False, "error": "mission_not_found"}

        target = MissionPhase(phase) if phase else self._next_phase(record.phase)

        if target == MissionPhase.SIMULATE:
            result = await self._phase_simulate(record)
        elif target == MissionPhase.VALIDATE:
            result = await self._phase_validate(record)
        elif target == MissionPhase.APPROVE:
            result = await self._phase_approve(record, operator)
        elif target == MissionPhase.UPLOAD:
            result = await self._phase_upload(record)
        elif target == MissionPhase.EXECUTE:
            result = await self._phase_execute(record)
        elif target == MissionPhase.MONITOR:
            result = await self._phase_monitor(record)
        elif target == MissionPhase.LEARN:
            result = await self._phase_learn(record)
        else:
            return {"success": False, "error": f"unsupported_phase:{target.value}"}

        if result.get("success") is False and target in (MissionPhase.UPLOAD, MissionPhase.EXECUTE):
            return {"success": False, "mission": record.to_dict(), "phase_result": result}

        record.phase = target
        self._audit(record, f"phase_{target.value}", result if isinstance(result, dict) else {"ok": True})
        return {"success": True, "mission": record.to_dict(), "phase_result": result}

    def _next_phase(self, current: MissionPhase) -> MissionPhase:
        try:
            i = PHASE_ORDER.index(current)
            return PHASE_ORDER[min(i + 1, len(PHASE_ORDER) - 1)]
        except ValueError:
            return MissionPhase.SIMULATE

    async def _get_snapshot(self) -> Dict[str, Any]:
        if self._snapshot_provider:
            return await self._snapshot_provider()
        return await self.kernel.process(
            {"physics": {"battery": 80}, "ekf": {"confidence": 0.9}, "risk": {"value": 0.2}}
        )

    async def _phase_simulate(self, record: MissionLifecycleRecord) -> Dict[str, Any]:
        snap = await self._get_snapshot()
        snap["mission_intent"] = record.intent
        forecast = self.world_model.simulate(snap)
        record.simulation = forecast.to_dict()
        return {"forecast": record.simulation}

    async def _phase_validate(self, record: MissionLifecycleRecord) -> Dict[str, Any]:
        plan = record.plan or {}
        max_risk = float(plan.get("max_risk", 0.5))
        sim = record.simulation or {}
        surv = float(sim.get("mission_survivability_forecast", 0.5))
        landing = float(sim.get("landing_success_forecast", 0.8))
        passed = max_risk <= 0.6 and surv >= 0.4 and landing >= 0.5
        record.validation = {
            "passed": passed,
            "max_risk": max_risk,
            "survivability_forecast": surv,
            "landing_forecast": landing,
            "blockers": [] if passed else ["risk_or_survivability_gate"],
        }
        return record.validation

    async def _phase_approve(self, record: MissionLifecycleRecord, operator: str) -> Dict[str, Any]:
        if not record.validation or not record.validation.get("passed"):
            return {"approved": False, "reason": "validation_failed"}
        record.approved_by = operator
        record.approved_at = time.time()
        evidence = self.kernel.evidence_dag.record_event(
            "mission_approved",
            {"mission_id": record.mission_id, "operator": operator, "intent": record.intent},
        )
        record.evidence_ids.append(evidence["node_id"])
        return {"approved": True, "operator": operator, "evidence": evidence}

    async def _phase_upload(self, record: MissionLifecycleRecord) -> Dict[str, Any]:
        if not record.approved_at:
            return {"success": False, "reason": "not_approved"}
        wps = (record.plan or {}).get("waypoints", [])
        result = await self.flight_stack.upload_mission(wps)
        record.upload_result = result
        return result

    async def _phase_execute(self, record: MissionLifecycleRecord) -> Dict[str, Any]:
        if not record.upload_result or not record.upload_result.get("success"):
            return {"success": False, "reason": "upload_required"}
        record.execution_result = {"status": "active", "monitor_via": "/ws/v1/stream"}
        return record.execution_result

    async def _phase_monitor(self, record: MissionLifecycleRecord) -> Dict[str, Any]:
        tel = await self.flight_stack.get_live_telemetry()
        return {"telemetry": tel, "phase": "monitor"}

    async def _phase_learn(self, record: MissionLifecycleRecord) -> Dict[str, Any]:
        self.kernel.lake.ingest_cycle(
            {"mission_id": record.mission_id, "intent": record.intent, "learn": True},
            self.uav_id,
        )
        return {"learned": True, "mission_id": record.mission_id}
