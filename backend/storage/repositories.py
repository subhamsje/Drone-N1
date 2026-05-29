"""In-memory + optional PostgreSQL repositories for dev/production."""

import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional

logger = logging.getLogger("repositories")


@dataclass
class UAVStateCache:
    uav_id: str
    last_snapshot: Optional[Dict[str, Any]] = None
    last_risk: float = 0.0
    last_updated: float = 0.0
    status: str = "unknown"


class StateRepository:
    """Hot state cache — production backs with Redis."""

    def __init__(self, max_history_per_uav: int = 500):
        self._uavs: Dict[str, UAVStateCache] = {}
        self._telemetry_history: Dict[str, Deque[Dict]] = {}
        self._events: Deque[Dict] = deque(maxlen=50_000)
        self._max_history = max_history_per_uav

    def upsert_snapshot(self, uav_id: str, snapshot: Dict[str, Any]):
        if uav_id not in self._uavs:
            self._uavs[uav_id] = UAVStateCache(uav_id=uav_id)
        cache = self._uavs[uav_id]
        cache.last_snapshot = snapshot
        cache.last_risk = snapshot.get("risk", {}).get("value", 0.0)
        cache.last_updated = time.time()
        cache.status = snapshot.get("system_state", "unknown")

        hist = self._telemetry_history.setdefault(uav_id, deque(maxlen=self._max_history))
        hist.append(snapshot)

    def get_uav_state(self, uav_id: str) -> Optional[Dict[str, Any]]:
        cache = self._uavs.get(uav_id)
        return cache.last_snapshot if cache else None

    def list_uavs(self) -> List[Dict[str, Any]]:
        return [
            {
                "uav_id": c.uav_id,
                "status": c.status,
                "last_risk": c.last_risk,
                "last_updated": c.last_updated,
            }
            for c in self._uavs.values()
        ]

    def get_history(self, uav_id: str, limit: int = 100) -> List[Dict]:
        hist = self._telemetry_history.get(uav_id, deque())
        return list(hist)[-limit:]

    def append_event(self, event: Dict[str, Any]):
        self._events.append(event)

    def query_events(self, uav_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        out = list(self._events)
        if uav_id:
            out = [e for e in out if e.get("uav_id") == uav_id]
        return out[-limit:]


_repo: Optional[StateRepository] = None


def get_state_repository() -> StateRepository:
    global _repo
    if _repo is None:
        _repo = StateRepository()
    return _repo
