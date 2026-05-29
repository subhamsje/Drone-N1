"""
Advanced Route Governance — semantic airspace intelligence.
NOT waypoint navigation — intent-based dynamic routing.
"""

import logging
import numpy as np
from typing import Any, Dict, List, Optional

from core.cognitive_models import RouteGovernanceState

logger = logging.getLogger("route_governance")


class RouteGovernanceEngine:
    """Dynamic rerouting, weather/battery/risk-aware corridor governance."""

    def __init__(self):
        self._no_fly_zones: List[Dict] = []
        self._learned_hazards: List[Dict] = []

    def set_geofence(self, bounds: Dict[str, float]):
        self._no_fly_zones = [{"type": "geofence", "bounds": bounds}]

    def add_learned_hazard(self, hazard: Dict[str, Any]):
        self._learned_hazards.append(hazard)
        if len(self._learned_hazards) > 100:
            self._learned_hazards = self._learned_hazards[-100:]

    def evaluate(
        self,
        snapshot: Dict[str, Any],
        mission_intent: Optional[str] = None,
        position: tuple = (0.0, 0.0),
        battery_reserve_pct: float = 20.0,
    ) -> RouteGovernanceState:
        risk = float(snapshot.get("risk", {}).get("value", 0))
        battery = float(snapshot.get("physics", {}).get("battery", 100))
        nav = snapshot.get("navigation", {}) or {}
        weather = float(nav.get("weather_hazard", 0))
        fleet = snapshot.get("fleet", {}) or {}

        corridor_risk = float(np.clip(risk * 0.6 + weather * 0.4, 0, 1))
        battery_feasible = battery > battery_reserve_pct + 10
        no_fly = self._check_no_fly(position)
        congestion = 0.3 if fleet.get("threat_propagated") else 0.1

        reroute = corridor_risk > 0.55 or not battery_feasible or no_fly or weather > 0.7

        # Semantic compliance — keyword heuristics for intent
        compliance = 1.0
        if mission_intent:
            intent_lower = mission_intent.lower()
            if "populated" in intent_lower and nav.get("terrain_type") == "HUMAN":
                compliance = 0.2
            if "minimize battery" in intent_lower and battery < 40:
                compliance = 0.5
            if "avoid" in intent_lower and corridor_risk > 0.4:
                compliance = max(0.3, 1.0 - corridor_risk)

        alt = 30.0 if weather > 0.6 else 15.0 if risk > 0.5 else 10.0

        return RouteGovernanceState(
            reroute_required=reroute,
            corridor_risk=corridor_risk,
            battery_feasible=battery_feasible,
            no_fly_violation=no_fly,
            semantic_compliance=compliance,
            recommended_altitude_m=alt,
            congestion_level=congestion,
        )

    def _check_no_fly(self, position: tuple) -> bool:
        x, y = position[0], position[1]
        for zone in self._no_fly_zones:
            b = zone.get("bounds", {})
            if b.get("min_x", -1e9) <= x <= b.get("max_x", 1e9):
                if b.get("min_y", -1e9) <= y <= b.get("max_y", 1e9):
                    return True
        return False

    def parse_semantic_intent(self, intent: str) -> Dict[str, Any]:
        """Extract routing constraints from natural language mission intent."""
        constraints = {"avoid_populated": False, "minimize_battery": False, "max_risk": 0.5}
        il = intent.lower()
        if "populated" in il or "human" in il or "civilian" in il:
            constraints["avoid_populated"] = True
            constraints["max_risk"] = 0.3
        if "battery" in il or "efficient" in il:
            constraints["minimize_battery"] = True
        if "safe" in il:
            constraints["max_risk"] = 0.35
        return constraints
