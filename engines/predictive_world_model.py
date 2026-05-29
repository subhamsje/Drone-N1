"""Predictive world model — future-state simulation before action."""

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("predictive_world")


@dataclass
class FutureStateNode:
    horizon_s: float
    state_key: str
    probability: float
    severity: float
    consequence: str

    def to_dict(self) -> Dict:
        return {
            "horizon_s": self.horizon_s,
            "state_key": self.state_key,
            "probability": round(self.probability, 4),
            "severity": round(self.severity, 4),
            "consequence": self.consequence,
        }


@dataclass
class WorldModelForecast:
    horizon_s: float
    nodes: List[FutureStateNode]
    mission_survivability_forecast: float
    landing_success_forecast: float
    recommended_preemptive_action: Optional[str]
    cognition_graph_edges: List[Tuple[str, str, float]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "horizon_s": self.horizon_s,
            "nodes": [n.to_dict() for n in self.nodes],
            "mission_survivability_forecast": round(self.mission_survivability_forecast, 4),
            "landing_success_forecast": round(self.landing_success_forecast, 4),
            "recommended_preemptive_action": self.recommended_preemptive_action,
            "cognition_graph_edges": [
                {"from": a, "to": b, "weight": round(w, 4)} for a, b, w in self.cognition_graph_edges
            ],
        }


class PredictiveWorldModelEngine:
    """
    Internal consequence simulation — turbulence, collision, mission degradation,
    perception collapse, comm degradation, adversarial conditions.
    """

    HORIZONS = (0.5, 2.0, 5.0, 15.0)

    def __init__(self):
        self._history_surv: List[float] = []

    def simulate(
        self,
        snapshot: Dict[str, Any],
        airspace: Optional[Dict] = None,
        collective_risk: float = 0.0,
    ) -> WorldModelForecast:
        physics = snapshot.get("physics", {})
        risk = float(snapshot.get("risk", {}).get("value", 0))
        turb = float(snapshot.get("twin_physics", {}).get("turbulence_estimate", 0.1))
        crash_p = float(snapshot.get("inference", {}).get("crash_probability", 0))
        perc = snapshot.get("multimodal_perception", {}) or snapshot.get("perception_health", {})
        fusion_conf = float(perc.get("fusion_confidence", perc.get("overall_confidence", 0.8)))
        comm = float(snapshot.get("sensor_trust", {}).get("comm_trust", 0.9))
        cyber = snapshot.get("cyber_warfare", {})
        attack_conf = max(
            (a.get("conf", 0) for a in cyber.get("attacks", []) if isinstance(a, dict)),
            default=0.0,
        )

        nodes: List[FutureStateNode] = []
        edges: List[Tuple[str, str, float]] = []

        for h in self.HORIZONS:
            turb_prop = min(1.0, turb * (1.0 + 0.15 * h))
            nodes.append(FutureStateNode(
                h, "turbulence_propagation", turb_prop, turb_prop * 0.7,
                "instability_escalation" if turb_prop > 0.6 else "stable",
            ))
            edges.append(("current", f"turbulence_{h}s", turb_prop))

            coll_p = min(1.0, float((airspace or {}).get("conflict_risk", 0)) * (1.0 + h / 10))
            if coll_p > 0.2:
                nodes.append(FutureStateNode(
                    h, "collision_trajectory", coll_p, coll_p,
                    "deconflict_required",
                ))
                edges.append(("position", f"collision_{h}s", coll_p))

            miss_deg = min(1.0, risk * 0.5 + crash_p * 0.4 + (1 - fusion_conf) * 0.3)
            nodes.append(FutureStateNode(
                h, "mission_degradation", miss_deg, miss_deg * 0.8,
                "mission_abort_risk" if miss_deg > 0.65 else "continuity_ok",
            ))

            if fusion_conf < 0.5:
                pc = min(1.0, (0.5 - fusion_conf) * (1 + h / 5))
                nodes.append(FutureStateNode(h, "perception_collapse", pc, pc, "degraded_vision_survival"))
                edges.append(("perception", f"collapse_{h}s", pc))

            if comm < 0.6:
                nodes.append(FutureStateNode(
                    h, "comm_degradation", 1 - comm, 0.6, "edge_autonomy_required",
                ))

            if attack_conf > 0.3:
                nodes.append(FutureStateNode(
                    h, "adversarial_escalation", attack_conf, attack_conf, "cyber_containment",
                ))

        landing_p = float(snapshot.get("probabilistic_safety", {}).get("landing_success_probability", 0.85))
        landing_forecast = landing_p * (1.0 - turb * 0.2 - (1 - fusion_conf) * 0.15)
        nodes.append(FutureStateNode(5.0, "landing_survivability", 1 - landing_forecast, 1 - landing_forecast,
                                     "rtl_if_low" if landing_forecast < 0.5 else "land_ok"))

        surv = float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.75))
        mission_forecast = surv * (1.0 - collective_risk * 0.1 - crash_p * 0.2)
        self._history_surv.append(mission_forecast)
        if len(self._history_surv) > 100:
            self._history_surv = self._history_surv[-50:]

        coll_p = float((airspace or {}).get("conflict_risk", 0))
        preempt = None
        worst = max((n.severity * n.probability for n in nodes), default=0)
        if worst > 0.55:
            preempt = "PREEMPTIVE_DEESCALATE" if turb > 0.5 else "PREEMPTIVE_REROUTE" if coll_p > 0.5 else "PREEMPTIVE_RTL"

        return WorldModelForecast(
            horizon_s=max(self.HORIZONS),
            nodes=nodes,
            mission_survivability_forecast=mission_forecast,
            landing_success_forecast=landing_forecast,
            recommended_preemptive_action=preempt,
            cognition_graph_edges=edges[:12],
        )
