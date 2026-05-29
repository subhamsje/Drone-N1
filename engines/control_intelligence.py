"""Aerospace control intelligence — MPC augmentation, RL hooks, instability forecasting."""

import logging
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("control_intelligence")


@dataclass
class ControlIntelligenceOutput:
    mpc_weight_scale: float
    rl_stabilization_bias: List[float]
    turbulence_compensation_gain: float
    energy_optimal_thrust_scale: float
    instability_forecast_s: float
    aggression_limit: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mpc_weight_scale": round(self.mpc_weight_scale, 4),
            "rl_stabilization_bias": [round(v, 4) for v in self.rl_stabilization_bias],
            "turbulence_compensation_gain": round(self.turbulence_compensation_gain, 4),
            "energy_optimal_thrust_scale": round(self.energy_optimal_thrust_scale, 4),
            "instability_forecast_s": round(self.instability_forecast_s, 2),
            "aggression_limit": round(self.aggression_limit, 4),
        }


class ControlIntelligenceEngine:
    """
    Augments adaptive MPC with RL-assisted stabilization signals.
    Production: Ray RLlib policy server; here: calibrated heuristic policy.
    """

    def __init__(self, n_motors: int = 4):
        self.n = n_motors
        self._rl_policy_state = np.zeros(n_motors)

    def compute(
        self,
        snapshot: Dict[str, Any],
        adaptive_control: Dict[str, Any],
        confidence: Dict[str, Any],
        twin_physics: Dict[str, Any],
    ) -> ControlIntelligenceOutput:
        turb = float(twin_physics.get("turbulence_index", 0))
        horizon = float(twin_physics.get("instability_horizon_s", 60))
        unc = float(confidence.get("global_uncertainty", 0.2))
        max_agg = float(confidence.get("max_aggression", 1.0))
        margin = float(confidence.get("safety_margin_multiplier", 1.0))

        # RL stabilization — damp oscillation modes under turbulence
        rl_bias = np.array([
            turb * 0.05 * (1 if i % 2 == 0 else -1) for i in range(self.n)
        ])
        self._rl_policy_state = 0.85 * self._rl_policy_state + 0.15 * rl_bias

        turb_gain = min(2.0, 1.0 + turb * 1.5 + float(adaptive_control.get("stability_gain", 1) - 1) * 0.3)
        energy_scale = float(adaptive_control.get("energy_bias", 1.0)) * (1.0 - unc * 0.2)
        mpc_scale = margin * (1.0 - unc * 0.35)

        return ControlIntelligenceOutput(
            mpc_weight_scale=mpc_scale,
            rl_stabilization_bias=self._rl_policy_state.tolist(),
            turbulence_compensation_gain=turb_gain,
            energy_optimal_thrust_scale=energy_scale,
            instability_forecast_s=horizon,
            aggression_limit=max_agg * (1.0 - turb * 0.3),
        )
