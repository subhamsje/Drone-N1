"""Mission governance — semantic missions, geofencing, dynamic reroute."""

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.events.bus import get_event_bus
from backend.events.schemas import DomainEvent, EventType
from backend.events.topics import Topic

logger = logging.getLogger("mission_service")


@dataclass
class SemanticMission:
    mission_id: str
    fleet_id: str
    name: str
    intent: str
    objectives: List[str] = field(default_factory=list)
    status: str = "active"
    geofence: Optional[Dict] = None
    assigned_uavs: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "fleet_id": self.fleet_id,
            "name": self.name,
            "intent": self.intent,
            "objectives": self.objectives,
            "status": self.status,
            "geofence": self.geofence,
            "assigned_uavs": self.assigned_uavs,
            "created_at": self.created_at,
        }


class MissionGovernanceService:
    """Intent-based mission orchestration — not waypoint-only navigation."""

    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self._missions: Dict[str, SemanticMission] = {}
        self._bus = get_event_bus()

    def create_mission(
        self,
        name: str,
        intent: str,
        objectives: Optional[List[str]] = None,
        geofence: Optional[Dict] = None,
        uav_ids: Optional[List[str]] = None,
    ) -> SemanticMission:
        mid = str(uuid.uuid4())
        m = SemanticMission(
            mission_id=mid,
            fleet_id=self.fleet_id,
            name=name,
            intent=intent,
            objectives=objectives or [],
            geofence=geofence,
            assigned_uavs=uav_ids or [],
        )
        self._missions[mid] = m
        return m

    def list_missions(self) -> List[Dict]:
        return [m.to_dict() for m in self._missions.values()]

    def get_mission(self, mission_id: str) -> Optional[Dict]:
        m = self._missions.get(mission_id)
        return m.to_dict() if m else None

    async def evaluate_reroute(self, snapshot: Dict[str, Any], mission_id: str) -> Optional[Dict]:
        m = self._missions.get(mission_id)
        if not m or m.status != "active":
            return None

        risk = float(snapshot.get("risk", {}).get("value", 0))
        nav = snapshot.get("navigation", {})
        weather = float(nav.get("weather_hazard", 0))

        if risk > 0.6 or weather > 0.7:
            reroute = {
                "mission_id": mission_id,
                "reason": "risk_or_weather",
                "risk_value": risk,
                "weather_hazard": weather,
                "recommended_action": snapshot.get("decision", {}).get("action"),
            }
            await self._bus.publish(
                DomainEvent.create(
                    EventType.MISSION_REROUTE,
                    snapshot.get("uav_id", "unknown"),
                    reroute,
                ),
                Topic.MISSION_REROUTE,
            )
            return reroute
        return None

    def check_geofence(self, position: tuple, mission_id: str) -> bool:
        m = self._missions.get(mission_id)
        if not m or not m.geofence:
            return True
        bounds = m.geofence.get("bounds", {})
        x, y = position[0], position[1]
        return (
            bounds.get("min_x", -1e9) <= x <= bounds.get("max_x", 1e9)
            and bounds.get("min_y", -1e9) <= y <= bounds.get("max_y", 1e9)
        )
