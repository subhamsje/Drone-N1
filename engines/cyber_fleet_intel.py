"""Distributed cyber threat intelligence — fleet-wide containment propagation."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

logger = logging.getLogger("cyber_fleet_intel")


@dataclass
class FleetThreatAlert:
    threat_id: str
    threat_type: str
    severity: float
    source_uav: str
    timestamp: float
    containment_actions: List[str]
    affected_region: str = "local"

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class DistributedCyberIntelligence:
    """Fleet-wide cyber alert propagation and autonomous containment policies."""

    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self._active_alerts: List[FleetThreatAlert] = []
        self._containment_policy = {
            "gps_spoofing": ["ISOLATE_GPS", "FLEET_VIO_MODE", "TRUST_ROTATE"],
            "mavlink_injection": ["QUARANTINE_RX", "SIGNED_ONLY"],
            "rf_jamming": ["DEGRADED_AUTONOMY", "RTL_BIAS"],
        }

    def process_local(self, uav_id: str, cyber_response: List[Dict]) -> List[FleetThreatAlert]:
        new_alerts = []
        for action in cyber_response:
            atype = action.get("action", "").lower()
            if "spoof" in atype or "gps" in atype:
                ttype = "gps_spoofing"
            elif "quarantine" in atype:
                ttype = "mavlink_injection"
            elif "degraded" in atype:
                ttype = "rf_jamming"
            else:
                continue
            alert = FleetThreatAlert(
                threat_id=f"{self.fleet_id}-{int(time.time())}",
                threat_type=ttype,
                severity=0.8 if action.get("severity") == "CRITICAL" else 0.6,
                source_uav=uav_id,
                timestamp=time.time(),
                containment_actions=self._containment_policy.get(ttype, []),
            )
            self._active_alerts.append(alert)
            new_alerts.append(alert)
        self._expire()
        return new_alerts

    def get_fleet_containment_directive(self) -> Dict[str, Any]:
        if not self._active_alerts:
            return {"active": False}
        worst = max(self._active_alerts, key=lambda a: a.severity)
        return {
            "active": True,
            "threat_type": worst.threat_type,
            "severity": worst.severity,
            "actions": worst.containment_actions,
            "alert_count": len(self._active_alerts),
        }

    def _expire(self, ttl_s: float = 300):
        now = time.time()
        self._active_alerts = [a for a in self._active_alerts if now - a.timestamp < ttl_s]
