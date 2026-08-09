"""High-fidelity digital twin physics — turbulence, drag, thermal, replay."""

import logging
import time
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from collections import deque

from core.cognitive_models import TwinPhysicsForecast

logger = logging.getLogger("twin_physics_hf")


@dataclass
class PhysicsReplayFrame:
    timestamp: float
    state: Dict[str, Any]
    wind: List[float]
    instability: float


class HighFidelityTwinPhysics:
    """
    Predictive physics cognition — forecasts instability before manifestation.
    """

    def __init__(self, mass_kg: float = 1.5, drag_coeff: float = 0.08):
        self.mass = mass_kg
        self.c_drag = drag_coeff
        self._wind_field = np.zeros(3)
        self._turbulence_state = 0.0
        self._thermal_state = 25.0
        self._vibration_modes = deque(maxlen=50)
        self._replay_buffer: List[PhysicsReplayFrame] = []

    def step(
        self,
        physics: Dict[str, Any],
        motor_thrusts: List[float],
        risk: float,
        dt: float = 0.2,
    ) -> TwinPhysicsForecast:
        imu = np.array(physics.get("imu", [0, 0, 9.81])[:3])
        rpm = float(physics.get("rpm", 5500))
        alt = float(physics.get("altitude", 5))

        # Wind field estimation (Kalman-smoothed)
        self._wind_field = 0.92 * self._wind_field + 0.08 * imu

        # Turbulence index from wind variance + altitude
        turb = float(np.clip(np.linalg.norm(self._wind_field) / 4.0 + alt / 50.0 * 0.1, 0, 1))

        # Aerodynamic drag estimate
        vel_est = np.linalg.norm(imu) * 0.1
        drag_force = 0.5 * self.c_drag * vel_est ** 2

        # Vibration propagation (modal superposition simplified)
        vib = abs(imu[0]) + abs(rpm - 5500) / 800.0
        self._vibration_modes.append(vib)
        vib_prop = float(np.mean(list(self._vibration_modes)) if self._vibration_modes else 0)

        # Thermal from motor stress with Joule heating model
        thrust_mean = float(np.mean(motor_thrusts)) if motor_thrusts else 5.0
        joule_heating = 0.05 * (thrust_mean ** 1.8)
        self._thermal_state = 0.94 * self._thermal_state + 0.06 * (22.0 + joule_heating * 12.0)
        thermal_inst = float(np.clip((self._thermal_state - 55.0) / 45.0, 0.0, 1.0))

        # Dynamic Pressure (q = 0.5 * rho * v^2) with ISA air density lapse
        rho_air = 1.225 * np.exp(-alt / 8500.0)
        dynamic_pressure_pa = float(0.5 * rho_air * (vel_est ** 2))

        # Structural Stress Tensor (Bending moment + Aerodynamic aeroelastic load)
        structural_stress_mpa = float((thrust_mean * 9.81 * 0.35) / 0.0012 + dynamic_pressure_pa * 0.04)

        # Thrust imbalance & motor degradation metric
        if motor_thrusts and len(motor_thrusts) >= 4:
            thrust_deg = float(np.std(motor_thrusts) / (np.mean(motor_thrusts) + 1e-6))
        else:
            thrust_deg = risk * 0.3

        # Power instability from battery state & dynamic internal resistance (Ri)
        battery_pct = float(physics.get("battery", 100.0))
        ri_ohms = 0.015 + 0.035 * max(0.0, (30.0 - battery_pct) / 30.0)
        if battery_pct < 30.0:
            thrust_deg = min(1.0, thrust_deg + 0.2)

        # Instability horizon calculation
        instability_rate = turb * 0.35 + vib_prop * 0.25 + thrust_deg * 0.25 + thermal_inst * 0.15
        horizon = max(3.0, 90.0 * (1.0 - instability_rate) * (alt / 10.0 + 0.1))

        forecast = TwinPhysicsForecast(
            wind_field_estimate=self._wind_field.tolist(),
            turbulence_index=turb,
            vibration_propagation=vib_prop,
            thrust_degradation_forecast=thrust_deg,
            instability_horizon_s=horizon,
            replay_available=True,
        )

        self._replay_buffer.append(PhysicsReplayFrame(
            time.time(), physics, self._wind_field.tolist(), instability_rate
        ))
        if len(self._replay_buffer) > 5000:
            self._replay_buffer = self._replay_buffer[-2500:]

        return forecast

    def replay_crash(self, start_ts: float, end_ts: float) -> List[Dict]:
        return [
            {"ts": f.timestamp, "instability": f.instability, "wind": f.wind}
            for f in self._replay_buffer
            if start_ts <= f.timestamp <= end_ts
        ]
