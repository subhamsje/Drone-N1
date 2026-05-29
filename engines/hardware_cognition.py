"""Hardware cognition — motor, ESC, vibration, battery, structural fatigue intelligence."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger("hardware_cognition")


@dataclass
class HardwareCognitionState:
    motor_degradation_index: float
    esc_wear_prediction: float
    vibration_evolution: float
    battery_chemistry_health: float
    structural_fatigue_risk: float
    maintenance_urgency: str
    hardware_survivability_factor: float

    def to_dict(self) -> Dict:
        return {k: round(v, 4) if isinstance(v, float) else v for k, v in self.__dict__.items()}


class HardwareCognitionEngine:
    """Embodied hardware intelligence from physics telemetry and flight-hour wear."""

    def __init__(self):
        self._rpm_ema = 0.0
        self._vibration_ema = 0.0
        self._battery_ema = 100.0
        self._motor_asymmetry_ema = 0.0
        self._cycles = 0

    def evaluate(
        self,
        snapshot: Dict[str, Any],
        flight_hour_intel: Optional[Dict] = None,
    ) -> HardwareCognitionState:
        physics = snapshot.get("physics", {})
        twin = snapshot.get("twin_physics", {})

        rpm = float(physics.get("rpm", 0))
        battery = float(physics.get("battery", 100))
        imu = physics.get("imu", [0, 0, 0])
        if isinstance(imu, (list, tuple)) and len(imu) >= 3:
            vibration = float(np.linalg.norm(imu[:3]))
        else:
            vibration = 0.0

        self._rpm_ema = 0.9 * self._rpm_ema + 0.1 * rpm
        self._vibration_ema = 0.85 * self._vibration_ema + 0.15 * vibration
        self._battery_ema = 0.95 * self._battery_ema + 0.05 * battery
        self._cycles += 1

        motors = physics.get("motor_thrusts", [5.42] * 4)
        if isinstance(motors, list) and len(motors) >= 4:
            asym = float(np.std(motors[:4]) / max(np.mean(motors[:4]), 0.1))
        else:
            asym = 0.0
        self._motor_asymmetry_ema = 0.9 * self._motor_asymmetry_ema + 0.1 * asym

        wear_index = 0.0
        if flight_hour_intel:
            aging = flight_hour_intel.get("actuator_aging_dataset", {})
            wears = [v.get("wear_index", 0) for v in aging.values() if isinstance(v, dict)]
            wear_index = max(wears) if wears else 0.0

        motor_deg = min(1.0, self._motor_asymmetry_ema * 2 + wear_index * 0.5)
        esc_wear = min(1.0, self._rpm_ema / 12000.0 * 0.3 + motor_deg * 0.4)
        vib_evo = min(1.0, self._vibration_ema / 15.0)
        batt_health = self._battery_ema / 100.0
        alt_roc = abs(float(twin.get("altitude_roc", physics.get("alt_roc", 0))))
        fatigue = min(1.0, vib_evo * 0.4 + motor_deg * 0.3 + alt_roc * 0.1)

        urgency = "nominal"
        if motor_deg > 0.65 or batt_health < 0.25:
            urgency = "immediate"
        elif motor_deg > 0.4 or esc_wear > 0.5:
            urgency = "scheduled"

        hw_surv = max(0.2, 1.0 - motor_deg * 0.35 - (1 - batt_health) * 0.25 - fatigue * 0.2)

        return HardwareCognitionState(
            motor_degradation_index=motor_deg,
            esc_wear_prediction=esc_wear,
            vibration_evolution=vib_evo,
            battery_chemistry_health=batt_health,
            structural_fatigue_risk=fatigue,
            maintenance_urgency=urgency,
            hardware_survivability_factor=hw_surv,
        )
