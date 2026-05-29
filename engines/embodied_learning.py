"""True embodied learning — RL-driven thrust, hover, landing, energy optimization."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger("embodied_learning")


@dataclass
class EmbodiedLearningState:
    thrust_scale: float
    hover_stability_gain: float
    turbulence_damping: float
    landing_descent_rate: float
    energy_curve_bias: float
    payload_trim: float
    aerodynamic_learn_rate: float
    policy_updates: int
    cumulative_reward: float

    def to_dict(self) -> Dict[str, Any]:
        return {k: round(v, 4) if isinstance(v, float) else v for k, v in self.__dict__.items()}


class EmbodiedLearningEngine:
    """
    Online RL adaptation from mission telemetry — no manual tuning.
    Complements OnlineAdaptiveLearningEngine with continuous motor/energy optimization.
    """

    ACTION_DIM = 6  # thrust, hover, turb, landing, energy, payload

    def __init__(self, learning_rate: float = 0.08, discount: float = 0.95):
        self.lr = learning_rate
        self.gamma = discount
        self._params = np.array([1.0, 1.0, 1.0, 0.8, 1.0, 1.0], dtype=np.float64)
        self._param_ema = self._params.copy()
        self._updates = 0
        self._cumulative_reward = 0.0
        self._history: List[float] = []

    def _state_vector(self, snapshot: Dict[str, Any]) -> np.ndarray:
        return np.array([
            float(snapshot.get("twin_physics", {}).get("turbulence_estimate", 0.1)),
            float(snapshot.get("physics", {}).get("battery", 100)) / 100.0,
            float(snapshot.get("risk", {}).get("value", 0)),
            1.0 - float(snapshot.get("confidence", {}).get("global_uncertainty", 0.3)),
            float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.75)),
            float(snapshot.get("physics", {}).get("payload_mass_kg", 0)) / 5.0,
        ], dtype=np.float64)

    def update(self, snapshot: Dict[str, Any], online_policy: Optional[Dict] = None) -> EmbodiedLearningState:
        state = self._state_vector(snapshot)
        surv = float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.5))
        crash_p = float(snapshot.get("inference", {}).get("crash_probability", 0))
        energy = float(snapshot.get("physics", {}).get("battery", 100)) / 100.0

        reward = surv - crash_p * 0.6 + energy * 0.1
        self._cumulative_reward = 0.99 * self._cumulative_reward + 0.01 * reward
        self._history.append(reward)
        if len(self._history) > 1000:
            self._history = self._history[-500:]

        # Policy gradient style: nudge params toward reward
        grad = state * (reward - 0.5) * self.lr
        self._params += grad
        self._params = np.clip(self._params, [0.4, 0.5, 0.5, 0.3, 0.6, 0.7], [1.8, 2.0, 2.5, 1.2, 1.5, 1.4])
        self._param_ema = 0.92 * self._param_ema + 0.08 * self._params

        if online_policy:
            gains = online_policy.get("control_gains", {})
            self._params[0] *= float(gains.get("stability", 1.0))
            self._params[2] *= float(gains.get("turbulence", 1.0))

        self._updates += 1

        # Apply learned params to control path via snapshot hints
        ctrl = snapshot.setdefault("adaptive_control", {})
        base_thrust = ctrl.get("adjusted_thrusts", snapshot.get("physics", {}).get("motor_thrusts", [5.42] * 4))
        if isinstance(base_thrust, list):
            scale = float(self._param_ema[0])
            ctrl["rl_thrust_scale"] = scale
            ctrl["adjusted_thrusts"] = [t * scale for t in base_thrust[:4]]

        return EmbodiedLearningState(
            thrust_scale=float(self._param_ema[0]),
            hover_stability_gain=float(self._param_ema[1]),
            turbulence_damping=float(self._param_ema[2]),
            landing_descent_rate=float(self._param_ema[3]),
            energy_curve_bias=float(self._param_ema[4]),
            payload_trim=float(self._param_ema[5]),
            aerodynamic_learn_rate=float(np.mean(np.abs(self._params - 1.0))),
            policy_updates=self._updates,
            cumulative_reward=self._cumulative_reward,
        )
