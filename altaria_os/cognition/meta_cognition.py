"""Meta-cognition — self-evaluation, weakness identification, doctrine evolution."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("meta_cognition")


@dataclass
class CognitionWeakness:
    subsystem: str
    severity: float
    symptom: str
    recommended_mutation: str


@dataclass
class MetaCognitionReport:
    cognition_health_score: float
    weaknesses: List[CognitionWeakness]
    survival_doctrine_version: int
    policy_mutations_applied: List[str]
    fleet_doctrine_sync: bool
    introspection_summary: str
    strategic_evolution_signal: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cognition_health_score": round(self.cognition_health_score, 4),
            "weaknesses": [
                {"subsystem": w.subsystem, "severity": round(w.severity, 4),
                 "symptom": w.symptom, "recommended_mutation": w.recommended_mutation}
                for w in self.weaknesses
            ],
            "survival_doctrine_version": self.survival_doctrine_version,
            "policy_mutations_applied": self.policy_mutations_applied,
            "fleet_doctrine_sync": self.fleet_doctrine_sync,
            "introspection_summary": self.introspection_summary,
            "strategic_evolution_signal": round(self.strategic_evolution_signal, 4),
        }


class MetaCognitionEngine:
    """
    Evaluates own cognition, identifies weaknesses, evolves mission doctrine.
    Works with evolution engine — does not replace it.
    """

    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self._doctrine_version = 1
        self._mutations: List[str] = []
        self._cycle_scores: List[float] = []

    def introspect(
        self,
        snapshot: Dict[str, Any],
        world_forecast: Optional[Dict] = None,
        evolution: Optional[Dict] = None,
    ) -> MetaCognitionReport:
        weaknesses: List[CognitionWeakness] = []

        surv = float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.75))
        conf = float(snapshot.get("confidence", {}).get("global_uncertainty", 0.3))
        perc = snapshot.get("adversarial_perception", {}) or {}
        cyber = snapshot.get("cyber_warfare", {})
        wm = world_forecast or {}

        if surv < 0.5:
            weaknesses.append(CognitionWeakness(
                "survival", 1 - surv, "low_composite_survivability", "increase_survival_bias"
            ))
        if conf > 0.55:
            weaknesses.append(CognitionWeakness(
                "confidence", conf, "high_uncertainty", "reduce_aggression_cap"
            ))
        if perc.get("robustness_verdict") == "CRITICAL_FALLBACK":
            weaknesses.append(CognitionWeakness(
                "perception", 0.8, "critical_perception_fallback", "thermal_primary_routing"
            ))
        if cyber.get("mission_continuity_under_attack", True) is False:
            weaknesses.append(CognitionWeakness(
                "cyber", 0.9, "mission_continuity_threatened", "trust_anchor_rotation"
            ))

        forecast_surv = float(wm.get("mission_survivability_forecast", surv))
        if forecast_surv < surv - 0.15:
            weaknesses.append(CognitionWeakness(
                "world_model", 0.7, "negative_future_trajectory", "preemptive_deescalate"
            ))

        mutations = []
        for w in weaknesses:
            if w.severity > 0.6:
                mutations.append(w.recommended_mutation)
                self._mutations.append(f"{w.subsystem}:{w.recommended_mutation}")
                if w.recommended_mutation == "increase_survival_bias":
                    self._doctrine_version += 1

        health = max(0.0, min(1.0, surv * (1 - conf * 0.3) * (1 - len(weaknesses) * 0.05)))
        self._cycle_scores.append(health)
        if len(self._cycle_scores) > 200:
            self._cycle_scores = self._cycle_scores[-100:]

        evo_signal = float((evolution or {}).get("best_fitness", 0.5))
        trend = sum(self._cycle_scores[-10:]) / max(1, len(self._cycle_scores[-10:]))
        strategic = 0.5 * evo_signal + 0.5 * trend

        summary = (
            f"Health={health:.2f} weaknesses={len(weaknesses)} "
            f"doctrine_v{self._doctrine_version} forecast_surv={forecast_surv:.2f}"
        )

        return MetaCognitionReport(
            cognition_health_score=health,
            weaknesses=weaknesses,
            survival_doctrine_version=self._doctrine_version,
            policy_mutations_applied=mutations,
            fleet_doctrine_sync=len(mutations) > 0,
            introspection_summary=summary,
            strategic_evolution_signal=strategic,
        )

    def strategic_evolution(
        self,
        evolution: Dict[str, Any],
        embodied_learning: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Fleet-wide strategic policy evolution from reinforcement signals."""
        fitness = float(evolution.get("best_fitness", 0.5))
        mutations = []
        if fitness < 0.5:
            mutations.append("increase_survival_bias")
            self._doctrine_version += 1
        if embodied_learning and embodied_learning.get("cumulative_reward", 0) > 0.7:
            mutations.append("reinforce_embodied_params")
        return {
            "strategic_mutations": mutations,
            "doctrine_version": self._doctrine_version,
            "evolution_fitness": fitness,
            "fleet_collective_evolution": True,
        }

    def apply_doctrine_to_snapshot(self, snapshot: Dict[str, Any], report: MetaCognitionReport) -> Dict[str, Any]:
        if "increase_survival_bias" in report.policy_mutations_applied:
            surv = snapshot.setdefault("survival", {})
            if surv.get("urgency") == "NORMAL":
                surv["doctrine_bias"] = "elevated"
        if "reduce_aggression_cap" in report.policy_mutations_applied:
            snapshot.setdefault("confidence", {})["max_aggression"] = min(
                float(snapshot.get("confidence", {}).get("max_aggression", 1.0)), 0.55
            )
        snapshot["meta_cognition"] = report.to_dict()
        return snapshot
