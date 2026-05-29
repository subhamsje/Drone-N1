"""Planetary autonomous federation — regional clusters, disconnected edge, cross-region sync."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger("planetary_federation")


@dataclass
class RegionalCluster:
    cluster_id: str
    authority: str  # edge | regional | planetary
    disconnected: bool
    mission_partition: str
    last_sync_ts: float
    learning_generation: int


class PlanetaryAutonomousFederation:
    """Extends cognition fabric with operational partitioning and governance."""

    def __init__(self):
        self._clusters: Dict[str, RegionalCluster] = {
            "us-west-edge": RegionalCluster("us-west-edge", "edge", False, "logistics-west", time.time(), 0),
            "eu-regional": RegionalCluster("eu-regional", "regional", False, "urban-mobility-eu", time.time(), 0),
            "ap-edge-disconnected": RegionalCluster("ap-edge-disconnected", "edge", True, "disaster-ap", time.time(), 0),
            "defense-theater": RegionalCluster("defense-theater", "edge", False, "contested-alpha", time.time(), 0),
        }
        self._governance_log: List[Dict] = []

    def partition_mission(self, mission_id: str, home_cluster: str) -> Dict[str, Any]:
        c = self._clusters.get(home_cluster)
        if not c:
            return {"error": "unknown_cluster"}
        self._governance_log.append({"mission": mission_id, "cluster": home_cluster, "ts": time.time()})
        return {
            "mission_id": mission_id,
            "home_cluster": home_cluster,
            "authority": c.authority,
            "edge_autonomous": c.disconnected,
        }

    def propagate_intelligence(self, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        propagated = 0
        for cid, cluster in self._clusters.items():
            if cid == source or cluster.disconnected:
                continue
            cluster.learning_generation += 1
            cluster.last_sync_ts = time.time()
            propagated += 1
        return {"source": source, "targets_synced": propagated, "payload_keys": list(payload.keys())}

    def get_planetary_status(self) -> Dict[str, Any]:
        return {
            "clusters": [
                {
                    "cluster_id": c.cluster_id,
                    "authority": c.authority,
                    "disconnected": c.disconnected,
                    "partition": c.mission_partition,
                    "learning_gen": c.learning_generation,
                }
                for c in self._clusters.values()
            ],
            "governance_events": len(self._governance_log),
        }
