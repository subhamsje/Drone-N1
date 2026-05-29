"""Fleet cognition backend — aggregates swarm health, propagates alerts."""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backend.events.bus import get_event_bus
from backend.events.schemas import DomainEvent, EventType
from backend.events.topics import Topic

logger = logging.getLogger("fleet_service")


class FleetCoordinationService:
    """Distributed fleet cognition — wraps engines.fleet.FleetCognitionLayer."""

    def __init__(self, fleet_id: str, primary_uav_id: str = "Altaria-Alpha"):
        self.fleet_id = fleet_id
        self.primary_uav_id = primary_uav_id
        self._bus = get_event_bus()
        self._layer = None

    def _ensure_layer(self):
        if self._layer is None:
            from engines.fleet import FleetCognitionLayer
            self._layer = FleetCognitionLayer(self.primary_uav_id)

    def evaluate_from_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_layer()
        fleet_data = snapshot.get("fleet")
        if fleet_data:
            return fleet_data

        phys = snapshot.get("physics", {})
        risk = snapshot.get("risk", {})
        decision = snapshot.get("decision", {})
        cycle = snapshot.get("cycle", 0)

        status = self._layer.evaluate_fleet(
            float(phys.get("battery", 100)),
            float(risk.get("value", 0)),
            decision.get("action", "NONE"),
            int(cycle),
        )
        return {
            "fleet_health": status.fleet_health_score,
            "active_members": status.active_swarm_members,
            "threat_propagated": status.swarm_threat_propagated,
            "member_states": [
                {
                    "uav_id": m.uav_id,
                    "battery": m.battery,
                    "health_score": m.health_score,
                    "active_action": m.active_action,
                    "risk_level": m.risk_level,
                }
                for m in status.member_states
            ],
        }

    async def publish_fleet_health(self, snapshot: Dict[str, Any]):
        fleet = self.evaluate_from_snapshot(snapshot)
        await self._bus.publish(
            DomainEvent.create(
                EventType.FLEET_HEALTH,
                self.primary_uav_id,
                fleet,
                fleet_id=self.fleet_id,
            ),
            Topic.FLEET_HEALTH,
        )
        if fleet.get("threat_propagated"):
            await self._bus.publish(
                DomainEvent.create(
                    EventType.FLEET_ALERT,
                    self.primary_uav_id,
                    {"alert": "swarm_threat_propagated", "fleet": fleet},
                    fleet_id=self.fleet_id,
                ),
                Topic.FLEET_ALERT,
            )

    def get_fleet_summary(self) -> Dict[str, Any]:
        self._ensure_layer()
        return {
            "fleet_id": self.fleet_id,
            "primary_uav": self.primary_uav_id,
            "members": list(self._layer._members.keys()),
            "threat_propagated": self._layer.swarm_threat_propagated,
        }
