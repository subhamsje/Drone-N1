"""Foundation world cognition — uncertainty propagation and future-state graphs."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger("world_cognition")


@dataclass
class UncertaintyPropagation:
    perception_uncertainty: float
    navigation_uncertainty: float
    mission_uncertainty: float
    composite_uncertainty: float
    propagated_nodes: List[Dict]

    def to_dict(self) -> Dict:
        return {
            "perception_uncertainty": round(self.perception_uncertainty, 4),
            "navigation_uncertainty": round(self.navigation_uncertainty, 4),
            "mission_uncertainty": round(self.mission_uncertainty, 4),
            "composite_uncertainty": round(self.composite_uncertainty, 4),
            "propagated_nodes": self.propagated_nodes,
        }


class WorldCognitionEngine:
    """Extends foundation forecasts with uncertainty DAG and environment evolution."""

    def __init__(self):
        self._environment_ema: Dict[str, float] = {}

    def propagate_uncertainty(
        self,
        snapshot: Dict[str, Any],
        foundation: Dict[str, Any],
        world_model: Optional[Dict] = None,
    ) -> UncertaintyPropagation:
        perc_u = float((snapshot.get("adversarial_perception") or {}).get("uncertainty_bound", 0.3))
        nav_u = float(snapshot.get("confidence", {}).get("global_uncertainty", 0.3))
        miss_u = 1.0 - float(foundation.get("generative_survivability", 0.75))

        nodes = []
        if world_model:
            for n in world_model.get("nodes", [])[:4]:
                nodes.append({
                    "key": n.get("state_key"),
                    "horizon_s": n.get("horizon_s"),
                    "uncertainty": round(n.get("probability", 0) * n.get("severity", 0), 4),
                })

        composite = float(np.clip(0.35 * perc_u + 0.35 * nav_u + 0.3 * miss_u, 0, 1))

        env_key = snapshot.get("embodied_cognition", {}).get("weather_signature_id", "wx_0")
        self._environment_ema[env_key] = 0.9 * self._environment_ema.get(env_key, 0.2) + 0.1 * composite

        return UncertaintyPropagation(
            perception_uncertainty=perc_u,
            navigation_uncertainty=nav_u,
            mission_uncertainty=miss_u,
            composite_uncertainty=composite,
            propagated_nodes=nodes,
        )

    def build_future_cognition_graph(
        self,
        foundation: Dict[str, Any],
        uncertainty: UncertaintyPropagation,
    ) -> Dict[str, Any]:
        edges = list(foundation.get("consequence_graph", []))
        edges.append({
            "from": "uncertainty_root",
            "to": "generative_survivability",
            "weight": uncertainty.composite_uncertainty,
        })
        return {
            "graph_id": f"wc-{int(uncertainty.composite_uncertainty * 1000)}",
            "nodes": len(edges) + 1,
            "edges": edges[:10],
            "environment_evolution": dict(self._environment_ema),
        }
