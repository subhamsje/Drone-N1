"""Edge-cloud synchronization — offline queue, conflict resolution."""

import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional

logger = logging.getLogger("edge_sync")


@dataclass
class SyncRecord:
    key: str
    uav_id: str
    payload: Dict[str, Any]
    timestamp: float
    source: str  # edge | cloud
    version: int = 0


class EdgeCloudSyncEngine:
    """
    Hybrid deployment sync:
    - Edge wins: recovery commands
    - Cloud wins: mission waypoints
    - Merge: fleet map (LWW)
    """

    def __init__(self, uav_id: str):
        self.uav_id = uav_id
        self._edge_state: Dict[str, SyncRecord] = {}
        self._cloud_state: Dict[str, SyncRecord] = {}
        self._offline_queue: Deque[SyncRecord] = deque(maxlen=10_000)
        self._connected = True

    def set_connected(self, connected: bool):
        self._connected = connected
        if connected:
            asyncio_drain = len(self._offline_queue)
            logger.info("Edge reconnected — draining %d queued records", asyncio_drain)

    def push_edge(self, key: str, payload: Dict[str, Any], version: int = 0):
        rec = SyncRecord(key=key, uav_id=self.uav_id, payload=payload, timestamp=time.time(), source="edge", version=version)
        self._edge_state[key] = rec
        if not self._connected:
            self._offline_queue.append(rec)
        return rec

    def push_cloud(self, key: str, payload: Dict[str, Any], version: int = 0):
        rec = SyncRecord(key=key, uav_id=self.uav_id, payload=payload, timestamp=time.time(), source="cloud", version=version)
        self._cloud_state[key] = rec
        return rec

    def resolve(self, key: str, authority: str = "edge") -> Optional[Dict[str, Any]]:
        edge = self._edge_state.get(key)
        cloud = self._cloud_state.get(key)
        if authority == "edge" and edge:
            return edge.payload
        if authority == "cloud" and cloud:
            return cloud.payload
        if edge and cloud:
            winner = edge if edge.version >= cloud.version else cloud
            if edge.version == cloud.version:
                winner = edge if edge.timestamp >= cloud.timestamp else cloud
            return winner.payload
        return (edge or cloud).payload if (edge or cloud) else None

    def drain_offline_queue(self) -> List[Dict]:
        drained = [r.payload for r in self._offline_queue]
        self._offline_queue.clear()
        return drained

    def get_sync_status(self) -> Dict[str, Any]:
        return {
            "uav_id": self.uav_id,
            "connected": self._connected,
            "edge_keys": len(self._edge_state),
            "cloud_keys": len(self._cloud_state),
            "offline_pending": len(self._offline_queue),
        }
