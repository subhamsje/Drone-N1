"""
Sensor Trust & Probabilistic Fusion Engine
Never trust a single sensor — dynamic trust-weighted fusion with drift detection.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any
from collections import deque

from core.cognitive_models import SensorTrustState
from config.settings import SystemConfig

logger = logging.getLogger("sensor_trust")


class SensorTrustEngine:
    """
    Estimates per-sensor confidence and selects primary navigation source.
    Feeds trust weights into risk/cognition pipelines.
    """

    SENSOR_IDS = ("gps", "imu", "baro", "vision", "lidar", "magnetometer")

    def __init__(self, config: SystemConfig):
        self._innovation_history: deque = deque(maxlen=30)
        self._gps_residuals: deque = deque(maxlen=20)
        self._imu_bias_drift: deque = deque(maxlen=20)

    def evaluate(
        self,
        ekf_confidence: float,
        innovation_mag: float,
        imu: List[float],
        comm_delay: float,
        is_gps_spoofed: bool = False,
        vision_confidence: float = 0.85,
        gps_fix: int = 3,
    ) -> SensorTrustState:
        # GPS trust — degrades on spoof, low fix, high innovation
        gps_conf = 0.95
        if is_gps_spoofed:
            gps_conf = 0.05
        elif gps_fix < 3:
            gps_conf = 0.35 + 0.15 * gps_fix
        if innovation_mag > 2.0:
            gps_conf *= max(0.3, 1.0 - innovation_mag / 10.0)
        gps_conf = float(np.clip(gps_conf, 0.0, 1.0))

        # IMU trust — drift from acceleration inconsistency
        imu_arr = np.array(imu[:3] if len(imu) >= 3 else [0, 0, 0])
        imu_mag = float(np.linalg.norm(imu_arr))
        imu_conf = float(np.clip(1.0 - abs(imu_mag - 9.81) / 15.0, 0.4, 1.0))
        self._imu_bias_drift.append(imu_mag)
        drift_var = float(np.var(list(self._imu_bias_drift))) if len(self._imu_bias_drift) > 5 else 0.0
        if drift_var > 2.0:
            imu_drift_risk = "HIGH"
            imu_conf *= 0.6
        elif drift_var > 0.5:
            imu_drift_risk = "MEDIUM"
            imu_conf *= 0.8
        else:
            imu_drift_risk = "LOW"

        # Barometer — stable unless rapid altitude disagreement
        baro_conf = float(np.clip(ekf_confidence * 0.9 + 0.1, 0.5, 1.0))

        # Vision — external input or default high in sim
        vis_conf = float(np.clip(vision_confidence, 0.0, 1.0))

        # LiDAR / magnetometer — simulation placeholders
        lidar_conf = 0.88 if vis_conf > 0.5 else 0.5
        mag_conf = float(np.clip(0.9 - comm_delay * 2.0, 0.3, 1.0))

        # Weighted fusion confidence
        weights = np.array([gps_conf, imu_conf, baro_conf, vis_conf, lidar_conf, mag_conf])
        weights = weights / (weights.sum() + 1e-9)
        fusion_conf = float(np.dot(weights, np.array([gps_conf, imu_conf, baro_conf, vis_conf, lidar_conf, mag_conf])))

        degraded = []
        if gps_conf < 0.5:
            degraded.append("gps")
        if imu_conf < 0.5:
            degraded.append("imu")
        if comm_delay > 0.15:
            degraded.append("comms")

        # Primary nav source selection
        if gps_conf < 0.4 and vis_conf > 0.7:
            primary = "visual_odometry"
        elif gps_conf < 0.3 and imu_conf > 0.6:
            primary = "dead_reckoning"
        else:
            primary = "gps"

        return SensorTrustState(
            gps_confidence=gps_conf,
            imu_confidence=imu_conf,
            baro_confidence=baro_conf,
            vision_confidence=vis_conf,
            lidar_confidence=lidar_conf,
            magnetometer_confidence=mag_conf,
            fusion_confidence=fusion_conf,
            imu_drift_risk=imu_drift_risk,
            degraded_sensors=degraded,
            primary_nav_source=primary,
        )
