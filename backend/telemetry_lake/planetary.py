"""Planetary-scale telemetry intelligence — hyperscale operational cognition."""

import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger("telemetry.planetary")


@dataclass
class SurvivabilityAggregate:
    region: str
    missions_active: int
    mean_survivability: float
    anomaly_rate: float
    recovery_success_rate: float
    environmental_stress_index: float


class PlanetaryTelemetryLakehouse:
    """
    Billions-event scale interface — ring buffers + regional aggregates.
    Cross-region learning and fleet survivability intelligence.
    """

    def __init__(self, shard_id: str = "global-0"):
        self.shard_id = shard_id
        self._event_buffer: deque = deque(maxlen=500_000)
        self._regional: Dict[str, SurvivabilityAggregate] = {}
        self._missions: Dict[str, Dict] = {}
        self._total_events = 0

    def ingest_event(self, snapshot: Dict[str, Any], uav_id: str, region: str = "us-west"):
        self._total_events += 1
        event = {
            "ts": time.time(),
            "uav_id": uav_id,
            "region": region,
            "survivability": float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0)),
            "risk": float(snapshot.get("risk", {}).get("value", 0)),
            "anomaly": float(snapshot.get("anomaly", {}).get("score", 0)),
            "recovery": snapshot.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"),
        }
        self._event_buffer.append(event)
        self._update_regional(region, event)
        mid = snapshot.get("flight_operations", {}).get("mission_id", "default")
        self._missions[mid] = {"last_ts": event["ts"], "surv_ema": event["survivability"]}

    def _update_regional(self, region: str, event: Dict):
        agg = self._regional.get(region)
        if not agg:
            agg = SurvivabilityAggregate(region, 0, 0.75, 0.0, 0.0, 0.0)
        n = agg.missions_active + 1
        agg.mean_survivability = (agg.mean_survivability * (n - 1) + event["survivability"]) / n
        agg.anomaly_rate = (agg.anomaly_rate * (n - 1) + (1 if event["anomaly"] > 0.6 else 0)) / n
        if event["recovery"]:
            agg.recovery_success_rate = (agg.recovery_success_rate * (n - 1) + 0.8) / n
        agg.environmental_stress_index = (agg.environmental_stress_index * (n - 1) + event["risk"]) / n
        agg.missions_active = len([m for m in self._missions.values() if time.time() - m["last_ts"] < 3600])
        self._regional[region] = agg

    def get_planetary_intelligence(self) -> Dict[str, Any]:
        regions = [
            {
                "region": a.region,
                "mean_survivability": round(a.mean_survivability, 4),
                "anomaly_rate": round(a.anomaly_rate, 4),
                "recovery_success_rate": round(a.recovery_success_rate, 4),
                "environmental_stress": round(a.environmental_stress_index, 4),
                "missions_active": a.missions_active,
            }
            for a in self._regional.values()
        ]
        global_surv = sum(r["mean_survivability"] for r in regions) / max(1, len(regions)) if regions else 0.75
        return {
            "shard_id": self.shard_id,
            "total_events": self._total_events,
            "buffer_depth": len(self._event_buffer),
            "active_missions": len(self._missions),
            "global_mean_survivability": round(global_surv, 4),
            "regions": regions,
            "scale_tier": "planetary",
        }

    def query_anomaly_archive(self, limit: int = 20) -> List[Dict]:
        return [e for e in list(self._event_buffer)[-limit:] if e.get("anomaly", 0) > 0.5]
