"""Adversarial operational resilience — deception detection, mission hardening."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("adversarial_ops")


@dataclass
class AdversarialOpsState:
    deception_detected: bool
    deception_type: Optional[str]
    mission_hardening_level: str
    threat_propagation: List[str]
    isolation_channels: List[str]
    hardened_continuity: float

    def to_dict(self) -> Dict:
        return self.__dict__


class AdversarialOperationalResilience:
    """
    Contested-environment ops layer atop CyberWarfareResilienceEngine.
    GPS spoof, RF, MAVLink, telemetry hijack, environmental deception.
    """

    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self._deception_log: List[Dict] = []
        self._hardening_level = "standard"

    def assess(
        self,
        snapshot: Dict[str, Any],
        cyber_warfare: Optional[Dict] = None,
        cyber_fleet: Optional[Dict] = None,
    ) -> AdversarialOpsState:
        cyber = snapshot.get("cybersecurity", {}) or {}
        trust = snapshot.get("sensor_trust", {}) or {}
        cw = cyber_warfare or {}

        deception = False
        dtype = None

        gps_jump = float(trust.get("gps_confidence", 1)) < 0.2 and not cyber.get("is_spoofed")
        if gps_jump:
            deception = True
            dtype = "environmental_gps_deception"

        innov = float(snapshot.get("ekf", {}).get("innovation_mag", 0))
        if innov > 2.0 and float(trust.get("fusion_confidence", 1)) > 0.8:
            deception = True
            dtype = dtype or "telemetry_inconsistency"

        attacks = cw.get("attacks", [])
        if len(attacks) >= 2:
            self._hardening_level = "maximum"
        elif len(attacks) == 1:
            self._hardening_level = "elevated"
        else:
            self._hardening_level = "standard"

        propagation = []
        if isinstance(cyber_fleet, dict):
            for a in cyber_fleet.get("actions", [])[:3]:
                propagation.append(str(a))

        isolation = list(cw.get("quarantined_channels", []))
        continuity = float(cw.get("mission_continuity", 1.0))
        if deception:
            continuity *= 0.85
            self._deception_log.append({"type": dtype, "ts": time.time()})

        if self._hardening_level == "maximum":
            continuity = max(0.55, continuity)

        return AdversarialOpsState(
            deception_detected=deception,
            deception_type=dtype,
            mission_hardening_level=self._hardening_level,
            threat_propagation=propagation,
            isolation_channels=isolation,
            hardened_continuity=continuity,
        )
