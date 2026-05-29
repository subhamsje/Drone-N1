"""Adversarial perception resilience — hostile environment survival modes."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger("perception.adversarial")


@dataclass
class AdversarialPerceptionState:
    survival_mode: str
    trust_routing: Dict[str, float]
    active_fallback: str
    adversarial_score: float
    thermal_nav_assist: bool
    radar_assist: bool
    redundancy_level: int
    uncertainty_bound: float
    robustness_verdict: str

    def to_dict(self) -> Dict[str, Any]:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in self.__dict__.items()}


class AdversarialPerceptionResilience:
    """
    Trust-weighted fusion under rain, fog, smoke, darkness, motion blur,
    sensor corruption, and adversarial visual conditions.
    """

    MODALITIES = ("rgb", "thermal", "depth", "lidar", "radar", "imu", "ultrasonic")

    def __init__(self):
        self._trust: Dict[str, float] = {m: 0.9 for m in self.MODALITIES}
        self._adversarial_events = 0

    def assess(
        self,
        perception_health: Dict[str, Any],
        multimodal: Optional[Dict] = None,
        environment: Optional[Dict] = None,
    ) -> AdversarialPerceptionState:
        env = environment or {}
        weather = float(env.get("weather_hazard", perception_health.get("weather_visibility", 1.0)))
        if isinstance(weather, float) and weather > 1:
            weather = 1.0 - min(weather, 1.0)

        lighting = float(perception_health.get("lighting_quality", 0.8))
        degraded = perception_health.get("degraded", False)
        pipeline = perception_health.get("active_pipeline", "rgb_standard")
        mm = multimodal or {}
        survival_mode = mm.get("survival_mode", "nominal")

        # Environment-driven trust decay
        conditions = {
            "rain": env.get("rain", weather > 0.5),
            "fog": env.get("fog", weather > 0.65),
            "smoke": env.get("smoke", False),
            "darkness": lighting < 0.35,
            "motion_blur": env.get("motion_blur", False),
        }

        for cond, active in conditions.items():
            if active:
                self._trust["rgb"] *= 0.85
                self._trust["depth"] *= 0.9
                if cond in ("fog", "smoke", "darkness"):
                    self._trust["thermal"] = min(1.0, self._trust["thermal"] * 1.05)
                    self._trust["radar"] = min(1.0, self._trust["radar"] * 1.08)

        if conditions.get("motion_blur"):
            self._trust["rgb"] *= 0.7

        corruption = float(env.get("sensor_corruption", 0))
        if corruption > 0.3:
            worst = min(self._trust, key=self._trust.get)
            self._trust[worst] *= 0.5
            self._adversarial_events += 1

        adv_visual = float(env.get("adversarial_visual", 0))
        adversarial_score = adv_visual + corruption * 0.5 + (1 - lighting) * 0.2

        routing = {m: float(np.clip(self._trust[m], 0.05, 1.0)) for m in self.MODALITIES}
        total = sum(routing.values()) or 1.0
        routing = {k: v / total for k, v in routing.items()}

        if routing.get("thermal", 0) > routing.get("rgb", 0):
            fallback = "thermal_assisted_navigation"
            thermal_nav = True
        elif routing.get("radar", 0) > 0.15:
            fallback = "radar_assisted_perception"
            thermal_nav = False
        elif routing.get("lidar", 0) > routing.get("rgb", 0):
            fallback = "lidar_primary"
            thermal_nav = False
        else:
            fallback = "imu_dead_reckoning" if degraded else pipeline
            thermal_nav = False

        radar_assist = routing.get("radar", 0) > 0.12
        redundancy = sum(1 for v in routing.values() if v > 0.1)

        if adversarial_score > 0.6 or degraded:
            survival_mode = "degraded_vision_survival"
        elif survival_mode == "nominal" and weather > 0.55:
            survival_mode = "weather_adaptive"

        uncertainty = 1.0 - float(perception_health.get("fusion_confidence", 0.7))
        verdict = "ROBUST" if uncertainty < 0.35 else "DEGRADED_OPERABLE" if uncertainty < 0.6 else "CRITICAL_FALLBACK"

        return AdversarialPerceptionState(
            survival_mode=survival_mode,
            trust_routing=routing,
            active_fallback=fallback,
            adversarial_score=adversarial_score,
            thermal_nav_assist=thermal_nav,
            radar_assist=radar_assist,
            redundancy_level=redundancy,
            uncertainty_bound=uncertainty,
            robustness_verdict=verdict,
        )
