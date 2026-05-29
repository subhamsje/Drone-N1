"""Global cognition fabric — planetary-scale federated autonomy."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger("cognition_fabric")


@dataclass
class RegionalZone:
    zone_id: str
    region: str
    autonomy_authority: str  # edge | regional | cloud
    fleet_partitions: List[str]
    learning_generation: int = 0
    disconnected: bool = False

    def to_dict(self) -> Dict:
        return self.__dict__


class GlobalCognitionFabric:
    """Planetary fleet intelligence with regional learning propagation."""

    def __init__(self):
        self._zones: Dict[str, RegionalZone] = {
            "us-west": RegionalZone("us-west", "us-west-2", "edge", ["swarm-alpha-1"]),
            "eu-central": RegionalZone("eu-central", "eu-central-1", "regional", []),
            "ap-south": RegionalZone("ap-south", "ap-south-1", "regional", []),
            "defense-theater": RegionalZone("defense-theater", "classified", "edge", [], 0, False),
        }
        self._sync_buffer: List[Dict] = []
        self._global_learning_gen = 0

    def sync_regional_learning(self, zone_id: str, learning_export: Dict[str, Any]):
        if zone_id in self._zones:
            self._zones[zone_id].learning_generation += 1
        self._sync_buffer.append({"zone": zone_id, "learning": learning_export, "ts": time.time()})
        self._global_learning_gen += 1

    def propagate_to_fleet(self, target_zone: str) -> Dict[str, Any]:
        """Merge learning from all zones into target."""
        merged_weights = {}
        for entry in self._sync_buffer[-50:]:
            w = entry.get("learning", {}).get("recommended_weights", {})
            for k, v in w.items():
                merged_weights[k] = merged_weights.get(k, 0) + v
        if merged_weights:
            total = sum(merged_weights.values())
            merged_weights = {k: v/total for k, v in merged_weights.items()}
        return {"target_zone": target_zone, "merged_weights": merged_weights, "global_gen": self._global_learning_gen}

    def get_fabric_status(self) -> Dict[str, Any]:
        return {
            "zones": [z.to_dict() for z in self._zones.values()],
            "global_learning_generation": self._global_learning_gen,
            "pending_sync": len(self._sync_buffer),
        }
