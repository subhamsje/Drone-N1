"""Mixed-criticality runtime — deterministic isolation of survival vs analytics."""

import logging
import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("rt.mixed_criticality")


class CriticalityDomain(IntEnum):
    FLIGHT_STABILIZATION = 0
    COLLISION_AVOIDANCE = 1
    SURVIVAL = 2
    COGNITION = 3
    PERCEPTION = 4
    ANALYTICS = 5
    TELEMETRY = 6
    PERSISTENCE = 7


DOMAIN_BUDGET_MS = {
    CriticalityDomain.FLIGHT_STABILIZATION: 8.0,
    CriticalityDomain.COLLISION_AVOIDANCE: 10.0,
    CriticalityDomain.SURVIVAL: 12.0,
    CriticalityDomain.COGNITION: 15.0,
    CriticalityDomain.PERCEPTION: 12.0,
    CriticalityDomain.ANALYTICS: 200.0,
    CriticalityDomain.TELEMETRY: 100.0,
    CriticalityDomain.PERSISTENCE: 150.0,
}


@dataclass
class DomainExecutionRecord:
    domain: str
    latency_ms: float
    budget_ms: float
    met_budget: bool

    def to_dict(self) -> Dict:
        return {
            "domain": self.domain,
            "latency_ms": round(self.latency_ms, 2),
            "budget_ms": self.budget_ms,
            "met_budget": self.met_budget,
        }


class MixedCriticalityRuntime:
    """
    Survival domains always preempt analytics/telemetry/persistence.
    Total critical band budget: 50ms (flight + collision + survival + cognition core).
    """

    CRITICAL_BAND_MS = 50.0

    def __init__(self):
        self._records: List[DomainExecutionRecord] = []
        self._cycle_critical_ms = 0.0
        self._preemptions = 0

    def begin_cycle(self):
        self._cycle_critical_ms = 0.0
        self._records = []

    def record_domain(self, domain: CriticalityDomain, latency_ms: float) -> bool:
        budget = DOMAIN_BUDGET_MS[domain]
        met = latency_ms <= budget
        self._records.append(DomainExecutionRecord(domain.name, latency_ms, budget, met))

        if domain.value <= CriticalityDomain.COGNITION.value:
            self._cycle_critical_ms += latency_ms

        if self._cycle_critical_ms > self.CRITICAL_BAND_MS and domain.value > CriticalityDomain.SURVIVAL.value:
            self._preemptions += 1
            return False  # defer lower priority
        return True

    def should_defer_non_critical(self) -> bool:
        return self._cycle_critical_ms >= self.CRITICAL_BAND_MS

    def escalate_emergency(self, reason: str) -> Dict[str, Any]:
        """Survival-priority emergency — blocks analytics/telemetry/persistence."""
        self._preemptions += 1
        return {"escalated": True, "reason": reason, "only_critical": True}

    def finalize_cycle(self, emergency: bool = False) -> Dict[str, Any]:
        deferred = self.should_defer_non_critical() or emergency
        return {
            "critical_band_ms": round(self._cycle_critical_ms, 2),
            "critical_band_met": self._cycle_critical_ms <= self.CRITICAL_BAND_MS,
            "domains": [r.to_dict() for r in self._records],
            "defer_analytics": deferred,
            "defer_telemetry": deferred,
            "defer_persistence": deferred,
            "preemptions": self._preemptions,
            "emergency_escalation": emergency,
            "isolation": "mixed_criticality_v7",
        }
