"""Human-AI operational trust — explainable survival, confidence analytics."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("operational_trust")


@dataclass
class OperationalTrustReport:
    trust_score: float
    confidence_trend: str
    survival_escalation_reason: str
    route_change_reason: str
    recovery_lineage: List[str]
    uncertainty_factors: Dict[str, float]
    operator_alert_level: str
    mission_risk_score: float
    bounded_confidence: float
    survivability_explanation: str

    def to_dict(self) -> Dict:
        return {
            "trust_score": round(self.trust_score, 4),
            "confidence_trend": self.confidence_trend,
            "survival_escalation_reason": self.survival_escalation_reason,
            "route_change_reason": self.route_change_reason,
            "recovery_lineage": self.recovery_lineage,
            "uncertainty_factors": {k: round(v, 4) for k, v in self.uncertainty_factors.items()},
            "operator_alert_level": self.operator_alert_level,
            "mission_risk_score": round(self.mission_risk_score, 4),
            "bounded_confidence": round(self.bounded_confidence, 4),
            "survivability_explanation": self.survivability_explanation,
        }


class OperationalTrustEngine:
    """Collaborative autonomy trust for operators and certification."""

    def __init__(self):
        self._trust_ema = 0.85
        self._confidence_history: List[float] = []

    def evaluate(
        self,
        snapshot: Dict[str, Any],
        explanation: Optional[Dict] = None,
        mission_replay: Optional[Dict] = None,
    ) -> OperationalTrustReport:
        exp = explanation or snapshot.get("explanation", {})
        conf = 1.0 - float(snapshot.get("confidence", {}).get("global_uncertainty", 0.3))
        self._confidence_history.append(conf)
        if len(self._confidence_history) > 50:
            self._confidence_history = self._confidence_history[-30:]

        trend = "stable"
        if len(self._confidence_history) >= 5:
            recent = sum(self._confidence_history[-5:]) / 5
            older = sum(self._confidence_history[:5]) / 5
            if recent < older - 0.1:
                trend = "degrading"
            elif recent > older + 0.1:
                trend = "improving"

        surv = snapshot.get("survival", {})
        route = snapshot.get("route_governance", {})
        esc_reason = exp.get("survival_rationale", surv.get("strategy", "none"))
        route_reason = exp.get("factor_contributions", {}).get("route", route.get("reroute_reason", "none"))

        lineage = []
        if snapshot.get("decision", {}).get("os_override"):
            lineage.append(f"override:{snapshot['decision'].get('override_reason')}")
        if surv.get("urgency") in ("IMMEDIATE", "HIGH"):
            lineage.append(f"recovery:{surv.get('strategy')}")
        lineage.append(f"audit:{snapshot.get('safety_audit_id', 'n/a')}")

        factors = {
            "risk": float(snapshot.get("risk", {}).get("value", 0)),
            "perception": 1.0 - float((snapshot.get("adversarial_perception") or {}).get("uncertainty_bound", 0.3)),
            "cyber": float((snapshot.get("adversarial_operations") or {}).get("hardened_continuity", 1)),
            "world_model": float((snapshot.get("foundation_world_model") or {}).get("generative_survivability", 0.75)),
        }

        trust = conf * (1.0 - factors["risk"] * 0.4) * factors.get("cyber", 1.0)
        self._trust_ema = 0.9 * self._trust_ema + 0.1 * trust

        alert = "nominal"
        if trust < 0.4 or trend == "degrading":
            alert = "critical"
        elif trust < 0.6:
            alert = "elevated"

        mission_risk = float(snapshot.get("risk", {}).get("value", 0)) * (1 + factors.get("perception", 0))
        bounded_conf = max(0.0, min(1.0, conf * (1 - mission_risk * 0.5)))
        surv_exp = (
            f"Composite survivability {snapshot.get('probabilistic_safety', {}).get('composite_survivability', 0):.2f}; "
            f"hardware factor {snapshot.get('hardware_cognition', {}).get('hardware_survivability_factor', 1):.2f}"
        )

        return OperationalTrustReport(
            trust_score=self._trust_ema,
            confidence_trend=trend,
            survival_escalation_reason=str(esc_reason)[:100],
            route_change_reason=str(route_reason)[:80],
            recovery_lineage=lineage,
            uncertainty_factors=factors,
            operator_alert_level=alert,
            mission_risk_score=mission_risk,
            bounded_confidence=bounded_conf,
            survivability_explanation=surv_exp[:120],
        )
