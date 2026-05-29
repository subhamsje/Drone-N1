"""Operational intelligence — ROI, survivability scoring, fleet uptime, insurance risk."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np

logger = logging.getLogger("operations.intelligence")


@dataclass
class OperationalMetrics:
    crash_prevention_score: float
    survivability_index: float
    fleet_uptime_pct: float
    recovery_success_rate: float
    mean_mission_continuity: float
    insurance_risk_reduction: float
    estimated_cost_avoidance_usd: float

    def to_dict(self) -> Dict[str, Any]:
        return {k: (round(v, 2) if isinstance(v, float) and "usd" in k else round(v, 4) if isinstance(v, float) else v)
                for k, v in self.__dict__.items()}


class OperationalIntelligencePlatform:
    """
    Measurable economic value from autonomous resilience.
    """

    def __init__(self, fleet_id: str, aircraft_value_usd: float = 15000.0):
        self.fleet_id = fleet_id
        self.aircraft_value = aircraft_value_usd
        self._cycles: List[Dict] = []
        self._recoveries = 0
        self._crashes_prevented = 0

    def record_cycle(self, snapshot: Dict[str, Any]):
        prob = snapshot.get("probabilistic_safety", {})
        self._cycles.append({
            "ts": time.time(),
            "surv": float(prob.get("composite_survivability", 0)),
            "crash_p": float(snapshot.get("inference", {}).get("crash_probability", 0)),
            "recovery": snapshot.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"),
        })
        if self._cycles[-1]["recovery"]:
            self._recoveries += 1
        if self._cycles[-1]["crash_p"] > 0.7 and self._cycles[-1]["recovery"]:
            self._crashes_prevented += 1
        if len(self._cycles) > 50_000:
            self._cycles = self._cycles[-25_000:]

    def compute_metrics(self, fleet_size: int = 4) -> OperationalMetrics:
        if not self._cycles:
            return OperationalMetrics(0, 0, 100, 0, 0, 0, 0)
        surv = [c["surv"] for c in self._cycles]
        crash_ps = [c["crash_p"] for c in self._cycles]
        recoveries = sum(1 for c in self._cycles if c["recovery"])

        mean_surv = float(np.mean(surv))
        mean_crash = float(np.mean(crash_ps))
        prevention = float(np.clip(1.0 - mean_crash + self._crashes_prevented / max(1, len(self._cycles)), 0, 1))
        recovery_rate = recoveries / max(1, len(self._cycles))
        continuity = mean_surv * 0.85 + recovery_rate * 0.15
        insurance_reduction = prevention * 0.4 + recovery_rate * 0.3
        cost_avoidance = self._crashes_prevented * self.aircraft_value * 0.7

        return OperationalMetrics(
            crash_prevention_score=prevention,
            survivability_index=mean_surv,
            fleet_uptime_pct=min(100, 95 + mean_surv * 5),
            recovery_success_rate=recovery_rate,
            mean_mission_continuity=continuity,
            insurance_risk_reduction=insurance_reduction,
            estimated_cost_avoidance_usd=cost_avoidance,
        )
