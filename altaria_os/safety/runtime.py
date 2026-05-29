"""
Safety-Critical Runtime — watchdog, kill-switch, audit trail, deterministic state machine.
Every AI decision: replayable, explainable, auditable.
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("safety.runtime")


class SafetyState(str, Enum):
    NOMINAL = "NOMINAL"
    DEGRADED = "DEGRADED"
    RECOVERY = "RECOVERY"
    EMERGENCY = "EMERGENCY"
    KILLED = "KILLED"


@dataclass
class AuditRecord:
    record_id: str
    timestamp: float
    cycle: int
    decision: str
    override: bool
    risk_value: float
    survival_strategy: str
    confidence_uncertainty: float
    explainability_hash: str
    sensor_trust_snapshot: Dict[str, Any]
    full_snapshot_ref: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "cycle": self.cycle,
            "decision": self.decision,
            "override": self.override,
            "risk_value": self.risk_value,
            "survival_strategy": self.survival_strategy,
            "confidence_uncertainty": self.confidence_uncertainty,
            "explainability_hash": self.explainability_hash,
        }


class SafetyCriticalRuntime:
    """Independent failsafe layer — can veto AI commands."""

    WATCHDOG_TIMEOUT_S = 2.0
    MAX_RISK_WITHOUT_OVERRIDE = 0.95

    def __init__(self):
        self._state = SafetyState.NOMINAL
        self._kill_switch = False
        self._last_heartbeat = time.time()
        self._audit_trail: List[AuditRecord] = []
        self._veto_count = 0

    def heartbeat(self):
        self._last_heartbeat = time.time()

    def check_watchdog(self) -> bool:
        if time.time() - self._last_heartbeat > self.WATCHDOG_TIMEOUT_S:
            logger.critical("WATCHDOG TIMEOUT — escalating to EMERGENCY")
            self._state = SafetyState.EMERGENCY
            return False
        return True

    def engage_kill_switch(self, reason: str = "operator"):
        self._kill_switch = True
        self._state = SafetyState.KILLED
        logger.critical("KILL SWITCH: %s", reason)

    def release_kill_switch(self):
        self._kill_switch = False
        self._state = SafetyState.DEGRADED

    def veto_command(self, command: str, risk: float, uncertainty: float) -> bool:
        """Returns True if command VETOED."""
        if self._kill_switch:
            self._veto_count += 1
            return True
        if not self.check_watchdog():
            return command not in ("EMERGENCY_LAND", "LAND", "RTL")
        if uncertainty > 0.85 and command == "NONE" and risk > 0.7:
            return False  # allow escalation
        if risk > self.MAX_RISK_WITHOUT_OVERRIDE and command == "NONE":
            self._veto_count += 1
            return True
        return False

    def audit_cycle(self, snapshot: Dict[str, Any]) -> AuditRecord:
        expl = snapshot.get("explainability", {})
        rec = AuditRecord(
            record_id=str(uuid.uuid4()),
            timestamp=snapshot.get("timestamp", time.time()),
            cycle=int(snapshot.get("cycle", 0)),
            decision=snapshot.get("decision", {}).get("action", "NONE"),
            override=bool(snapshot.get("decision", {}).get("os_override", False)),
            risk_value=float(snapshot.get("risk", {}).get("value", 0)),
            survival_strategy=snapshot.get("survival", {}).get("strategy", ""),
            confidence_uncertainty=float(snapshot.get("confidence", {}).get("global_uncertainty", 0)),
            explainability_hash=str(hash(expl.get("root_cause", "")))[:12],
            sensor_trust_snapshot=snapshot.get("sensor_trust", {}),
        )
        self._audit_trail.append(rec)
        if len(self._audit_trail) > 10_000:
            self._audit_trail = self._audit_trail[-5000:]
        return rec

    def transition(self, new_state: SafetyState):
        logger.info("Safety state: %s → %s", self._state.value, new_state.value)
        self._state = new_state

    def get_status(self) -> Dict[str, Any]:
        return {
            "state": self._state.value,
            "kill_switch": self._kill_switch,
            "watchdog_ok": self.check_watchdog(),
            "audit_records": len(self._audit_trail),
            "vetoes": self._veto_count,
        }

    def get_audit_trail(self, limit: int = 100) -> List[Dict]:
        return [r.to_dict() for r in self._audit_trail[-limit:]]
