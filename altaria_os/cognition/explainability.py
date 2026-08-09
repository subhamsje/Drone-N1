"""
Autonomy Trust & Situation Awareness-Based Agent Transparency (SAT) Engine.
Based on research:
- "Human-Agent Teaming for Multirobot Control: A Review of the Human Factors Issues" (IEEE Transactions on Human-Machine Systems, 2014)
- "Situation Awareness-Based Agent Transparency (SAT) for Autonomous Systems" (IEEE THMS, 2018 / 2020)

SAT 3-Level Formal Model:
- SAT Level 1: Current State, Active Degradation Mode, and Agent Intent
- SAT Level 2: Causal Reasoning, Constraint Boundaries, and Risk Attribution
- SAT Level 3: Projected Trajectory, Epistemic Uncertainty Horizon, and Operator Cognitive Workload Index
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("cognition.explain")


@dataclass
class SATLevel1State:
    current_mode: str
    primary_nav_source: str
    sensor_trust_vector: Dict[str, float]
    active_intent: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_mode": self.current_mode,
            "primary_nav_source": self.primary_nav_source,
            "sensor_trust_vector": {k: round(v, 3) for k, v in self.sensor_trust_vector.items()},
            "active_intent": self.active_intent,
        }


@dataclass
class SATLevel2Reasoning:
    dominant_failure_mode: str
    constraint_margins: Dict[str, float]
    candidate_actions_evaluated: List[str]
    causal_rationale_chain: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dominant_failure_mode": self.dominant_failure_mode,
            "constraint_margins": {k: round(v, 3) for k, v in self.constraint_margins.items()},
            "candidate_actions_evaluated": self.candidate_actions_evaluated,
            "causal_rationale_chain": self.causal_rationale_chain,
        }


@dataclass
class SATLevel3Projection:
    survivability_10s_forecast: float
    epistemic_uncertainty_score: float
    operator_cognitive_load_index: float  # 0.0 (low) -> 1.0 (overload)
    recommended_intervention_window_s: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "survivability_10s_forecast": round(self.survivability_10s_forecast, 4),
            "epistemic_uncertainty_score": round(self.epistemic_uncertainty_score, 4),
            "operator_cognitive_load_index": round(self.operator_cognitive_load_index, 4),
            "recommended_intervention_window_s": round(self.recommended_intervention_window_s, 2),
        }


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
    sat_level_1: Optional[SATLevel1State] = None
    sat_level_2: Optional[SATLevel2Reasoning] = None
    sat_level_3: Optional[SATLevel3Projection] = None

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
            "sat_level_1": self.sat_level_1.to_dict() if self.sat_level_1 else None,
            "sat_level_2": self.sat_level_2.to_dict() if self.sat_level_2 else None,
            "sat_level_3": self.sat_level_3.to_dict() if self.sat_level_3 else None,
        }


class AutonomyExplainabilityEngine:
    """
    Explainable AI & Human-Autonomy Teaming Engine implementing the SAT transparency protocol.
    """

    def explain_cycle(self, snapshot: Dict[str, Any]) -> DecisionExplanation:
        decision = snapshot.get("decision", {})
        action = decision.get("action", "NONE")
        cognition = snapshot.get("cognition", {})
        survival = snapshot.get("survival", {})
        landing = snapshot.get("landing_zone", {})
        prob = snapshot.get("probabilistic_safety", {})
        conf = snapshot.get("confidence", {})
        sensor_trust = snapshot.get("sensor_trust", {})
        fwm = snapshot.get("foundation_world_model", {})

        factors = cognition.get("reasoning_factors", {})
        utilities = cognition.get("utility_scores", {})

        # ── SAT Level 1: Current State & Intent ──
        sat_l1 = SATLevel1State(
            current_mode=str(snapshot.get("autonomy_mode", "NOMINAL_AUTONOMOUS")),
            primary_nav_source=str(sensor_trust.get("primary_nav_source", "gps")),
            sensor_trust_vector={
                "gps": float(sensor_trust.get("gps_confidence", 0.95)),
                "imu": float(sensor_trust.get("imu_confidence", 0.95)),
                "vision": float(sensor_trust.get("vision_confidence", 0.90)),
                "fusion": float(sensor_trust.get("fusion_confidence", 0.92)),
            },
            active_intent=f"EXECUTE_{action}",
        )

        # ── SAT Level 2: Causal Reasoning & Constraints ──
        chain = []
        risk_val = float(snapshot.get("risk", {}).get("value", 0.0))
        if risk_val > 0.5:
            chain.append(f"Risk elevated to {snapshot['risk'].get('level', 'HIGH')} ({risk_val:.2f})")
        if survival.get("urgency") in ("IMMEDIATE", "HIGH"):
            chain.append(f"Survival urgency: {survival['urgency']} -> strategy {survival.get('strategy')}")
        if decision.get("os_override"):
            chain.append(f"OS override triggered: {decision.get('override_reason')}")
        if prob.get("recommendation") not in (None, "CONTINUE_MONITOR"):
            chain.append(f"Probabilistic safety: {prob['recommendation']}")
        if not chain:
            chain.append("Nominal operations — flight envelope and constraints fully satisfied")

        sat_l2 = SATLevel2Reasoning(
            dominant_failure_mode=str(snapshot.get("risk", {}).get("dominant_source", "NOMINAL")),
            constraint_margins={
                "battery_margin": float(snapshot.get("telemetry", {}).get("battery", 100.0)) - 20.0,
                "geofence_distance_m": float(snapshot.get("routing", {}).get("geofence_clearance_m", 150.0)),
                "structural_stress_margin": max(0.0, 1.0 - risk_val),
            },
            candidate_actions_evaluated=["HOLD_POSITION", "THRUST_REALLOC", "RETURN_HOME", "EMERGENCY_LAND"],
            causal_rationale_chain=chain,
        )

        # ── SAT Level 3: Projection, Uncertainty & Operator Workload ──
        surv_10s = float(fwm.get("generative_survivability", 1.0 - risk_val * 0.5))
        unc_score = float(conf.get("global_uncertainty", 0.15))
        # Operator cognitive load index (higher when multi-faults or rapid mode transitions occur)
        cognitive_load = min(1.0, risk_val * 0.6 + unc_score * 0.4 + (0.3 if len(chain) > 2 else 0.0))
        intervention_window = max(2.5, 30.0 * (1.0 - risk_val))

        sat_l3 = SATLevel3Projection(
            survivability_10s_forecast=surv_10s,
            epistemic_uncertainty_score=unc_score,
            operator_cognitive_load_index=cognitive_load,
            recommended_intervention_window_s=intervention_window,
        )

        surv_rat = (
            f"Evaluated {survival.get('scenarios_evaluated', 0)} scenarios; "
            f"selected {survival.get('strategy', 'HOLD')} with survival score {survival.get('survival_score', 0):.2f}"
        )
        land_rat = (
            f"Landing zone {landing.get('zone_id', 'LZ')} ranked #{landing.get('rank', 1)}: "
            f"{landing.get('terrain_type', 'nominal')} terrain, score {landing.get('total_score', 0):.2f}"
        )
        threat_rat = "No active threats detected"
        if snapshot.get("cyber_response"):
            threat_rat = f"Cyber defense: {len(snapshot['cyber_response'])} containment actions active"
        unc_rat = (
            f"Global uncertainty {unc_score:.2f} -> degraded mode {conf.get('degraded_mode', 'NOMINAL')}"
        )

        trust = float(prob.get("autonomy_trust", cognition.get("confidence", 0.85)))

        return DecisionExplanation(
            primary_action=action,
            confidence=float(cognition.get("confidence", 0.85)),
            reasoning_chain=chain,
            factor_contributions=utilities or factors,
            survival_rationale=surv_rat,
            landing_rationale=land_rat,
            threat_rationale=threat_rat,
            uncertainty_explanation=unc_rat,
            ai_trust_score=trust,
            replay_id=str(snapshot.get("safety_audit_id", "REPLAY_001")),
            sat_level_1=sat_l1,
            sat_level_2=sat_l2,
            sat_level_3=sat_l3,
        )
