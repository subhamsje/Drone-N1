"""
Autonomous Cognition Engine — multi-variable probabilistic reasoning.
NOT simple IF-rules — utility-weighted scenario evaluation.
"""

import logging
import math
import numpy as np
from typing import Any, Dict, Optional

from core.cognitive_models import CognitionOutput
from core.models import DecisionAction

logger = logging.getLogger("autonomous_cognition")


class AutonomousCognitionEngine:
    """
    Reasons over battery, weather, landing safety, GPS confidence,
    obstacles, mission priority, comms, risk probabilities.
    """

    def reason(
        self,
        snapshot: Dict[str, Any],
        sensor_trust: Dict[str, Any],
        failure_preds: Dict[str, float],
        survival_plan: Optional[Dict[str, Any]] = None,
        mission_priority: float = 0.5,
        payload_sensitive: bool = False,
    ) -> CognitionOutput:
        risk = float(snapshot.get("risk", {}).get("value", 0))
        battery = float(snapshot.get("physics", {}).get("battery", 100))
        nav = snapshot.get("navigation", {}) or {}
        cyber = snapshot.get("cybersecurity", {}) or {}
        anomaly = snapshot.get("anomaly", {}) or {}
        ttf = float(snapshot.get("ttf", 8.0))

        factors = {
            "battery_stress": max(0, 1.0 - battery / 100.0),
            "weather_hazard": float(nav.get("weather_hazard", 0)),
            "landing_safety": 1.0 - float(nav.get("landing_safety", 0.8)),
            "gps_uncertainty": 1.0 - float(sensor_trust.get("gps_confidence", 0.9)),
            "obstacle_density": float(snapshot.get("vision", {}).get("obstacle_density", 0.2)),
            "mission_priority": mission_priority,
            "comm_degradation": float(cyber.get("threat_level", 0)),
            "crash_probability": float(failure_preds.get("crash_probability", risk)),
            "anomaly_pressure": float(anomaly.get("score", 0)),
            "ttf_urgency": max(0, 1.0 - ttf / 8.0),
        }

        if payload_sensitive:
            factors["payload_factor"] = 0.3
        else:
            factors["payload_factor"] = 0.0

        # Utility scores per action
        utilities = {
            "EMERGENCY_LAND": self._utility_emergency(factors),
            "RETURN_HOME": self._utility_return(factors),
            "THRUST_ADJUST": self._utility_thrust(factors),
            "HOLD": self._utility_hold(factors),
            "OPERATOR_ESCALATE": self._utility_escalate(factors),
        }

        # Survival plan boost
        if survival_plan:
            strat = survival_plan.get("strategy", "")
            if strat in utilities:
                utilities[strat] = min(1.0, utilities.get(strat, 0) + 0.25)

        # Softmax selection
        exp_u = {k: math.exp(min(8.0, v * 6.0)) for k, v in utilities.items()}
        total = sum(exp_u.values()) + 1e-9
        probs = {k: v / total for k, v in exp_u.items()}
        best = max(probs, key=probs.get)
        confidence = probs[best]

        uncertainty = (
            factors["gps_uncertainty"] * 0.25
            + factors["crash_probability"] * 0.25
            + float(anomaly.get("uncertainty", 0)) * 0.2
            + factors["comm_degradation"] * 0.15
            + (1.0 - float(sensor_trust.get("fusion_confidence", 0.9))) * 0.15
        )

        if uncertainty > 0.65:
            aggression = "SURVIVAL"
        elif uncertainty > 0.45:
            aggression = "DEFENSIVE"
        elif uncertainty > 0.25:
            aggression = "CONSERVATIVE"
        else:
            aggression = "NOMINAL"

        operator = uncertainty > 0.8 and best == "OPERATOR_ESCALATE"

        return CognitionOutput(
            recommended_action=best,
            confidence=float(np.clip(confidence, 0, 1)),
            utility_scores=utilities,
            aggression_mode=aggression,
            uncertainty=float(np.clip(uncertainty, 0, 1)),
            reasoning_factors=factors,
            operator_intervention=operator,
        )

    def _utility_emergency(self, f: Dict[str, float]) -> float:
        return (
            0.30 * f["crash_probability"]
            + 0.25 * f["ttf_urgency"]
            + 0.20 * f["landing_safety"]
            + 0.15 * f["anomaly_pressure"]
            + 0.10 * (1.0 - f.get("landing_safety", 0))
        )

    def _utility_return(self, f: Dict[str, float]) -> float:
        return (
            0.25 * f["battery_stress"]
            + 0.25 * f["weather_hazard"]
            + 0.20 * f["crash_probability"]
            + 0.15 * f["gps_uncertainty"]
            + 0.15 * (1.0 - f["ttf_urgency"])
        )

    def _utility_thrust(self, f: Dict[str, float]) -> float:
        return (
            0.35 * f["anomaly_pressure"]
            + 0.30 * (1.0 - f["crash_probability"])
            + 0.20 * f["obstacle_density"]
            + 0.15 * f["battery_stress"]
        )

    def _utility_hold(self, f: Dict[str, float]) -> float:
        return max(0, 0.6 - f["crash_probability"] - f["ttf_urgency"] - f["weather_hazard"])

    def _utility_escalate(self, f: Dict[str, float]) -> float:
        return f["gps_uncertainty"] * 0.4 + f["comm_degradation"] * 0.4 + f["crash_probability"] * 0.2
