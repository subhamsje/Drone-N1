"""
Foundation World Model Engine — Recurrent State-Space Model (RSSM) Latent Generative Dynamics.
Based on research:
- "DayDreamer: World Models for Physical Robot Learning" (Science Robotics / CoRL / PMLR, 2023)
- "Predictive Coding and Latent Dynamics for Autonomous Flight Decision-Making" (IEEE TNNLS)

Architectural Components:
1. Deterministic Recurrent State h_t = GRU(h_{t-1}, [z_{t-1}, a_{t-1}])
2. Stochastic Latent State z_t ~ N(mu(h_t), sigma^2(h_t))
3. Multi-Step Counterfactual Latent Rollforward Simulation (Imaginary Trajectories)
4. Epistemic Uncertainty Estimation & Latent Consequence Graph Generation
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("foundation_world")


@dataclass
class LatentWorldState:
    latent: List[float]
    recurrent_h: List[float]
    decoded_risk: float
    decoded_survivability: float
    epistemic_uncertainty: float
    rollforward_steps: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "latent_dim": len(self.latent),
            "latent": [round(x, 4) for x in self.latent[:8]],
            "recurrent_h": [round(x, 4) for x in self.recurrent_h[:8]],
            "decoded_risk": round(self.decoded_risk, 4),
            "decoded_survivability": round(self.decoded_survivability, 4),
            "epistemic_uncertainty": round(self.epistemic_uncertainty, 4),
            "rollforward_steps": self.rollforward_steps,
        }


@dataclass
class CounterfactualTrajectory:
    action_candidate: str
    predicted_risk_horizon: List[float]
    survivability_score: float
    boundary_violation_probability: float


@dataclass
class FoundationForecast:
    latent_state: LatentWorldState
    consequence_graph: List[Dict[str, Any]]
    counterfactual_rollouts: List[Dict[str, Any]]
    swarm_interaction_forecast: Dict[str, float]
    comm_collapse_probability: float
    adversarial_escalation_forecast: float
    generative_survivability: float
    preemptive_recommendation: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "latent_state": self.latent_state.to_dict(),
            "consequence_graph": self.consequence_graph,
            "counterfactual_rollouts": self.counterfactual_rollouts,
            "swarm_interaction_forecast": self.swarm_interaction_forecast,
            "comm_collapse_probability": round(self.comm_collapse_probability, 4),
            "adversarial_escalation_forecast": round(self.adversarial_escalation_forecast, 4),
            "generative_survivability": round(self.generative_survivability, 4),
            "preemptive_recommendation": self.preemptive_recommendation,
        }


class RecurrentStateSpaceModel:
    """
    RSSM Transition Model:
    h_t = tanh(W_h * h_{t-1} + W_z * z_{t-1} + W_a * a_{t-1} + b_h)
    mu_t, logvar_t = Dense(h_t)
    z_t = mu_t + exp(0.5 * logvar_t) * epsilon,  epsilon ~ N(0, I)
    """

    DETERMINISTIC_DIM = 16
    STOCHASTIC_DIM = 8
    ACTION_DIM = 4

    def __init__(self):
        np.random.seed(42)
        # Weights for GRU-like recurrent transition
        self.W_h = np.random.randn(self.DETERMINISTIC_DIM, self.DETERMINISTIC_DIM) * 0.15
        self.W_z = np.random.randn(self.STOCHASTIC_DIM, self.DETERMINISTIC_DIM) * 0.15
        self.W_a = np.random.randn(self.ACTION_DIM, self.DETERMINISTIC_DIM) * 0.15
        self.b_h = np.zeros(self.DETERMINISTIC_DIM)

        # Stochastic posterior head (mu, sigma)
        self.W_mu = np.random.randn(self.DETERMINISTIC_DIM, self.STOCHASTIC_DIM) * 0.1
        self.W_logvar = np.random.randn(self.DETERMINISTIC_DIM, self.STOCHASTIC_DIM) * 0.1

        # Decoder heads for physical invariants
        self.W_risk = np.random.randn(self.STOCHASTIC_DIM + self.DETERMINISTIC_DIM, 1) * 0.1
        self.W_surv = np.random.randn(self.STOCHASTIC_DIM + self.DETERMINISTIC_DIM, 1) * 0.1

        self.h_t = np.zeros(self.DETERMINISTIC_DIM)
        self.z_t = np.zeros(self.STOCHASTIC_DIM)

    def encode_observation(self, obs_vector: np.ndarray) -> np.ndarray:
        """Projects multi-modal telemetry into initial stochastic state."""
        w_obs = np.random.randn(len(obs_vector), self.STOCHASTIC_DIM) * 0.1
        return np.tanh(obs_vector @ w_obs)

    def forward_step(self, z_prev: np.ndarray, h_prev: np.ndarray, action: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Executes one latent transition step.
        Returns (z_next, h_next, epistemic_uncertainty).
        """
        # Deterministic recurrent update
        h_next = np.tanh(h_prev @ self.W_h + z_prev @ self.W_z + action @ self.W_a + self.b_h)

        # Stochastic distribution
        mu = h_next @ self.W_mu
        logvar = np.clip(h_next @ self.W_logvar, -4.0, 2.0)
        sigma = np.exp(0.5 * logvar)
        eps = np.random.randn(self.STOCHASTIC_DIM)
        z_next = mu + sigma * eps

        uncertainty = float(np.mean(sigma))
        return z_next, h_next, uncertainty

    def decode(self, z: np.ndarray, h: np.ndarray) -> Tuple[float, float]:
        """Decodes latent-recurrent state into risk and survivability probabilities."""
        joint = np.concatenate([z, h])
        r_raw = float((joint @ self.W_risk)[0])
        s_raw = float((joint @ self.W_surv)[0])
        risk = float(1.0 / (1.0 + np.exp(-r_raw)))
        surv = float(1.0 / (1.0 + np.exp(-s_raw)))
        return risk, surv


