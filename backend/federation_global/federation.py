"""Global distributed infrastructure — regional zones, telemetry federation."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

logger = logging.getLogger("global.federation")


@dataclass
class RegionalZone:
    zone_id: str
    region: str
    edge_autonomous: bool
    kafka_bootstrap: str
    triton_endpoint: str
    fleet_ids: List[str] = field(default_factory=list)


class GlobalFederationController:
    """
    Multi-region cognition clusters with disconnected edge operation.
    """

    DEFAULT_ZONES = [
        RegionalZone("us-west", "us-west-2", True, "kafka-usw:9092", "triton-usw:8000", ["swarm-alpha-1"]),
        RegionalZone("eu-central", "eu-central-1", True, "kafka-eu:9092", "triton-eu:8000", []),
        RegionalZone("ap-south", "ap-south-1", True, "kafka-ap:9092", "triton-ap:8000", []),
    ]

    def __init__(self, home_zone: str = "us-west"):
        self._zones = {z.zone_id: z for z in self.DEFAULT_ZONES}
        self.home_zone = home_zone
        self._edge_disconnected = False
        self._federation_buffer: List[Dict] = []

    def set_edge_disconnected(self, disconnected: bool):
        self._edge_disconnected = disconnected

    def route_snapshot(self, snapshot: Dict[str, Any], uav_id: str) -> Dict[str, Any]:
        zone = self._zones.get(self.home_zone)
        snapshot["federation"] = {
            "home_zone": self.home_zone,
            "region": zone.region if zone else "unknown",
            "edge_disconnected": self._edge_disconnected,
            "buffered": len(self._federation_buffer),
        }
        if self._edge_disconnected:
            self._federation_buffer.append({"ts": time.time(), "uav_id": uav_id, "snap": snapshot})
            if len(self._federation_buffer) > 10_000:
                self._federation_buffer = self._federation_buffer[-5000:]
        return snapshot

    def drain_federation_buffer(self) -> List[Dict]:
        d = self._federation_buffer.copy()
        self._federation_buffer.clear()
        return d

    def list_zones(self) -> List[Dict]:
        return [
            {"zone_id": z.zone_id, "region": z.region, "fleets": z.fleet_ids}
            for z in self._zones.values()
        ]
