"""Semantic mission planning — intent to plan, route, contingencies."""

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from engines.route_governance import RouteGovernanceEngine

logger = logging.getLogger("semantic_planner")


@dataclass
class MissionWaypoint:
    lat: float
    lon: float
    alt_m: float
    label: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"lat": self.lat, "lon": self.lon, "altM": self.alt_m, "label": self.label}


@dataclass
class ContingencyPlan:
    trigger: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"trigger": self.trigger, "action": self.action, "params": self.params}


@dataclass
class SemanticMissionPlan:
    plan_id: str
    intent: str
    constraints: Dict[str, Any]
    waypoints: List[MissionWaypoint]
    contingencies: List[ContingencyPlan]
    recovery_strategy: str
    estimated_duration_s: float
    max_risk: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "intent": self.intent,
            "constraints": self.constraints,
            "waypoints": [w.to_dict() for w in self.waypoints],
            "contingencies": [c.to_dict() for c in self.contingencies],
            "recovery_strategy": self.recovery_strategy,
            "estimated_duration_s": self.estimated_duration_s,
            "max_risk": self.max_risk,
        }


class SemanticMissionPlanner:
    """Altaria plans WHY/WHERE/WHEN — autopilot plans HOW."""

    def __init__(self):
        self._routing = RouteGovernanceEngine()

    def plan_from_intent(
        self,
        intent: str,
        origin: Dict[str, float],
        geospatial_context: Optional[Dict[str, Any]] = None,
        operator_waypoints: Optional[List[Dict[str, Any]]] = None,
    ) -> SemanticMissionPlan:
        constraints = self._routing.parse_semantic_intent(intent)
        il = intent.lower()
        if "battery" in il or "energy" in il:
            constraints["minimize_battery"] = True
        if "risk" in il or "safe" in il:
            constraints["max_risk"] = min(constraints.get("max_risk", 0.5), 0.35)
        if "inspect" in il or "solar" in il or "powerline" in il:
            constraints["pattern"] = "lawnmower"

        geo = geospatial_context or {}
        weather = geo.get("weather", {})
        turb = float(weather.get("turbulence_index", 0.15))
        max_risk = float(constraints.get("max_risk", 0.5))
        if turb > 0.4:
            max_risk = min(max_risk, 0.35)

        lat0 = float(origin.get("lat", 12.97))
        lon0 = float(origin.get("lon", 77.59))
        alt0 = float(origin.get("alt_m", 100.0))

        if operator_waypoints:
            wps = [
                MissionWaypoint(
                    float(w.get("lat", w.get("latitude", lat0))),
                    float(w.get("lon", w.get("longitude", lon0))),
                    float(w.get("altM", w.get("alt_m", alt0))),
                    str(w.get("label", f"WP{i}")),
                )
                for i, w in enumerate(operator_waypoints)
            ]
        else:
            wps = self._generate_pattern(lat0, lon0, alt0, constraints.get("pattern", "patrol"))

        contingencies = [
            ContingencyPlan("risk>0.7", "REROUTE", {"altitude_m": alt0 + 20}),
            ContingencyPlan("battery<25", "RETURN_HOME", {}),
            ContingencyPlan("gps_spoof", "HOLD", {"duration_s": 30}),
            ContingencyPlan("comm_loss>10s", "RETURN_HOME", {}),
        ]
        if constraints.get("avoid_populated"):
            contingencies.append(ContingencyPlan("terrain=HUMAN", "REROUTE", {"lateral_offset_m": 200}))

        recovery = "EMERGENCY_LAND" if "inspect" in il else "RETURN_HOME"
        duration = len(wps) * 120.0 * (1.0 + turb)

        return SemanticMissionPlan(
            plan_id=str(uuid.uuid4())[:12],
            intent=intent,
            constraints=constraints,
            waypoints=wps,
            contingencies=contingencies,
            recovery_strategy=recovery,
            estimated_duration_s=duration,
            max_risk=max_risk,
        )

    def _generate_pattern(self, lat: float, lon: float, alt: float, pattern: str) -> List[MissionWaypoint]:
        d = 0.003 if pattern == "lawnmower" else 0.002
        return [
            MissionWaypoint(lat, lon, alt, "START"),
            MissionWaypoint(lat + d, lon, alt + 20, "LEG-1"),
            MissionWaypoint(lat + d, lon + d * 0.5, alt + 15, "LEG-2"),
            MissionWaypoint(lat, lon + d, alt + 10, "END"),
        ]
