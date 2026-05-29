"""
Distributed Fleet Learning — cross-drone threat propagation and shared map intelligence.
"""

import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from core.cognitive_models import FleetIntelligenceState

logger = logging.getLogger("fleet_learning")


@dataclass
class SharedThreat:
    threat_type: str
    location: tuple
    severity: float
    source_uav: str
    timestamp: float
    ttl_s: float = 300.0


class FleetLearningEngine:
    """
    If one drone learns dangerous wind, spoofing, or RF interference —
    entire fleet updates instantly.
    """

    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self._threats: List[SharedThreat] = []
        self._learned_zones: List[Dict[str, Any]] = []
        self._map_version = "v1"
        self._anomaly_count = 0

    def ingest_local_observation(self, uav_id: str, snapshot: Dict[str, Any]) -> FleetIntelligenceState:
        now = time.time()
        cyber = snapshot.get("cybersecurity", {}) or {}
        nav = snapshot.get("navigation", {}) or {}
        risk = float(snapshot.get("risk", {}).get("value", 0))

        if cyber.get("is_spoofed"):
            self._add_threat("gps_spoofing", (0, 0), 0.9, uav_id, now)
        if float(nav.get("weather_hazard", 0)) > 0.75:
            self._add_threat("dangerous_wind", (nav.get("landing_x", 0), nav.get("landing_y", 0)), 0.7, uav_id, now)
        if float(cyber.get("threat_level", 0)) > 0.6:
            self._add_threat("rf_interference", (0, 0), cyber["threat_level"], uav_id, now)
        if snapshot.get("anomaly", {}).get("is_anomaly"):
            self._anomaly_count += 1

        self._expire_threats(now)
        return FleetIntelligenceState(
            shared_threats=[t.threat_type for t in self._threats],
            learned_zones=[{"type": t.threat_type, "severity": t.severity} for t in self._threats[-10:]],
            cross_drone_anomalies=self._anomaly_count,
            map_version=self._map_version,
        )

    def _add_threat(self, ttype: str, loc: tuple, severity: float, source: str, ts: float):
        self._threats.append(SharedThreat(ttype, loc, severity, source, ts))
        self._learned_zones.append({
            "type": ttype, "location": loc, "severity": severity, "learned_at": ts,
        })
        self._map_version = f"v{len(self._learned_zones)}"

    def _expire_threats(self, now: float):
        self._threats = [t for t in self._threats if now - t.timestamp < t.ttl_s]

    def get_fleet_risk_boost(self) -> float:
        if not self._threats:
            return 0.0
        return min(0.25, max(t.severity for t in self._threats) * 0.2)
