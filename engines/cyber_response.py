"""Autonomous cyber defense — detect, isolate, rotate trust, switch nav, fleet alert."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("cyber_response")


@dataclass
class CyberResponseAction:
    action: str
    severity: str
    description: str
    nav_mode_switch: Optional[str] = None
    quarantine_channel: Optional[str] = None
    fleet_alert: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "severity": self.severity,
            "description": self.description,
            "nav_mode_switch": self.nav_mode_switch,
            "quarantine_channel": self.quarantine_channel,
            "fleet_alert": self.fleet_alert,
        }


class AutonomousCyberResponseEngine:
    """
    Beyond detection — autonomous preservation under attack.
    """

    def __init__(self):
        self._trust_anchor_version = 1
        self._quarantined_channels: List[str] = []
        self._attack_history: List[Dict] = []

    def respond(self, cyber: Dict[str, Any], sensor_trust: Dict[str, Any]) -> List[CyberResponseAction]:
        actions: List[CyberResponseAction] = []
        threat = float(cyber.get("threat_level", 0))
        spoofed = bool(cyber.get("is_spoofed", False))
        blocks = int(cyber.get("firewall_blocks", 0))

        if spoofed:
            actions.append(CyberResponseAction(
                action="ISOLATE_GPS",
                severity="CRITICAL",
                description="GPS spoof detected — quarantine GPS channel, switch to VIO",
                nav_mode_switch="vio",
                quarantine_channel="gps",
                fleet_alert=True,
            ))
            self._quarantined_channels.append("gps")
            self._rotate_trust_anchor()

        if threat > 0.7:
            actions.append(CyberResponseAction(
                action="QUARANTINE_TELEMETRY",
                severity="HIGH",
                description="Telemetry hijack suspected — signed-only commands",
                quarantine_channel="telemetry_rx",
                fleet_alert=True,
            ))

        if blocks > 5:
            actions.append(CyberResponseAction(
                action="RATE_LIMIT_COMMANDS",
                severity="HIGH",
                description="MAVLink injection pattern — strict firewall",
            ))

        if threat > 0.5 and float(sensor_trust.get("fusion_confidence", 1)) < 0.5:
            actions.append(CyberResponseAction(
                action="DEGRADED_AUTONOMY",
                severity="MEDIUM",
                description="Reduce aggression, widen safety margins",
                nav_mode_switch="inertial",
            ))

        for a in actions:
            self._attack_history.append({"ts": time.time(), **a.to_dict()})
        return actions

    def _rotate_trust_anchor(self):
        self._trust_anchor_version += 1
        logger.warning("Trust anchor rotated to v%d", self._trust_anchor_version)

    def get_status(self) -> Dict[str, Any]:
        return {
            "trust_anchor_version": self._trust_anchor_version,
            "quarantined": self._quarantined_channels,
            "recent_attacks": len(self._attack_history),
        }
