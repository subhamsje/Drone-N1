"""Multi-modal resilient perception — RGB, thermal, depth, LiDAR, radar fusion."""

import logging
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("perception.multimodal")


@dataclass
class ModalityTrust:
    modality: str
    confidence: float
    available: bool
    degraded: bool


@dataclass
class MultimodalPerceptionState:
    fused_confidence: float
    primary_modality: str
    obstacle_density: float
    visibility_index: float
    weather_degraded: bool
    modalities: List[ModalityTrust]
    survival_mode: str  # nominal | degraded_vision | minimal_perception

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fused_confidence": round(self.fused_confidence, 4),
            "primary_modality": self.primary_modality,
            "obstacle_density": round(self.obstacle_density, 4),
            "visibility_index": round(self.visibility_index, 4),
            "weather_degraded": self.weather_degraded,
            "survival_mode": self.survival_mode,
            "modalities": [
                {"mod": m.modality, "conf": round(m.confidence, 3), "ok": m.available}
                for m in self.modalities
            ],
        }


class MultimodalPerceptionFusion:
    """Trust-weighted fusion surviving fog, rain, darkness, partial sensor failure."""

    MODALITIES = ("rgb", "thermal", "depth", "lidar", "radar", "ultrasonic")

    def __init__(self):
        self._health = {m: 1.0 for m in self.MODALITIES}
        self._weather = {"fog": 0.0, "rain": 0.0, "smoke": 0.0, "darkness": 0.0}

    def set_weather(self, fog: float = 0, rain: float = 0, smoke: float = 0, darkness: float = 0):
        self._weather = {"fog": fog, "rain": rain, "smoke": smoke, "darkness": darkness}

    def set_sensor_failure(self, modality: str):
        if modality in self._health:
            self._health[modality] = 0.0

    def fuse(
        self,
        perception: Optional[Dict] = None,
        perception_health: Optional[Dict] = None,
    ) -> MultimodalPerceptionState:
        weather_deg = max(self._weather.values()) > 0.5
        vis_idx = float(np.clip(1.0 - max(self._weather.values()) * 0.7, 0.1, 1.0))

        trusts: List[ModalityTrust] = []
        weights = []
        confs = []

        rgb_h = self._health["rgb"] * (1.0 - self._weather["darkness"] * 0.6 - self._weather["fog"] * 0.4)
        thermal_h = self._health["thermal"] * (1.0 + self._weather["darkness"] * 0.3)
        depth_h = self._health["depth"] * (1.0 - self._weather["fog"] * 0.5)
        lidar_h = self._health["lidar"] * (1.0 - self._weather["rain"] * 0.3)
        radar_h = self._health["radar"]
        ultra_h = self._health["ultrasonic"]

        for name, conf in [
            ("rgb", rgb_h), ("thermal", thermal_h), ("depth", depth_h),
            ("lidar", lidar_h), ("radar", radar_h), ("ultrasonic", ultra_h),
        ]:
            avail = conf > 0.2
            deg = conf < 0.5
            trusts.append(ModalityTrust(name, conf, avail, deg))
            if avail:
                weights.append(conf)
                confs.append(conf)

        fused = float(np.average(confs, weights=weights)) if confs else 0.2
        primary = max(trusts, key=lambda t: t.confidence if t.available else -1).modality

        obs = float((perception or {}).get("obstacle_density", 0.2))
        if weather_deg:
            obs = min(1.0, obs + 0.15)

        if fused < 0.35 or sum(1 for t in trusts if t.available) < 2:
            survival_mode = "minimal_perception"
        elif fused < 0.55 or weather_deg:
            survival_mode = "degraded_vision"
        else:
            survival_mode = "nominal"

        return MultimodalPerceptionState(
            fused_confidence=fused,
            primary_modality=primary,
            obstacle_density=obs,
            visibility_index=vis_idx,
            weather_degraded=weather_deg,
            modalities=trusts,
            survival_mode=survival_mode,
        )
