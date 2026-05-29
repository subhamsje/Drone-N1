"""Perception robustness — low-light, thermal, multi-camera, weather-degraded."""

import logging
from dataclasses import dataclass
from typing import Any, Dict

import numpy as np

logger = logging.getLogger("perception.robustness")


@dataclass
class PerceptionHealth:
    rgb_available: bool
    thermal_available: bool
    depth_available: bool
    lighting_quality: float
    weather_visibility: float
    fusion_confidence: float
    active_pipeline: str
    degraded: bool

    def to_dict(self) -> Dict[str, Any]:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in self.__dict__.items()}


class PerceptionRobustnessLayer:
    """Routes perception through best available modality under degradation."""

    def __init__(self):
        self._camera_health = {"rgb": 1.0, "thermal": 0.9, "depth": 0.85}
        self._lighting_ema = 0.8

    def update(
        self,
        weather_hazard: float = 0.0,
        obstacle_density: float = 0.2,
        force_low_light: bool = False,
    ) -> PerceptionHealth:
        # Simulate lighting from time-of-day proxy + weather
        self._lighting_ema = 0.9 * self._lighting_ema + 0.1 * max(0.1, 1.0 - weather_hazard * 0.7)
        if force_low_light:
            self._lighting_ema = 0.25

        visibility = float(np.clip(1.0 - weather_hazard * 0.6 - obstacle_density * 0.2, 0.1, 1.0))

        rgb_ok = self._camera_health["rgb"] > 0.3 and self._lighting_ema > 0.35
        thermal_ok = self._camera_health["thermal"] > 0.4
        depth_ok = self._camera_health["depth"] > 0.3 and visibility > 0.4

        if not rgb_ok and thermal_ok:
            pipeline = "thermal_primary"
            fusion = 0.75 * self._camera_health["thermal"] + 0.25 * visibility
        elif not rgb_ok and depth_ok:
            pipeline = "depth_assisted"
            fusion = 0.65
        elif self._lighting_ema < 0.4 and thermal_ok:
            pipeline = "low_light_thermal"
            fusion = 0.7
        else:
            pipeline = "rgb_standard"
            fusion = float(np.clip(self._lighting_ema * visibility, 0.2, 1.0))

        degraded = fusion < 0.45 or not (rgb_ok or thermal_ok)

        return PerceptionHealth(
            rgb_available=rgb_ok,
            thermal_available=thermal_ok,
            depth_available=depth_ok,
            lighting_quality=self._lighting_ema,
            weather_visibility=visibility,
            fusion_confidence=fusion,
            active_pipeline=pipeline,
            degraded=degraded,
        )

    def apply_camera_failure(self, camera: str):
        self._camera_health[camera] = 0.0
