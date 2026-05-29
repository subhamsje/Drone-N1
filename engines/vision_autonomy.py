"""
Visual Autonomy Engine — GPS-denied navigation, landing zones, obstacle density.
Interfaces with ORB-SLAM3 / YOLO / depth models when deployed on edge.
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional, Tuple

from core.cognitive_models import VisionAutonomyState

logger = logging.getLogger("vision_autonomy")


class VisualAutonomyEngine:
    """
    Vision-native autonomy layer.
    When GPS confidence < threshold, activates visual odometry path.
    """

    GPS_DENIED_THRESHOLD = 0.45

    def __init__(self):
        self._vo_position = np.zeros(3)
        self._slam_confidence = 0.85
        self._frame_count = 0

    def update(
        self,
        sensor_trust: Dict[str, Any],
        physics: Dict[str, Any],
        navigation: Optional[Dict[str, Any]] = None,
    ) -> VisionAutonomyState:
        self._frame_count += 1
        gps_conf = float(sensor_trust.get("gps_confidence", 0.9))
        gps_denied = gps_conf < self.GPS_DENIED_THRESHOLD

        if gps_denied:
            # Simulate visual odometry integration
            imu = physics.get("imu", [0, 0, 0])
            dt = 0.2
            self._vo_position[0] += float(imu[0]) * dt * 0.1
            self._vo_position[1] += float(imu[1]) * dt * 0.1
            self._slam_confidence = min(0.95, self._slam_confidence + 0.01)
        else:
            self._slam_confidence = max(0.7, self._slam_confidence - 0.005)

        # Obstacle density from terrain mesh complexity
        obstacle_density = 0.15
        landing_zones = 0
        semantic_hazards: List[str] = []

        if navigation:
            terrain = navigation.get("terrain_type", "FIELD")
            safety = float(navigation.get("landing_safety", 0.8))
            if terrain in ("TREES", "WATER", "HUMAN"):
                obstacle_density = 0.75
                semantic_hazards.append(terrain.lower())
            elif terrain == "ROOFTOP":
                obstacle_density = 0.45
            landing_zones = 5 if safety > 0.7 else 2

        return VisionAutonomyState(
            visual_odometry_active=gps_denied,
            slam_confidence=float(self._slam_confidence),
            obstacle_density=obstacle_density,
            landing_zones_detected=landing_zones,
            gps_denied_mode=gps_denied,
            depth_available=True,
            semantic_hazards=semantic_hazards,
        )

    def get_vo_position(self) -> Tuple[float, float, float]:
        return tuple(self._vo_position.tolist())
