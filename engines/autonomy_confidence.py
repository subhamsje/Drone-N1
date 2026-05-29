"""Autonomy Confidence Engine — uncertainty-aware mission scaling."""

import logging
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger("autonomy_confidence")


@dataclass
class ConfidenceState:
    global_uncertainty: float
    perception_reliability: float
    prediction_reliability: float
    navigation_reliability: float
    degraded_mode: str  # NOMINAL | DEGRADED | MINIMAL | MANUAL_REQUIRED
    safety_margin_multiplier: float
    max_aggression: float
    operator_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in self.__dict__.items()}


class AutonomyConfidenceEngine:
    """Knows when uncertain — adapts margins and autonomy state."""

    def evaluate(
        self,
        snapshot: Dict[str, Any],
        sensor_trust: Dict[str, Any],
        perception: Optional[Dict] = None,
    ) -> ConfidenceState:
        ekf_c = float(snapshot.get("ekf", {}).get("confidence", 0.9))
        anom_u = float(snapshot.get("anomaly", {}).get("uncertainty", 0))
        pred_c = float(snapshot.get("prediction", {}).get("confidence", 0.8))
        inf_c = float(snapshot.get("inference", {}).get("model_confidence", 0.85))
        fusion = float(sensor_trust.get("fusion_confidence", 0.9))
        vis_c = float(sensor_trust.get("vision_confidence", 0.85))
        nav_mode = snapshot.get("navigation_state", {}).get("mode", "gps")
        nav_rel = 0.9 if nav_mode == "gps" else 0.6 if nav_mode in ("vio", "slam") else 0.35

        perc_rel = 1.0 - float((perception or {}).get("obstacle_density", 0.2)) * 0.3
        pred_rel = pred_c * inf_c

        global_u = float(np.clip(
            (1 - ekf_c) * 0.2 + anom_u * 0.2 + (1 - fusion) * 0.25
            + (1 - pred_rel) * 0.15 + (1 - nav_rel) * 0.2,
            0, 1,
        ))

        if global_u > 0.75:
            degraded = "MANUAL_REQUIRED"
            margin = 2.5
            max_agg = 0.1
            op_req = True
        elif global_u > 0.55:
            degraded = "MINIMAL"
            margin = 2.0
            max_agg = 0.25
            op_req = False
        elif global_u > 0.35:
            degraded = "DEGRADED"
            margin = 1.5
            max_agg = 0.5
            op_req = False
        else:
            degraded = "NOMINAL"
            margin = 1.0
            max_agg = 1.0
            op_req = False

        return ConfidenceState(
            global_uncertainty=global_u,
            perception_reliability=perc_rel,
            prediction_reliability=pred_rel,
            navigation_reliability=nav_rel,
            degraded_mode=degraded,
            safety_margin_multiplier=margin,
            max_aggression=max_agg,
            operator_required=op_req,
        )
