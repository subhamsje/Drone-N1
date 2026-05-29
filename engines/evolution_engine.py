"""Autonomous evolution engine — fleet-wide strategy mutation and collective optimization."""

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("evolution")


@dataclass
class PolicyGenome:
    genome_id: str
    survival_weights: Dict[str, float]
    route_aggression: float
    perception_trust_bias: float
    fitness: float = 0.5
    generation: int = 0

    def mutate(self, rate: float = 0.1) -> "PolicyGenome":
        new_weights = {k: max(0.01, v + random.gauss(0, rate)) for k, v in self.survival_weights.items()}
        total = sum(new_weights.values())
        new_weights = {k: v/total for k, v in new_weights.items()}
        return PolicyGenome(
            genome_id=f"gen-{int(time.time())}-{random.randint(0,999)}",
            survival_weights=new_weights,
            route_aggression=max(0.1, min(1.0, self.route_aggression + random.gauss(0, rate))),
            perception_trust_bias=max(0.1, min(1.0, self.perception_trust_bias + random.gauss(0, rate))),
            fitness=self.fitness,
            generation=self.generation + 1,
        )


class AutonomousEvolutionEngine:
    """
    Fleet evolves survival policies without human reprogramming.
    Selection pressure from operational outcomes.
    """

    def __init__(self, fleet_id: str, population_size: int = 8):
        self.fleet_id = fleet_id
        self._population: List[PolicyGenome] = []
        self._generation = 0
        self._best_fitness = 0.5
        self._init_population(population_size)

    def _init_population(self, n: int):
        base = {"EMERGENCY_LAND": 0.15, "RETURN_HOME": 0.3, "THRUST_REALLOC": 0.25, "HOLD": 0.3}
        for i in range(n):
            self._population.append(PolicyGenome(
                genome_id=f"gen0-{i}",
                survival_weights=base.copy(),
                route_aggression=0.5,
                perception_trust_bias=0.7,
                generation=0,
            ))

    def evaluate_fitness(self, snapshot: Dict[str, Any]) -> float:
        surv = float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.5))
        recovery_ok = 1.0 if snapshot.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH") and surv > 0.4 else 0.5
        crash = float(snapshot.get("inference", {}).get("crash_probability", 0))
        return max(0, min(1, surv * 0.5 + recovery_ok * 0.3 - crash * 0.2))

    def evolve_generation(self, fleet_snapshots: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not fleet_snapshots:
            return self.get_state()

        avg_fitness = sum(self.evaluate_fitness(s) for s in fleet_snapshots) / len(fleet_snapshots)
        for g in self._population:
            g.fitness = 0.9 * g.fitness + 0.1 * avg_fitness

        self._population.sort(key=lambda g: g.fitness, reverse=True)
        elite = self._population[:2]
        self._best_fitness = elite[0].fitness

        # Breed next generation
        new_pop = elite.copy()
        while len(new_pop) < len(self._population):
            parent = elite[random.randint(0, len(elite)-1)]
            child = parent.mutate(0.08)
            new_pop.append(child)

        self._population = new_pop[:len(self._population)]
        self._generation += 1

        return self.get_state()

    def get_recommended_genome(self) -> Dict[str, Any]:
        best = max(self._population, key=lambda g: g.fitness)
        return {
            "genome_id": best.genome_id,
            "survival_weights": best.survival_weights,
            "route_aggression": best.route_aggression,
            "fitness": round(best.fitness, 4),
            "generation": best.generation,
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "fleet_id": self.fleet_id,
            "generation": self._generation,
            "population": len(self._population),
            "best_fitness": round(self._best_fitness, 4),
            "elite_genome": self.get_recommended_genome(),
        }
