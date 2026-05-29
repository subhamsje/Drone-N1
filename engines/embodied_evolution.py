"""Continuous embodied evolution — RL + replay + swarm propagation + environmental priors."""

import logging
from dataclasses import dataclass
from collections import deque
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger("embodied_evolution")


@dataclass
class EmbodiedEvolutionState:
    generation: int
    thrust_evolution: float
    hover_evolution: float
    actuator_compensation: List[float]
    environmental_prior: str
    swarm_propagated: bool
    replay_samples: int
    evolution_fitness: float

    def to_dict(self) -> Dict[str, Any]:
        d = {k: v for k, v in self.__dict__.items() if k != "actuator_compensation"}
        d["actuator_compensation"] = [round(x, 4) for x in self.actuator_compensation]
        d["evolution_fitness"] = round(self.evolution_fitness, 4)
        return d


class ContinuousEmbodiedEvolutionEngine:
    """
    Long-horizon embodied optimization atop EmbodiedLearningEngine.
    Uses operational replay, environmental priors, fleet knowledge merge.
    """

    ENV_PRIORS = {
        "adverse_weather": np.array([0.9, 1.2, 1.3, 0.7, 0.95, 1.0]),
        "gps_denied": np.array([1.0, 1.15, 1.1, 0.75, 1.0, 1.05]),
        "urban": np.array([0.95, 1.05, 1.0, 0.85, 1.1, 1.0]),
        "contested": np.array([0.85, 1.25, 1.35, 0.65, 0.9, 0.95]),
        "default": np.ones(6),
    }

    def __init__(self):
        self._generation = 0
        self._replay: deque = deque(maxlen=2000)
        self._fleet_params_ema: Optional[np.ndarray] = None
        self._actuator_trim = np.ones(4)

    def ingest_replay(self, snapshot: Dict[str, Any], reward: float):
        self._replay.append({
            "reward": reward,
            "surv": float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0)),
            "region": snapshot.get("embodied_cognition", {}).get("regional_profile", "default"),
        })

    def merge_swarm_knowledge(self, swarm_params: List[Dict[str, Any]]) -> bool:
        if not swarm_params:
            return False
        vectors = []
        for p in swarm_params:
            vectors.append([
                p.get("thrust_scale", 1.0),
                p.get("hover_stability_gain", 1.0),
                p.get("turbulence_damping", 1.0),
            ])
        if vectors:
            merged = np.mean(vectors, axis=0)
            if self._fleet_params_ema is None:
                self._fleet_params_ema = merged
            else:
                self._fleet_params_ema = 0.7 * self._fleet_params_ema + 0.3 * merged
            return True
        return False

    def evolve_cycle(
        self,
        snapshot: Dict[str, Any],
        embodied_learning: Dict[str, Any],
        collective_swarm: Optional[Dict] = None,
    ) -> EmbodiedEvolutionState:
        region = snapshot.get("embodied_cognition", {}).get("regional_profile", "default")
        prior_key = region if region in self.ENV_PRIORS else (
            "contested" if snapshot.get("adversarial_operations", {}).get("deception_detected") else "default"
        )
        prior = self.ENV_PRIORS.get(prior_key, self.ENV_PRIORS["default"])

        reward = float(embodied_learning.get("cumulative_reward", 0.5))
        self.ingest_replay(snapshot, reward)

        # Replay batch improvement
        if len(self._replay) >= 10:
            recent = list(self._replay)[-20:]
            mean_r = np.mean([r["reward"] for r in recent])
            if mean_r > reward:
                self._generation += 1

        thrust = float(embodied_learning.get("thrust_scale", 1.0)) * prior[0]
        hover = float(embodied_learning.get("hover_stability_gain", 1.0)) * prior[1]

        # Actuator compensation from motor fault proxy
        motors = snapshot.get("physics", {}).get("motor_thrusts", [5.42] * 4)
        if isinstance(motors, list) and len(motors) >= 4:
            mean_t = np.mean(motors[:4])
            for i in range(4):
                delta = (motors[i] - mean_t) / max(mean_t, 0.1)
                self._actuator_trim[i] = 0.95 * self._actuator_trim[i] + 0.05 * (1.0 - abs(delta) * 0.3)
        self._actuator_trim = np.clip(self._actuator_trim, 0.6, 1.2)

        swarm_prop = False
        if collective_swarm:
            members = collective_swarm.get("cognition_graph", {}).get("nodes", [])
            if len(members) > 1:
                swarm_prop = self.merge_swarm_knowledge([embodied_learning])

        if self._fleet_params_ema is not None:
            thrust *= float(self._fleet_params_ema[0])
            hover *= float(self._fleet_params_ema[1])

        fitness = reward * float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.75))

        ctrl = snapshot.setdefault("adaptive_control", {})
        if isinstance(ctrl.get("adjusted_thrusts"), list):
            ctrl["evolved_thrusts"] = [
                t * thrust * self._actuator_trim[i]
                for i, t in enumerate(ctrl["adjusted_thrusts"][:4])
            ]

        return EmbodiedEvolutionState(
            generation=self._generation,
            thrust_evolution=thrust,
            hover_evolution=hover,
            actuator_compensation=self._actuator_trim.tolist(),
            environmental_prior=prior_key,
            swarm_propagated=swarm_prop,
            replay_samples=len(self._replay),
            evolution_fitness=fitness,
        )
