"""
Digital Twin Physics Intelligence — wind, turbulence, vibration, thrust forecasting.
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional

from core.cognitive_models import TwinPhysicsForecast

logger = logging.getLogger("twin_physics")


class TwinPhysicsEngine:
    """Real-time aerodynamic reconstruction and instability forecasting."""

    def __init__(self):
        self._wind_estimate = np.zeros(3)
        self._vibration_state = 0.0

    def forecast(
        self,
        physics: Dict[str, Any],
        risk: float,
        motor_thrusts: Optional[List[float]] = None,
        fault_losses: Optional[List[float]] = None,
    ) -> TwinPhysicsForecast:
        imu = physics.get("imu", [0, 0, 0])
        rpm = float(physics.get("rpm", 5000))
        altitude = float(physics.get("altitude", 5))

        # Wind field from IMU residual (simplified)
        self._wind_estimate = 0.9 * self._wind_estimate + 0.1 * np.array(imu[:3])
        turb = float(np.clip(np.linalg.norm(self._wind_estimate) / 5.0, 0, 1))

        # Vibration propagation
        vib = abs(float(imu[0]) if imu else 0) + abs(rpm - 5500) / 1000.0
        self._vibration_state = 0.85 * self._vibration_state + 0.15 * vib

        # Thrust degradation
        thrust_deg = 0.0
        if fault_losses:
            thrust_deg = float(np.mean(fault_losses))
        elif motor_thrusts:
            hover = 5.42 * 4
            actual = sum(motor_thrusts)
            thrust_deg = max(0, 1.0 - actual / hover)

        # Instability horizon — seconds until critical if trend continues
        horizon = max(5.0, 120.0 * (1.0 - risk) * (altitude / 10.0))

        return TwinPhysicsForecast(
            wind_field_estimate=self._wind_estimate.tolist(),
            turbulence_index=turb,
            vibration_propagation=float(self._vibration_state),
            thrust_degradation_forecast=thrust_deg,
            instability_horizon_s=horizon,
            replay_available=True,
        )
