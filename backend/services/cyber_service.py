"""Cybersecurity backend — threat scoring, fleet-wide propagation."""

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

logger = logging.getLogger("cyber_service")


class CybersecurityService:
    """Wraps engines.cybersecurity for backend event emission."""

    def __init__(self, uav_id: str):
        self.uav_id = uav_id
        self._bus = get_event_bus()
        self._engine = None

    def _ensure_engine(self):
        if self._engine is None:
            from engines.cybersecurity import CybersecurityEngine
            from config.settings import CONFIG
            self._engine = CybersecurityEngine(CONFIG)

    def evaluate_from_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        cyber = snapshot.get("cybersecurity")
        if cyber:
            return cyber
        return {"threat_level": 0, "is_spoofed": False, "firewall_blocks": 0, "active_alarms": []}

    async def publish_threat(self, snapshot: Dict[str, Any]):
        cyber = self.evaluate_from_snapshot(snapshot)
        if float(cyber.get("threat_level", 0)) > 0.3 or cyber.get("is_spoofed"):
            await self._bus.publish(
                DomainEvent.create(EventType.CYBER_THREAT, self.uav_id, cyber),
                Topic.CYBER_THREAT,
            )
        if cyber.get("firewall_blocks", 0) > 0:
            await self._bus.publish(
                DomainEvent.create(
                    EventType.CYBER_BLOCKED,
                    self.uav_id,
                    {"blocks": cyber["firewall_blocks"]},
                ),
                Topic.CYBER_BLOCKED,
            )
