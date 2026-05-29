"""Adaptive flight control — MPC augmentation, thrust redistribution, energy-aware."""

import logging
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("adaptive_control")


@dataclass
class ControlDirective:
    thrust_redistribution: List[float]
    turbulence_compensation: List[float]
    energy_bias: float
    stability_gain: float
    aggression_scale: float
    mpc_cost_weight_adjust: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thrust_redistribution": [round(t, 3) for t in self.thrust_redistribution],
            "turbulence_compensation": [round(t, 3) for t in self.turbulence_compensation],
            "energy_bias": round(self.energy_bias, 4),
            "stability_gain": round(self.stability_gain, 4),
            "aggression_scale": round(self.aggression_scale, 4),
        }


class AdaptiveFlightController:
    """
    Augments base MPC with:
    - intelligent thrust redistribution under motor fault
    - turbulence compensation
    - confidence-scaled aggression
    """

    def __init__(self, n_motors: int = 4, hover_thrust: float = 5.42):
        self.n = n_motors
        self.hover = hover_thrust
        self._fault_mask = np.ones(n_motors)

    def compute(
        self,
        base_thrust: List[float],
        twin_physics: Dict[str, Any],
        confidence: Dict[str, Any],
        survival: Optional[Dict] = None,
        fault_index: Optional[int] = None,
    ) -> ControlDirective:
        thrust = np.array(base_thrust[:self.n], dtype=float)
        if len(thrust) < self.n:
            thrust = np.resize(thrust, self.n)
            thrust[:] = self.hover

        turb = float(twin_physics.get("turbulence_index", 0))
        vib = float(twin_physics.get("vibration_propagation", 0))
        thrust_deg = float(twin_physics.get("thrust_degradation_forecast", 0))

        # Thrust redistribution on fault
        if fault_index is not None and 0 <= fault_index < self.n:
            self._fault_mask[fault_index] = max(0.2, 1.0 - thrust_deg)
            lost = thrust[fault_index] * (1.0 - self._fault_mask[fault_index])
            others = [i for i in range(self.n) if i != fault_index]
            for i in others:
                thrust[i] += lost / len(others)

        # Turbulence compensation — differential thrust for attitude damping
        comp = np.array([
            turb * 0.1 * (1 if i % 2 == 0 else -1) for i in range(self.n)
        ])

        max_agg = float(confidence.get("max_aggression", 1.0))
        margin = float(confidence.get("safety_margin_multiplier", 1.0))
        energy_bias = max(0.7, 1.0 - (1.0 - max_agg) * 0.3)
        stability_gain = min(2.0, 1.0 + margin * 0.2 + vib * 0.3)

        if survival and survival.get("thrust_redistribution"):
            stability_gain *= 1.15

        thrust = np.clip(thrust * energy_bias, 0, 15.0)

        return ControlDirective(
            thrust_redistribution=thrust.tolist(),
            turbulence_compensation=comp.tolist(),
            energy_bias=energy_bias,
            stability_gain=stability_gain,
            aggression_scale=max_agg,
            mpc_cost_weight_adjust=margin,
        )
