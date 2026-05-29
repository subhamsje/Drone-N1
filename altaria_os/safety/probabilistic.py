"""
Probabilistic Safety Engine — mission survivability, landing success, autonomy trust.
Uncertainty propagation across navigation, perception, recovery.
"""

import logging
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("safety.probabilistic")


@dataclass
class ProbabilisticSafetyAssessment:
    autonomy_trust: float
    navigation_confidence: float
    perception_confidence: float
    landing_success_probability: float
    mission_continuity_probability: float
    recovery_validation_score: float
    route_safety_probability: float
    composite_survivability: float
    uncertainty_budget: float
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in self.__dict__.items()}


class ProbabilisticSafetyEngine:
    """
    Estimates probabilistic safety margins — feeds confidence engine and veto layer.
    Uses Bayesian-style fusion of subsystem confidences.
    """

    def assess(
        self,
        snapshot: Dict[str, Any],
        sensor_trust: Dict[str, Any],
        confidence: Dict[str, Any],
        survival: Optional[Dict] = None,
        landing_zone: Optional[Dict] = None,
    ) -> ProbabilisticSafetyAssessment:
        fusion = float(sensor_trust.get("fusion_confidence", 0.9))
        nav_state = snapshot.get("navigation_state", {})
        nav_conf = float(nav_state.get("localization_confidence", fusion))
        gps_c = float(sensor_trust.get("gps_confidence", 0.9))
        vis_c = float(sensor_trust.get("vision_confidence", 0.85))
        perc = snapshot.get("perception", {})
        perc_conf = max(0.2, 1.0 - float(perc.get("obstacle_density", 0.2)) * 0.5)

        navigation_confidence = float(np.clip(0.4 * gps_c + 0.35 * nav_conf + 0.25 * vis_c, 0, 1))
        perception_confidence = float(np.clip(perc_conf * vis_c, 0, 1))

        lz_score = float((landing_zone or {}).get("total_score", snapshot.get("navigation", {}).get("landing_safety", 0.7)))
        human_risk = float((landing_zone or {}).get("human_density", 0.1))
        landing_success = float(np.clip(lz_score * (1.0 - human_risk * 0.8), 0, 1))

        risk = float(snapshot.get("risk", {}).get("value", 0))
        crash_p = float(snapshot.get("inference", {}).get("crash_probability", risk))
        batt = float(snapshot.get("physics", {}).get("battery", 100)) / 100.0
        route_ok = 1.0 - float(snapshot.get("route_governance", {}).get("corridor_risk", 0))

        mission_continuity = float(np.clip(
            (1.0 - crash_p) * 0.35 + batt * 0.25 + route_ok * 0.2 + navigation_confidence * 0.2,
            0, 1,
        ))

        surv_score = float((survival or {}).get("survival_score", 0.5))
        best_out = (survival or {}).get("best_outcome", {})
        recovery_val = float(best_out.get("survival_probability", surv_score)) if best_out else surv_score

        route_safety = float(np.clip(
            route_ok * (1.0 - float(snapshot.get("route_governance", {}).get("no_fly_violation", False)) * 0.5),
            0, 1,
        ))

        global_u = float(confidence.get("global_uncertainty", 0.2))
        autonomy_trust = float(np.clip(1.0 - global_u * 0.6 - crash_p * 0.4, 0, 1))

        composite = float(np.clip(
            0.25 * landing_success + 0.25 * mission_continuity + 0.20 * recovery_val
            + 0.15 * autonomy_trust + 0.15 * route_safety,
            0, 1,
        ))

        uncertainty_budget = float(np.clip(global_u + (1.0 - fusion) * 0.3, 0, 1))

        if composite < 0.35 or landing_success < 0.3:
            rec = "ABORT_MISSION_ESCALATE"
        elif composite < 0.55 or crash_p > 0.6:
            rec = "RECOVERY_REQUIRED"
        elif uncertainty_budget > 0.65:
            rec = "DEGRADE_AUTONOMY"
        else:
            rec = "CONTINUE_MONITOR"

        return ProbabilisticSafetyAssessment(
            autonomy_trust=autonomy_trust,
            navigation_confidence=navigation_confidence,
            perception_confidence=perception_confidence,
            landing_success_probability=landing_success,
            mission_continuity_probability=mission_continuity,
            recovery_validation_score=recovery_val,
            route_safety_probability=route_safety,
            composite_survivability=composite,
            uncertainty_budget=uncertainty_budget,
            recommendation=rec,
        )
