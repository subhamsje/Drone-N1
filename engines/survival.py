"""
Autonomous Survival Engine — self-preserving UAV intelligence.
Observe → Predict → Evaluate → Simulate → Decide → Recover → Verify → Learn
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional

from core.cognitive_models import SurvivalPlan, ScenarioOutcome
from core.models import DecisionAction

logger = logging.getLogger("survival")


class ScenarioSimulator:
    """Monte-Carlo-lite outcome simulation for survival strategies."""

    ACTIONS = [
        "EMERGENCY_LAND", "RETURN_HOME", "THRUST_REALLOC",
        "HOLD", "REROUTE", "VISUAL_NAV_HOLD", "POWER_SAVE_GLIDE",
    ]

    def simulate(
        self,
        action: str,
        risk: float,
        battery: float,
        landing_safety: float,
        gps_conf: float,
        weather_hazard: float,
        payload_sensitive: bool = False,
    ) -> ScenarioOutcome:
        base_survival = 0.92
        if action == "EMERGENCY_LAND":
            survival = base_survival * landing_safety * (0.7 + 0.3 * gps_conf)
            human_risk = max(0.01, 0.15 * (1.0 - landing_safety))
            payload = 0.85 * landing_safety
            energy = 0.4
            t_exec = 25.0
        elif action == "RETURN_HOME":
            survival = base_survival * (battery / 100.0) * (1.0 - weather_hazard * 0.5)
            human_risk = 0.05
            payload = 0.9 if not payload_sensitive else 0.75
            energy = 0.6
            t_exec = 120.0
        elif action == "THRUST_REALLOC":
            survival = base_survival * (1.0 - risk * 0.4)
            human_risk = 0.08
            payload = 0.88
            energy = 0.5
            t_exec = 5.0
        elif action == "VISUAL_NAV_HOLD":
            survival = 0.75 + 0.2 * gps_conf
            human_risk = 0.04
            payload = 0.92
            energy = 0.3
            t_exec = 30.0
        elif action == "POWER_SAVE_GLIDE":
            survival = 0.7 + 0.25 * (battery / 100.0)
            human_risk = 0.03
            payload = 0.95
            energy = 0.15
            t_exec = 60.0
        else:
            survival = max(0.3, 0.9 - risk - weather_hazard)
            human_risk = 0.1
            payload = 0.7
            energy = 0.2
            t_exec = 10.0

        survival *= float(np.clip(1.0 - risk * 0.35, 0.2, 1.0))
        return ScenarioOutcome(
            action=action,
            survival_probability=float(np.clip(survival, 0, 1)),
            payload_safety=float(np.clip(payload, 0, 1)),
            human_risk=float(np.clip(human_risk, 0, 1)),
            energy_cost=energy,
            time_to_execute_s=t_exec,
        )


class AutonomousSurvivalEngine:
    """Core differentiator — autonomous self-preservation layer."""

    def __init__(self):
        self._simulator = ScenarioSimulator()
        self._last_plan: Optional[SurvivalPlan] = None
        self._recovery_count = 0

    def plan(
        self,
        snapshot: Dict[str, Any],
        failure_preds: Optional[Dict[str, float]] = None,
        sensor_trust: Optional[Dict[str, Any]] = None,
    ) -> SurvivalPlan:
        risk = float(snapshot.get("risk", {}).get("value", 0))
        level = snapshot.get("risk", {}).get("level", "LOW")
        battery = float(snapshot.get("physics", {}).get("battery", 100))
        nav = snapshot.get("navigation", {}) or {}
        landing_safety = float(nav.get("landing_safety", 0.8))
        weather = float(nav.get("weather_hazard", 0))
        gps_conf = float((sensor_trust or {}).get("gps_confidence", 0.9))
        primary_nav = (sensor_trust or {}).get("primary_nav_source", "gps")
        crash_p = float((failure_preds or {}).get("crash_probability", risk))

        # Expand action set under GPS denial
        actions = list(self._simulator.ACTIONS)
        if primary_nav == "visual_odometry":
            actions = ["VISUAL_NAV_HOLD", "EMERGENCY_LAND", "THRUST_REALLOC", "POWER_SAVE_GLIDE"]

        outcomes = [
            self._simulator.simulate(a, risk, battery, landing_safety, gps_conf, weather)
            for a in actions
        ]

        # Multi-objective utility: maximize survival, minimize human risk, preserve payload
        def utility(o: ScenarioOutcome) -> float:
            return (
                0.50 * o.survival_probability
                + 0.25 * o.payload_safety
                + 0.20 * (1.0 - o.human_risk)
                - 0.05 * o.energy_cost
            )

        best = max(outcomes, key=utility)
        survival_score = utility(best)

        if level == "CRITICAL" or crash_p > 0.75:
            urgency = "IMMEDIATE"
        elif level == "HIGH" or crash_p > 0.5:
            urgency = "HIGH"
        elif risk > 0.35:
            urgency = "ELEVATED"
        else:
            urgency = "NORMAL"

        backup_nav = "visual_odometry" if gps_conf < 0.4 else "gps"
        thrust_redist = best.action in ("THRUST_REALLOC", "EMERGENCY_LAND")
        emergency_power = battery < 25 or urgency == "IMMEDIATE"

        plan = SurvivalPlan(
            strategy=best.action,
            urgency=urgency,
            survival_score=survival_score,
            scenarios_evaluated=len(outcomes),
            best_outcome=best,
            backup_nav=backup_nav,
            thrust_redistribution=thrust_redist,
            emergency_power_mode=emergency_power,
            landing_site_rank={
                "x": nav.get("landing_x"),
                "y": nav.get("landing_y"),
                "safety": landing_safety,
                "terrain": nav.get("terrain_type"),
            } if nav else None,
        )
        self._last_plan = plan
        if urgency in ("IMMEDIATE", "HIGH"):
            self._recovery_count += 1
        return plan

    def should_override_decision(self, plan: SurvivalPlan, current_action: str) -> bool:
        if plan.urgency == "IMMEDIATE":
            return current_action not in ("EMERGENCY_LAND",)
        if plan.urgency == "HIGH" and plan.survival_score > 0.75:
            return current_action == "NONE"
        return False

    def map_to_decision_action(self, strategy: str) -> str:
        mapping = {
            "EMERGENCY_LAND": DecisionAction.EMERGENCY_LAND.value,
            "RETURN_HOME": DecisionAction.RETURN_HOME.value,
            "THRUST_REALLOC": DecisionAction.THRUST_ADJUST.value,
            "REROUTE": DecisionAction.RETURN_HOME.value,
            "VISUAL_NAV_HOLD": DecisionAction.THRUST_ADJUST.value,
            "POWER_SAVE_GLIDE": DecisionAction.RETURN_HOME.value,
            "HOLD": DecisionAction.NONE.value,
        }
        return mapping.get(strategy, DecisionAction.NONE.value)
