"""Foundation world model — latent generative simulation before action."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("foundation_world")


@dataclass
class LatentWorldState:
    latent: List[float]
    decoded_risk: float
    decoded_survivability: float
    rollforward_steps: int

    def to_dict(self) -> Dict:
        return {
            "latent_dim": len(self.latent),
            "latent": [round(x, 4) for x in self.latent[:8]],
            "decoded_risk": round(self.decoded_risk, 4),
            "decoded_survivability": round(self.decoded_survivability, 4),
            "rollforward_steps": self.rollforward_steps,
        }


@dataclass
class FoundationForecast:
    latent_state: LatentWorldState
    consequence_graph: List[Dict]
    swarm_interaction_forecast: Dict[str, float]
    comm_collapse_probability: float
    adversarial_escalation_forecast: float
    generative_survivability: float
    preemptive_recommendation: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "latent_state": self.latent_state.to_dict(),
            "consequence_graph": self.consequence_graph,
            "swarm_interaction_forecast": self.swarm_interaction_forecast,
            "comm_collapse_probability": round(self.comm_collapse_probability, 4),
            "adversarial_escalation_forecast": round(self.adversarial_escalation_forecast, 4),
            "generative_survivability": round(self.generative_survivability, 4),
            "preemptive_recommendation": self.preemptive_recommendation,
        }


class FoundationWorldModelEngine:
    """
    Generative predictive cognition — latent encoding + multi-step rollforward.
    Extends PredictiveWorldModelEngine; does not replace it.
    """

    LATENT_DIM = 8

    def __init__(self):
        self._W_encode = np.random.randn(6, self.LATENT_DIM) * 0.1
        self._W_decode = np.random.randn(self.LATENT_DIM, 3) * 0.1
        self._latent_ema = np.zeros(self.LATENT_DIM)

    def encode(self, snapshot: Dict[str, Any]) -> np.ndarray:
        features = np.array([
            float(snapshot.get("risk", {}).get("value", 0)),
            float(snapshot.get("inference", {}).get("crash_probability", 0)),
            float(snapshot.get("twin_physics", {}).get("turbulence_estimate", 0.1)),
            1.0 - float(snapshot.get("sensor_trust", {}).get("composite_trust", 0.9)),
            float((snapshot.get("airspace") or {}).get("conflict_risk", 0)),
            float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.75)),
        ])
        z = np.tanh(features @ self._W_encode)
        self._latent_ema = 0.9 * self._latent_ema + 0.1 * z
        return z

    def rollforward(self, z: np.ndarray, steps: int = 4) -> List[np.ndarray]:
        trajectory = [z.copy()]
        for _ in range(steps - 1):
            z_next = np.tanh(0.85 * z + 0.15 * self._latent_ema + np.random.randn(self.LATENT_DIM) * 0.02)
            trajectory.append(z_next)
            z = z_next
        return trajectory

    def simulate(
        self,
        snapshot: Dict[str, Any],
        predictive_forecast: Optional[Dict] = None,
        collective_swarm: Optional[Dict] = None,
    ) -> FoundationForecast:
        z = self.encode(snapshot)
        traj = self.rollforward(z, steps=4)

        decoded = traj[-1] @ self._W_decode
        decoded_risk = float(np.clip(decoded[0], 0, 1))
        decoded_surv = float(np.clip(1.0 - decoded[1], 0, 1))

        consequence_graph = []
        if predictive_forecast:
            for edge in predictive_forecast.get("cognition_graph_edges", [])[:6]:
                consequence_graph.append({
                    "from": edge.get("from"),
                    "to": edge.get("to"),
                    "weight": edge.get("weight"),
                    "generative_confidence": round(decoded_surv * edge.get("weight", 0.5), 4),
                })

        swarm_fc = collective_swarm or {}
        coll_sim = swarm_fc.get("collective_simulation", {})
        swarm_interaction = {
            "collective_survivability": coll_sim.get("collective_survivability_forecast", decoded_surv),
            "degraded_member_risk": 1.0 if coll_sim.get("degraded_member") else 0.0,
            "emergent_pressure": float((swarm_fc.get("emergent_routing") or {}).get("conflict_pressure", 0)),
        }

        comm_p = min(1.0, (1.0 - float(snapshot.get("sensor_trust", {}).get("comm_trust", 0.9))) * 1.2)
        adv_p = min(1.0, len(snapshot.get("cyber_warfare", {}).get("attacks", [])) * 0.25)

        gen_surv = decoded_surv * (1.0 - comm_p * 0.15 - adv_p * 0.2)
        if predictive_forecast:
            gen_surv = 0.6 * gen_surv + 0.4 * float(predictive_forecast.get("mission_survivability_forecast", gen_surv))

        preempt = predictive_forecast.get("recommended_preemptive_action") if predictive_forecast else None
        if gen_surv < 0.4 and not preempt:
            preempt = "GENERATIVE_RTL"

        latent = LatentWorldState(
            latent=z.tolist(),
            decoded_risk=decoded_risk,
            decoded_survivability=decoded_surv,
            rollforward_steps=len(traj),
        )

        return FoundationForecast(
            latent_state=latent,
            consequence_graph=consequence_graph,
            swarm_interaction_forecast=swarm_interaction,
            comm_collapse_probability=comm_p,
            adversarial_escalation_forecast=adv_p,
            generative_survivability=gen_surv,
            preemptive_recommendation=preempt,
        )
