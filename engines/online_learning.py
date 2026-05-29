"""Online adaptive learning — edge policy evolution without centralized retraining."""

import logging
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("online_learning")


@dataclass
class AdaptivePolicyState:
    survival_weights: Dict[str, float]
    control_gains: Dict[str, float]
    aggression_bias: float
    wind_adaptation: float
    mission_category: str
    updates: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "survival_weights": {k: round(v, 4) for k, v in self.survival_weights.items()},
            "control_gains": {k: round(v, 4) for k, v in self.control_gains.items()},
            "aggression_bias": round(self.aggression_bias, 4),
            "wind_adaptation": round(self.wind_adaptation, 4),
            "mission_category": self.mission_category,
            "updates": self.updates,
        }


class OnlineAdaptiveLearningEngine:
    """
    Continual edge adaptation via exponential policy updates (RL-ready hooks).
    Adapts to wind, payload, sensor degradation, regional environments.
    """

    def __init__(self, learning_rate: float = 0.05):
        self.lr = learning_rate
        self._policy = AdaptivePolicyState(
            survival_weights={"EMERGENCY_LAND": 0.2, "RETURN_HOME": 0.3, "THRUST_REALLOC": 0.25, "HOLD": 0.25},
            control_gains={"stability": 1.0, "energy": 1.0, "turbulence": 1.0},
            aggression_bias=0.5,
            wind_adaptation=0.0,
            mission_category="general",
        )
        self._reward_history: List[float] = []

    def update_from_cycle(self, snapshot: Dict[str, Any]) -> AdaptivePolicyState:
        """RL-style reward: positive survivability, negative crash probability."""
        surv = float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.5))
        crash_p = float(snapshot.get("inference", {}).get("crash_probability", 0))
        reward = surv - crash_p * 0.5
        self._reward_history.append(reward)
        if len(self._reward_history) > 500:
            self._reward_history = self._reward_history[-250:]

        # Wind adaptation
        turb = float(snapshot.get("twin_physics", {}).get("turbulence_index", 0))
        self._policy.wind_adaptation = 0.95 * self._policy.wind_adaptation + 0.05 * turb

        # Boost strategies that succeeded under high reward
        strategy = snapshot.get("survival", {}).get("strategy", "HOLD")
        if reward > 0.6 and strategy in self._policy.survival_weights:
            self._policy.survival_weights[strategy] += self.lr * reward
        elif reward < 0.3 and strategy in self._policy.survival_weights:
            self._policy.survival_weights[strategy] = max(0.05, self._policy.survival_weights[strategy] - self.lr)

        # Normalize weights
        total = sum(self._policy.survival_weights.values()) + 1e-9
        self._policy.survival_weights = {k: v / total for k, v in self._policy.survival_weights.items()}

        # Control gain adaptation
        if turb > 0.6:
            self._policy.control_gains["turbulence"] = min(2.0, self._policy.control_gains["turbulence"] + self.lr)
            self._policy.control_gains["stability"] = min(2.0, self._policy.control_gains["stability"] + self.lr * 0.5)
            self._policy.aggression_bias = max(0.1, self._policy.aggression_bias - self.lr * 2)

        # Sensor degradation → conservative
        if float(snapshot.get("confidence", {}).get("global_uncertainty", 0)) > 0.5:
            self._policy.aggression_bias = max(0.1, self._policy.aggression_bias - self.lr)

        self._policy.updates += 1
        return self._policy

    def set_mission_category(self, category: str):
        self._policy.mission_category = category
        presets = {
            "defense": {"aggression_bias": 0.35},
            "logistics": {"aggression_bias": 0.65},
            "disaster": {"aggression_bias": 0.55},
            "inspection": {"aggression_bias": 0.45},
        }
        if category in presets:
            self._policy.aggression_bias = presets[category]["aggression_bias"]

    def get_policy(self) -> Dict[str, Any]:
        return self._policy.to_dict()
