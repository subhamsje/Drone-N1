"""Autonomous cyber warfare resilience — contested environment survivability."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("cyber_warfare")


@dataclass
class AttackAssessment:
    attack_type: str
    confidence: float
    severity: str
    containment_active: bool
    mission_continuity: float


class CyberWarfareResilienceEngine:
    """
    Aerospace-grade adversarial survivability.
    Isolates telemetry, rotates trust, maintains mission under RF/GPS/MAVLink attacks.
    """

    ATTACK_SIGNATURES = {
        "gps_spoof": lambda s: bool(s.get("cybersecurity", {}).get("is_spoofed")),
        "mavlink_injection": lambda s: int(s.get("cybersecurity", {}).get("firewall_blocks", 0)) > 3,
        "rf_jamming": lambda s: float(s.get("cybersecurity", {}).get("threat_level", 0)) > 0.65,
        "telemetry_hijack": lambda s: float(s.get("sensor_trust", {}).get("fusion_confidence", 1)) < 0.4,
    }

    def __init__(self):
        self._trust_generation = 1
        self._quarantine_active: List[str] = []
        self._attack_log: List[Dict] = []
        self._mission_continuity = 1.0

    def assess_and_contain(self, snapshot: Dict[str, Any]) -> List[AttackAssessment]:
        assessments = []
        for atype, detector in self.ATTACK_SIGNATURES.items():
            if detector(snapshot):
                conf = 0.85 if atype == "gps_spoof" else 0.7
                sev = "CRITICAL" if atype in ("gps_spoof", "mavlink_injection") else "HIGH"
                self._apply_containment(atype)
                mc = max(0.3, 1.0 - conf * 0.5)
                self._mission_continuity = min(self._mission_continuity, mc)
                assessments.append(AttackAssessment(atype, conf, sev, True, mc))
                self._attack_log.append({"ts": time.time(), "type": atype, "conf": conf})

        if not assessments:
            self._mission_continuity = min(1.0, self._mission_continuity + 0.01)

        return assessments

    def _apply_containment(self, attack_type: str):
        actions = {
            "gps_spoof": ["gps_rx"],
            "mavlink_injection": ["mavlink_rx"],
            "rf_jamming": ["rf_primary"],
            "telemetry_hijack": ["telemetry_stream"],
        }
        for ch in actions.get(attack_type, []):
            if ch not in self._quarantine_active:
                self._quarantine_active.append(ch)
        self._trust_generation += 1

    def get_resilience_state(self) -> Dict[str, Any]:
        return {
            "trust_generation": self._trust_generation,
            "quarantined_channels": self._quarantine_active,
            "mission_continuity": round(self._mission_continuity, 4),
            "recent_attacks": len(self._attack_log),
            "contested_mode": self._mission_continuity < 0.7,
        }
