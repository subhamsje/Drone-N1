"""Autonomous flight operations intelligence — missions, replay, field telemetry."""

import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("flight_ops")


class MissionPhase(str, Enum):
    PREFLIGHT = "PREFLIGHT"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    RECOVERY = "RECOVERY"
    COMPLETE = "COMPLETE"
    ABORTED = "ABORTED"


@dataclass
class OperationalMission:
    mission_id: str
    intent: str
    phase: MissionPhase
    started_at: float
    cycles_completed: int = 0
    anomalies: int = 0
    recoveries: int = 0
    environmental_adaptation_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "intent": self.intent,
            "phase": self.phase.value,
            "cycles_completed": self.cycles_completed,
            "anomalies": self.anomalies,
            "recoveries": self.recoveries,
            "environmental_adaptation_score": round(self.environmental_adaptation_score, 4),
            "duration_s": round(time.time() - self.started_at, 1),
        }


class FlightOperationsOrchestrator:
    """Continuous autonomous mission operations with replay and field analytics."""

    def __init__(self, uav_id: str, fleet_id: str):
        self.uav_id = uav_id
        self.fleet_id = fleet_id
        self._active: Optional[OperationalMission] = None
        self._replay_buffer: List[Dict] = []
        self._field_archive: List[Dict] = []
        self._survivability_scores: List[float] = []

    def start_mission(self, intent: str) -> OperationalMission:
        self._active = OperationalMission(
            mission_id=str(uuid.uuid4())[:8],
            intent=intent,
            phase=MissionPhase.ACTIVE,
            started_at=time.time(),
        )
        return self._active

    def ingest_cycle(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        if not self._active:
            self.start_mission(snapshot.get("mission_intent", "autonomous_patrol"))

        m = self._active
        m.cycles_completed += 1
        surv = float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.5))
        self._survivability_scores.append(surv)

        if snapshot.get("anomaly", {}).get("is_anomaly"):
            m.anomalies += 1
        if snapshot.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"):
            m.recoveries += 1
            m.phase = MissionPhase.RECOVERY
        elif snapshot.get("confidence", {}).get("degraded_mode") != "NOMINAL":
            m.phase = MissionPhase.DEGRADED
        else:
            m.phase = MissionPhase.ACTIVE

        # Environmental adaptation from twin physics + route
        turb = float(snapshot.get("twin_physics", {}).get("turbulence_index", 0))
        m.environmental_adaptation_score = max(0.2, 1.0 - turb * 0.5)

        frame = {"ts": time.time(), "cycle": snapshot.get("cycle"), "snapshot_ref": snapshot.get("safety_audit_id")}
        self._replay_buffer.append(frame)
        if len(self._replay_buffer) > 5000:
            self._replay_buffer = self._replay_buffer[-2500:]

        return self.get_operational_metrics()

    def get_operational_metrics(self) -> Dict[str, Any]:
        m = self._active
        if not m:
            return {"status": "idle"}
        scores = self._survivability_scores[-100:]
        mean_surv = sum(scores) / len(scores) if scores else 0
        return {
            "mission": m.to_dict(),
            "crash_prevention_estimate": round(mean_surv * 0.9, 4),
            "mission_continuity_score": round(mean_surv, 4),
            "recovery_rate": m.recoveries / max(1, m.cycles_completed),
            "environmental_adaptation": m.environmental_adaptation_score,
        }

    def complete_mission(self) -> Dict:
        if self._active:
            self._active.phase = MissionPhase.COMPLETE
            summary = self._active.to_dict()
            self._field_archive.append(summary)
            self._active = None
            return summary
        return {}

    def replay_mission(self, start_ts: float, end_ts: float) -> List[Dict]:
        return [f for f in self._replay_buffer if start_ts <= f["ts"] <= end_ts]
