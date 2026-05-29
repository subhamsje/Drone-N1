"""Strategic self-evolution — routing doctrine, survival redesign, fleet mutation."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("strategic_evolution")


@dataclass
class StrategicDoctrine:
    version: int
    survival_weight: float
    routing_aggression: float
    adversarial_response: str
    environmental_adaptation: str
    mutations: List[str]

    def to_dict(self) -> Dict:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in self.__dict__.items()}


class StrategicEvolutionEngine:
    """Fleet-wide doctrine evolution without human redesign."""

    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self._version = 1
        self._doctrine = StrategicDoctrine(
            version=1,
            survival_weight=0.5,
            routing_aggression=0.65,
            adversarial_response="contain",
            environmental_adaptation="balanced",
            mutations=[],
        )

    def evolve(
        self,
        meta_cognition: Dict[str, Any],
        evolution: Dict[str, Any],
        collective: Dict[str, Any],
        adversarial: Dict[str, Any],
    ) -> StrategicDoctrine:
        mutations = []
        fitness = float(evolution.get("best_fitness", 0.5))
        health = float(meta_cognition.get("cognition_health_score", 0.75))

        if health < 0.5:
            self._doctrine.survival_weight = min(0.95, self._doctrine.survival_weight + 0.05)
            mutations.append("survival_weight_increase")
        if adversarial.get("contested_cognition_mode") == "contested":
            self._doctrine.adversarial_response = "aggressive_contain"
            self._doctrine.routing_aggression = max(0.3, self._doctrine.routing_aggression - 0.1)
            mutations.append("contested_routing_conservative")
        if collective.get("emergent_action") in ("SWARM_RTL", "COLLECTIVE_DEFEND"):
            self._doctrine.environmental_adaptation = "survival_first"
            mutations.append("collective_survival_doctrine")
        if fitness > 0.7:
            self._doctrine.routing_aggression = min(0.85, self._doctrine.routing_aggression + 0.02)
            mutations.append("fitness_routing_boost")

        if mutations:
            self._version += 1
        self._doctrine.version = self._version
        self._doctrine.mutations = mutations
        return self._doctrine
