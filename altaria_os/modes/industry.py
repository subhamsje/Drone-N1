"""Industry deployment modes — Defense, Logistics, Disaster, Inspection."""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger("industry_modes")


class IndustryMode(str, Enum):
    STANDARD = "STANDARD"
    DEFENSE = "DEFENSE"
    LOGISTICS = "LOGISTICS"
    DISASTER_RESPONSE = "DISASTER_RESPONSE"
    INDUSTRIAL_INSPECTION = "INDUSTRIAL_INSPECTION"


@dataclass
class ModeProfile:
    mode: IndustryMode
    gps_denied_priority: bool
    payload_preservation: float
    urban_routing: bool
    thermal_required: bool
    rf_resilience: float
    search_pattern: bool
    precision_hover: bool
    max_aggression_cap: float
    survival_bias: float


MODE_PROFILES = {
    IndustryMode.STANDARD: ModeProfile(
        IndustryMode.STANDARD, False, 0.7, False, False, 0.5, False, False, 1.0, 0.5
    ),
    IndustryMode.DEFENSE: ModeProfile(
        IndustryMode.DEFENSE, True, 0.85, False, True, 0.95, False, False, 0.7, 0.85
    ),
    IndustryMode.LOGISTICS: ModeProfile(
        IndustryMode.LOGISTICS, False, 0.95, True, False, 0.6, False, False, 0.85, 0.6
    ),
    IndustryMode.DISASTER_RESPONSE: ModeProfile(
        IndustryMode.DISASTER_RESPONSE, True, 0.75, False, True, 0.8, True, False, 0.75, 0.75
    ),
    IndustryMode.INDUSTRIAL_INSPECTION: ModeProfile(
        IndustryMode.INDUSTRIAL_INSPECTION, False, 0.8, False, True, 0.5, False, True, 0.6, 0.55
    ),
}


class IndustryModeController:
    """Applies industry-specific cognition and safety parameters."""

    def __init__(self, mode: IndustryMode = IndustryMode.STANDARD):
        self._mode = mode
        self.profile = MODE_PROFILES[mode]

    def set_mode(self, mode: IndustryMode):
        self._mode = mode
        self.profile = MODE_PROFILES[mode]

    def apply_to_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        p = self.profile
        snapshot["industry_mode"] = p.mode.value
        snapshot["industry_profile"] = {
            "gps_denied_priority": p.gps_denied_priority,
            "payload_preservation": p.payload_preservation,
            "rf_resilience": p.rf_resilience,
            "max_aggression_cap": p.max_aggression_cap,
        }

        if p.gps_denied_priority and snapshot.get("navigation_state", {}).get("mode") == "gps":
            # Bias toward VIO readiness
            st = snapshot.setdefault("sensor_trust", {})
            st["primary_nav_source"] = st.get("primary_nav_source", "gps")

        if p.max_aggression_cap < 1.0 and "confidence" in snapshot:
            snapshot["confidence"]["max_aggression"] = min(
                float(snapshot["confidence"].get("max_aggression", 1)),
                p.max_aggression_cap,
            )

        if p.survival_bias > 0.6 and "survival" in snapshot:
            surv = snapshot["survival"]
            if surv.get("urgency") == "NORMAL" and float(snapshot.get("risk", {}).get("value", 0)) > 0.45:
                surv["urgency"] = "ELEVATED"

        return snapshot
