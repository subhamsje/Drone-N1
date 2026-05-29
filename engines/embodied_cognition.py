"""Embodied autonomous intelligence — adaptive flight personality without manual reconfiguration."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger("embodied_cognition")


@dataclass
class EmbodiedPolicyState:
    flight_personality: str  # conservative | balanced | aggressive
    landing_strategy_bias: str
    payload_adaptation_factor: float
    weather_signature_id: str
    turbulence_adaptation: float
    hardware_degradation_factor: float
    regional_profile: str
    aerodynamic_compensation: float
    control_aggression_scale: float
    mission_context: str

    def to_dict(self) -> Dict[str, Any]:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in self.__dict__.items()}


class EmbodiedCognitionEngine:
    """
    Aircraft-adaptive embodied policy — evolves behavior from telemetry signatures.
    No centralized retraining; edge-local adaptation each cycle.
    """

    def __init__(self):
        self._turbulence_ema = 0.0
        self._payload_ema = 1.0
        self._degradation_ema = 0.0
        self._region = "default"
        self._landing_evolution = 0

    def adapt(
        self,
        snapshot: Dict[str, Any],
        adaptive_policy: Optional[Dict] = None,
        industry_profile: Optional[Dict] = None,
    ) -> EmbodiedPolicyState:
        physics = snapshot.get("physics", {})
        twin = snapshot.get("twin_physics", {})
        nav = snapshot.get("navigation", {}) or {}
        conf = snapshot.get("confidence", {})

        turb = float(twin.get("turbulence_estimate", physics.get("turbulence", 0.1)))
        self._turbulence_ema = 0.85 * self._turbulence_ema + 0.15 * turb

        mass_factor = float(physics.get("payload_mass_kg", 0)) / max(1.0, float(physics.get("nominal_mass_kg", 2.5)))
        self._payload_ema = 0.9 * self._payload_ema + 0.1 * mass_factor

        sensor_trust = snapshot.get("sensor_trust", {})
        deg = 1.0 - float(sensor_trust.get("composite_trust", 0.9))
        self._degradation_ema = 0.9 * self._degradation_ema + 0.1 * deg

        weather_h = float(nav.get("weather_hazard", 0))
        if weather_h > 0.6:
            self._region = "adverse_weather"
        elif snapshot.get("navigation_state", {}).get("mode") != "gps":
            self._region = "gps_denied"
        else:
            self._region = snapshot.get("industry_mode", "default").lower()

        uncertainty = float(conf.get("global_uncertainty", 0.3))
        survival_urgency = snapshot.get("survival", {}).get("urgency", "NORMAL")

        if survival_urgency in ("IMMEDIATE", "HIGH") or uncertainty > 0.65:
            personality = "conservative"
            aggression = 0.35
        elif self._turbulence_ema < 0.25 and uncertainty < 0.35:
            personality = "balanced"
            aggression = 0.65
        else:
            personality = "aggressive" if self._turbulence_ema < 0.15 else "balanced"
            aggression = 0.5

        cap = float((industry_profile or {}).get("max_aggression_cap", 1.0))
        aggression = min(aggression, cap)

        if adaptive_policy:
            aggression *= float(adaptive_policy.get("control_scale", 1.0))

        landing_bias = "precision_hover" if snapshot.get("industry_mode") == "INDUSTRIAL_INSPECTION" else (
            "emergency_flat" if survival_urgency == "IMMEDIATE" else "gradient_descent"
        )
        if float(snapshot.get("landing_zone", {}).get("total_score", 0)) > 0.7:
            self._landing_evolution += 1
            landing_bias = "learned_preferred"

        aero_comp = float(np.clip(1.0 + self._turbulence_ema * 0.3 - self._degradation_ema * 0.2, 0.5, 1.5))

        return EmbodiedPolicyState(
            flight_personality=personality,
            landing_strategy_bias=landing_bias,
            payload_adaptation_factor=self._payload_ema,
            weather_signature_id=f"wx_{int(weather_h * 10)}",
            turbulence_adaptation=self._turbulence_ema,
            hardware_degradation_factor=self._degradation_ema,
            regional_profile=self._region,
            aerodynamic_compensation=aero_comp,
            control_aggression_scale=aggression,
            mission_context=snapshot.get("flight_operations", {}).get("mission_phase", "cruise"),
        )
