"""Autonomy trust & explainability — decision graphs, survival reasoning."""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("cognition.explain")


@dataclass
class DecisionExplanation:
    primary_action: str
    confidence: float
    reasoning_chain: List[str]
    factor_contributions: Dict[str, float]
    survival_rationale: str
    landing_rationale: str
    threat_rationale: str
    uncertainty_explanation: str
    ai_trust_score: float
    replay_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_action": self.primary_action,
            "confidence": round(self.confidence, 4),
            "reasoning_chain": self.reasoning_chain,
            "factor_contributions": {k: round(v, 4) for k, v in self.factor_contributions.items()},
            "survival_rationale": self.survival_rationale,
            "landing_rationale": self.landing_rationale,
            "threat_rationale": self.threat_rationale,
            "uncertainty_explanation": self.uncertainty_explanation,
            "ai_trust_score": round(self.ai_trust_score, 4),
            "replay_id": self.replay_id,
        }


class AutonomyExplainabilityEngine:
    """Explainable cognition for operators and certification."""

    def explain_cycle(self, snapshot: Dict[str, Any]) -> DecisionExplanation:
        decision = snapshot.get("decision", {})
        action = decision.get("action", "NONE")
        cognition = snapshot.get("cognition", {})
        survival = snapshot.get("survival", {})
        landing = snapshot.get("landing_zone", {})
        prob = snapshot.get("probabilistic_safety", {})
        conf = snapshot.get("confidence", {})

        factors = cognition.get("reasoning_factors", {})
        utilities = cognition.get("utility_scores", {})

        chain = []
        if float(snapshot.get("risk", {}).get("value", 0)) > 0.5:
            chain.append(f"Risk elevated to {snapshot['risk']['level']} ({snapshot['risk']['value']:.2f})")
        if survival.get("urgency") in ("IMMEDIATE", "HIGH"):
            chain.append(f"Survival engine urgency: {survival['urgency']} → strategy {survival.get('strategy')}")
        if decision.get("os_override"):
            chain.append(f"OS override: {decision.get('override_reason')}")
        if prob.get("recommendation") not in (None, "CONTINUE_MONITOR"):
            chain.append(f"Probabilistic safety: {prob['recommendation']}")
        if not chain:
            chain.append("Nominal operations — all safety margins within envelope")

        surv_rat = (
            f"Evaluated {survival.get('scenarios_evaluated', 0)} scenarios; "
            f"selected {survival.get('strategy')} with survival score {survival.get('survival_score', 0):.2f}"
        )
        land_rat = (
            f"Landing zone {landing.get('zone_id', 'LZ')} ranked #{landing.get('rank', 1)}: "
            f"{landing.get('terrain_type', 'unknown')} terrain, score {landing.get('total_score', 0):.2f}"
        )
        threat_rat = "No active threats"
        if snapshot.get("cyber_response"):
            threat_rat = f"Cyber response: {len(snapshot['cyber_response'])} containment actions"
        unc_rat = (
            f"Global uncertainty {conf.get('global_uncertainty', 0):.2f} → "
            f"degraded mode {conf.get('degraded_mode', 'NOMINAL')}"
        )

        trust = float(prob.get("autonomy_trust", cognition.get("confidence", 0.5)))

        return DecisionExplanation(
            primary_action=action,
            confidence=float(cognition.get("confidence", 0.5)),
            reasoning_chain=chain,
            factor_contributions=utilities or factors,
            survival_rationale=surv_rat,
            landing_rationale=land_rat,
            threat_rationale=threat_rat,
            uncertainty_explanation=unc_rat,
            ai_trust_score=trust,
            replay_id=snapshot.get("safety_audit_id", ""),
        )