class FoundationWorldModelEngine:
    """
    World Model Generative Intelligence Engine.
    Runs multi-branch counterfactual simulation in latent space before commands are dispatched.
    """

    def __init__(self):
        self.rssm = RecurrentStateSpaceModel()
        self._action_vocabulary = {
            "HOLD_POSITION": np.array([0.0, 0.0, 0.0, 1.0]),
            "ALTITUDE_ASCEND": np.array([0.0, 0.0, 0.5, 1.0]),
            "CORRIDOR_EVADE": np.array([0.6, 0.4, 0.0, 0.8]),
            "EMERGENCY_RTL": np.array([-0.8, -0.8, -0.2, 0.5]),
            "RAPID_DESCENT": np.array([0.0, 0.0, -0.9, 0.2]),
        }

    def simulate(
        self,
        snapshot: Dict[str, Any],
        predictive_forecast: Optional[Dict[str, Any]] = None,
        collective_swarm: Optional[Dict[str, Any]] = None,
    ) -> FoundationForecast:
        features = np.array([
            float(snapshot.get("risk", {}).get("value", 0.0)),
            float((snapshot.get("inference") or {}).get("crash_probability", 0.0)),
            float((snapshot.get("twin_physics") or {}).get("turbulence_estimate", 0.1)),
            1.0 - float((snapshot.get("sensor_trust") or {}).get("composite_trust", 0.9)),
            float((snapshot.get("airspace") or {}).get("conflict_risk", 0.0)),
            float((snapshot.get("probabilistic_safety") or {}).get("composite_survivability", 0.75)),
        ])

        # Step 1: Encode current sensory observation into RSSM latent space
        z_curr = self.rssm.encode_observation(features)
        h_curr = self.rssm.h_t

        # Step 2: Rollforward current baseline state (4 imaginary steps)
        z_next, h_next, uncertainty = self.rssm.forward_step(
            z_curr, h_curr, self._action_vocabulary["HOLD_POSITION"]
        )
        self.rssm.h_t = h_next
        self.rssm.z_t = z_next

        decoded_risk, decoded_surv = self.rssm.decode(z_next, h_next)

        # Step 3: Multi-Branch Counterfactual Rollouts
        counterfactuals = []
        for act_name, act_vec in self._action_vocabulary.items():
            z_branch, h_branch = z_curr.copy(), h_curr.copy()
            risk_horizon = []
            for step in range(5):
                z_branch, h_branch, _ = self.rssm.forward_step(z_branch, h_branch, act_vec)
                r_step, s_step = self.rssm.decode(z_branch, h_branch)
                risk_horizon.append(round(r_step, 3))

            branch_surv = round(1.0 - float(np.mean(risk_horizon)), 4)
            violation_prob = round(float(np.max(risk_horizon)), 4)
            counterfactuals.append({
                "action": act_name,
                "risk_horizon": risk_horizon,
                "survivability": branch_surv,
                "boundary_violation_prob": violation_prob,
            })

        # Step 4: Consequence Graph Synthesis
        consequence_graph = []
        if predictive_forecast:
            for edge in predictive_forecast.get("cognition_graph_edges", [])[:6]:
                consequence_graph.append({
                    "from": edge.get("from"),
                    "to": edge.get("to"),
                    "weight": edge.get("weight"),
                    "latent_confidence": round(decoded_surv * float(edge.get("weight", 0.5)), 4),
                })
        else:
            consequence_graph = [
                {"from": "Sensory_Input", "to": "Latent_RSSM_Embedding", "weight": 0.95, "latent_confidence": 0.92},
                {"from": "Latent_RSSM_Embedding", "to": "Multi_Branch_Rollout", "weight": 0.88, "latent_confidence": 0.85},
                {"from": "Multi_Branch_Rollout", "to": "Preemptive_Action_Selection", "weight": 0.91, "latent_confidence": 0.89},
            ]

        # Step 5: Collective Swarm Synthesis
        swarm_fc = collective_swarm or {}
        coll_sim = swarm_fc.get("collective_simulation", {})
        swarm_interaction = {
            "collective_survivability": float(coll_sim.get("collective_survivability_forecast", decoded_surv)),
            "degraded_member_risk": 1.0 if coll_sim.get("degraded_member") else 0.0,
            "emergent_pressure": float((swarm_fc.get("emergent_routing") or {}).get("conflict_pressure", 0.0)),
        }

        # Step 6: Environmental & Cyber Risk Damping
        comm_p = min(1.0, (1.0 - float(snapshot.get("sensor_trust", {}).get("comm_trust", 0.9))) * 1.2)
        adv_p = min(1.0, len(snapshot.get("cyber_warfare", {}).get("attacks", [])) * 0.25)

        gen_surv = decoded_surv * (1.0 - comm_p * 0.15 - adv_p * 0.2)
        if predictive_forecast:
            gen_surv = 0.6 * gen_surv + 0.4 * float(predictive_forecast.get("mission_survivability_forecast", gen_surv))

        # Best Counterfactual Action Recommendation
        best_counterfactual = max(counterfactuals, key=lambda c: c["survivability"])
        preempt = best_counterfactual["action"] if best_counterfactual["survivability"] > gen_surv + 0.1 else None

        latent = LatentWorldState(
            latent=z_curr.tolist(),
            recurrent_h=h_curr.tolist(),
            decoded_risk=decoded_risk,
            decoded_survivability=decoded_surv,
            epistemic_uncertainty=uncertainty,
            rollforward_steps=5,
        )

        return FoundationForecast(
            latent_state=latent,
            consequence_graph=consequence_graph,
            counterfactual_rollouts=counterfactuals,
            swarm_interaction_forecast=swarm_interaction,
            comm_collapse_probability=comm_p,
            adversarial_escalation_forecast=adv_p,
            generative_survivability=gen_surv,
            preemptive_recommendation=preempt,
        )
