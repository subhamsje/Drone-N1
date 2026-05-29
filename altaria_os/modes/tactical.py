"""Tactical modes — disaster response and defense contested-environment cognition."""

import logging
from typing import Any, Dict

from altaria_os.modes.industry import IndustryMode, IndustryModeController

logger = logging.getLogger("tactical_modes")


class DisasterResponseCognition:
    """Wildfire, SAR, medical delivery, relay networking."""

    def apply(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        snapshot["tactical_mode"] = "DISASTER_RESPONSE"
        # Thermal priority, low-connectivity tolerance
        if "perception_health" in snapshot:
            snapshot["perception_health"]["active_pipeline"] = "thermal_primary"
        snapshot["mission_priority"] = "human_safety"
        if snapshot.get("multimodal_perception", {}).get("weather_degraded"):
            snapshot["survival"] = snapshot.get("survival", {})
            snapshot["survival"]["urgency"] = max(
                snapshot["survival"].get("urgency", "NORMAL"),
                "ELEVATED" if snapshot.get("risk", {}).get("value", 0) > 0.4 else "NORMAL",
            )
        return snapshot


class DefenseModeCognition:
    """GPS-denied, RF-resilient, evasive, contested navigation."""

    def apply(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        snapshot["tactical_mode"] = "DEFENSE"
        nav = snapshot.setdefault("navigation_state", {})
        if float(snapshot.get("sensor_trust", {}).get("gps_confidence", 1)) < 0.5:
            nav["mode"] = "vio"
        # Threat-priority routing
        if float(snapshot.get("cyber_warfare", {}).get("mission_continuity", 1)) < 0.7:
            rg = snapshot.setdefault("route_governance", {})
            rg["reroute_required"] = True
            snapshot["cognition"] = snapshot.get("cognition", {})
            snapshot["cognition"]["aggression_mode"] = "SURVIVAL"
        # Evasive bias
        air = snapshot.get("airspace", {})
        if air.get("conflict_risk", 0) > 0.4:
            snapshot["defense_evasive"] = True
        return snapshot


class TacticalModeOrchestrator:
    def __init__(self):
        self.industry = IndustryModeController()
        self.disaster = DisasterResponseCognition()
        self.defense = DefenseModeCognition()

    def apply(self, snapshot: Dict[str, Any], mode: str) -> Dict[str, Any]:
        if mode == "DISASTER_RESPONSE":
            self.industry.set_mode(IndustryMode.DISASTER_RESPONSE)
            snapshot = self.industry.apply_to_snapshot(snapshot)
            return self.disaster.apply(snapshot)
        if mode == "DEFENSE":
            self.industry.set_mode(IndustryMode.DEFENSE)
            snapshot = self.industry.apply_to_snapshot(snapshot)
            return self.defense.apply(snapshot)
        return self.industry.apply_to_snapshot(snapshot)
