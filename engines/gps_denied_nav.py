"""
GPS-Denied Autonomous Navigation
ORB-SLAM3 / VIO bridge with degraded-mode orchestration.
"""

import logging
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from collections import deque

logger = logging.getLogger("gps_denied_nav")


@dataclass
class NavigationState:
    mode: str  # gps | vio | slam | inertial | degraded
    position_ned: Tuple[float, float, float]
    velocity_ned: Tuple[float, float, float]
    orientation_quat: Tuple[float, float, float, float]
    localization_confidence: float
    map_quality: float
    drift_rate_m_s: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "position_ned": list(self.position_ned),
            "velocity_ned": list(self.velocity_ned),
            "localization_confidence": round(self.localization_confidence, 4),
            "map_quality": round(self.map_quality, 4),
            "drift_rate_m_s": round(self.drift_rate_m_s, 4),
        }


class ORBSLAM3Bridge:
    """
    Interface to ORB-SLAM3 process (Unix socket / shared memory in production).
    Simulation: visual-inertial odometry from IMU integration.
    """

    def __init__(self):
        self._position = np.zeros(3)
        self._velocity = np.zeros(3)
        self._keyframes = 0
        self._tracking_lost = False
        self._process = None

    def start(self, vocab_path: str = "", settings_path: str = ""):
        logger.info("ORB-SLAM3 bridge: simulation VIO (deploy binary for production)")

    def track(self, imu: List[float], dt: float, gyro: Optional[List[float]] = None) -> Tuple[np.ndarray, np.ndarray]:
        accel = np.array(imu[:3])
        self._velocity += accel * dt
        self._position += self._velocity * dt
        self._keyframes += 1
        if self._keyframes > 500 and np.linalg.norm(self._velocity) > 2.0:
            self._tracking_lost = True
        return self._position.copy(), self._velocity.copy()

    @property
    def tracking_ok(self) -> bool:
        return not self._tracking_lost and self._keyframes > 10


class GPSDeniedNavigator:
    """Orchestrates navigation mode transitions on GPS loss."""

    def __init__(self):
        self._slam = ORBSLAM3Bridge()
        self._slam.start()
        self._mode = "gps"
        self._confidence_history: deque = deque(maxlen=30)

    def update(
        self,
        gps_confidence: float,
        imu: List[float],
        dt: float = 0.2,
        vision_confidence: float = 0.85,
    ) -> NavigationState:
        if gps_confidence < 0.45:
            if vision_confidence > 0.65 and self._slam.tracking_ok:
                self._mode = "slam"
            elif vision_confidence > 0.5:
                self._mode = "vio"
            else:
                self._mode = "inertial"
        elif gps_confidence < 0.65:
            self._mode = "degraded"
        else:
            self._mode = "gps"

        pos, vel = self._slam.track(imu, dt)
        if self._mode == "gps":
            loc_conf = gps_confidence
            drift = 0.05
        elif self._mode == "slam":
            loc_conf = min(vision_confidence, 0.92)
            drift = 0.15
        elif self._mode == "vio":
            loc_conf = vision_confidence * 0.85
            drift = 0.25
        else:
            loc_conf = max(0.2, 0.5 - dt * 2)
            drift = 0.5 + dt

        self._confidence_history.append(loc_conf)
        map_q = 0.9 if self._slam.tracking_ok else 0.3

        return NavigationState(
            mode=self._mode,
            position_ned=(float(pos[0]), float(pos[1]), float(pos[2])),
            velocity_ned=(float(vel[0]), float(vel[1]), float(vel[2])),
            orientation_quat=(1.0, 0.0, 0.0, 0.0),
            localization_confidence=loc_conf,
            map_quality=map_q,
            drift_rate_m_s=drift,
        )

    def should_reroute(self) -> bool:
        return self._mode in ("inertial", "degraded") or (
            self._confidence_history and min(self._confidence_history) < 0.35
        )
