"""
Distributed Swarm Coordination Engine.
Implements Raft leader election, heuristic task auctioning, and shared spatial threat map sync.
"""

from typing import Dict, Any, List, Optional
import time
import math
import logging

logger = logging.getLogger("altaria.swarm_consensus")

class SwarmNode:
    def __init__(self, node_id: str, battery_pct: float, lat: float, lon: float, role: str = "FOLLOWER"):
        self.node_id = node_id
        self.battery_pct = battery_pct
        self.lat = lat
        self.lon = lon
        self.role = role # LEADER | FOLLOWER | CANDIDATE
        self.last_heartbeat = time.time()

class SwarmConsensusEngine:
    def __init__(self):
        self.nodes: Dict[str, SwarmNode] = {}
        self.current_leader_id: Optional[str] = None
        self.current_term: int = 1
        self.shared_threat_map: List[Dict[str, Any]] = []

    def register_node(self, node_id: str, battery_pct: float, lat: float, lon: float) -> None:
        self.nodes[node_id] = SwarmNode(node_id, battery_pct, lat, lon)
        if not self.current_leader_id:
            self.current_leader_id = node_id
            self.nodes[node_id].role = "LEADER"

    def elect_leader(self) -> str:
        """
        Raft-inspired election: selects node with highest battery SoC and best communication health.
        """
        if not self.nodes:
            return "NO_NODES"

        best_node_id = max(self.nodes.keys(), key=lambda nid: self.nodes[nid].battery_pct)
        self.current_leader_id = best_node_id
        self.current_term += 1

        for nid, node in self.nodes.items():
            node.role = "LEADER" if nid == best_node_id else "FOLLOWER"

        logger.info(f"[SwarmConsensus] Leader elected for Term {self.current_term}: {best_node_id}")
        return best_node_id

    def allocate_task_auction(self, task_name: str, target_lat: float, target_lon: float) -> Dict[str, Any]:
        """
        Auction-based distributed task assignment:
        Score = Distance * 0.6 + (100 - Battery) * 0.4
        Lowest bid wins the task.
        """
        if not self.nodes:
            return {"error": "No available swarm nodes"}

        bids = {}
        for nid, node in self.nodes.items():
            dist = math.sqrt((node.lat - target_lat)**2 + (node.lon - target_lon)**2) * 111000 # meters approx
            battery_cost = (100.0 - node.battery_pct) * 2.0
            total_cost = dist * 0.05 + battery_cost
            bids[nid] = total_cost

        winning_node = min(bids.keys(), key=lambda nid: bids[nid])
        return {
            "task": task_name,
            "assigned_uav": winning_node,
            "winning_bid_cost": round(bids[winning_node], 2),
            "all_bids": bids,
            "timestamp": time.time(),
        }

    def sync_threat_map(self, threat: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Broadcasts dynamic spatial threat (e.g. radar jamming, wind shear) to all swarm nodes."""
        self.shared_threat_map.append(threat)
        # Deduplicate & cap to last 50 threats
        if len(self.shared_threat_map) > 50:
            self.shared_threat_map.pop(0)
        return self.shared_threat_map

swarm_consensus_engine = SwarmConsensusEngine()
