"""Operational analytics — flight hours, survivability, fleet readiness."""

import time
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class FleetAnalyticsSnapshot:
    fleet_id: str
    active_missions: int = 0
    total_flight_hours: float = 0.0
    failure_rate: float = 0.0
    mean_survivability: float = 0.0
    fleet_readiness: float = 0.0
    missions_completed_24h: int = 0
    recovery_events_24h: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fleet_id": self.fleet_id,
            "active_missions": self.active_missions,
            "total_flight_hours": round(self.total_flight_hours, 2),
            "failure_rate": round(self.failure_rate, 4),
            "mean_survivability": round(self.mean_survivability, 4),
            "fleet_readiness": round(self.fleet_readiness, 4),
            "missions_completed_24h": self.missions_completed_24h,
            "recovery_events_24h": self.recovery_events_24h,
            "timestamp": time.time(),
        }


class OperationalAnalytics:
    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self._surv_samples: List[float] = []
        self._failures = 0
        self._cycles = 0
        self._recoveries = 0

    def ingest_snapshot(self, snapshot: Dict[str, Any]):
        self._cycles += 1
        surv = float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.5))
        self._surv_samples.append(surv)
        if len(self._surv_samples) > 5000:
            self._surv_samples = self._surv_samples[-2500:]
        if snapshot.get("anomaly", {}).get("is_anomaly"):
            self._failures += 1
        if snapshot.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"):
            self._recoveries += 1

    def snapshot(self, active_missions: int = 0) -> FleetAnalyticsSnapshot:
        scores = self._surv_samples[-200:] or [0.5]
        mean_s = sum(scores) / len(scores)
        fail_rate = self._failures / max(1, self._cycles)
        hours = self._cycles * 0.2 / 3600.0  # ~200ms per cycle
        readiness = max(0.0, min(1.0, mean_s * (1.0 - fail_rate)))
        return FleetAnalyticsSnapshot(
            fleet_id=self.fleet_id,
            active_missions=active_missions,
            total_flight_hours=hours,
            failure_rate=fail_rate,
            mean_survivability=mean_s,
            fleet_readiness=readiness,
            recovery_events_24h=self._recoveries,
        )
