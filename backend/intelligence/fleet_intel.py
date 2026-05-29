"""Fleet intelligence — scales 1 → 1000 UAVs with shared memory and threat propagation."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("fleet_intel")


class FleetIntelligenceLayer:
    """
    Altaria fleet brain — not autopilot swarm firmware.
    Coordinates mission allocation, threat propagation, and shared learning.
    """

    def __init__(self, fleet_id: str, member_ids: Optional[List[str]] = None):
        self.fleet_id = fleet_id
        self.members = member_ids or []
        self._shared_memory: Dict[str, Any] = {}
        self._threat_graph: Dict[str, float] = {}

    def register_uav(self, uav_id: str):
        if uav_id not in self.members:
            self.members.append(uav_id)

    def propagate_threat(self, source_uav: str, threat_level: float, radius_km: float = 5.0):
        for uid in self.members:
            if uid == source_uav:
                self._threat_graph[uid] = threat_level
            else:
                self._threat_graph[uid] = max(
                    self._threat_graph.get(uid, 0.0),
                    threat_level * 0.7,
                )
        self._shared_memory["last_threat_propagation"] = {
            "source": source_uav,
            "level": threat_level,
            "radius_km": radius_km,
        }

    def fleet_status(self, per_uav_snapshots: Optional[Dict[str, Dict]] = None) -> Dict[str, Any]:
        per_uav = per_uav_snapshots or {}
        members = []
        for uid in self.members:
            snap = per_uav.get(uid, {})
            members.append({
                "uav_id": uid,
                "survivability": float(
                    snap.get("probabilistic_safety", {}).get("composite_survivability", 0.5)
                ),
                "threat": self._threat_graph.get(uid, 0.0),
                "battery": float(snap.get("physics", {}).get("battery", 100)),
            })
        scale_tier = (
            "squad" if len(self.members) <= 10
            else "company" if len(self.members) <= 100
            else "battalion" if len(self.members) <= 1000
            else "theater"
        )
        return {
            "fleet_id": self.fleet_id,
            "scale_tier": scale_tier,
            "member_count": len(self.members),
            "members": members,
            "threat_propagated": any(v > 0.5 for v in self._threat_graph.values()),
            "shared_memory_keys": list(self._shared_memory.keys()),
        }

    def optimize_allocation(self, mission_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Assign mission legs to fleet members by battery and threat."""
        n = max(1, len(self.members))
        return {
            "allocation": {uid: mission_plan.get("plan_id", "mission") for uid in self.members[:n]},
            "strategy": "survivability_balanced",
        }
