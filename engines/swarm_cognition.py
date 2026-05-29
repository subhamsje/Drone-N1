"""Swarm cognition — consensus, task allocation, distributed perception fusion."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("swarm_cognition")


@dataclass
class SwarmTask:
    task_id: str
    task_type: str
    assigned_uav: str
    priority: float
    status: str = "pending"


@dataclass
class SwarmConsensus:
    fleet_id: str
    consensus_risk: float
    shared_map_version: str
    active_tasks: List[SwarmTask]
    collision_vectors: List[Dict[str, float]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fleet_id": self.fleet_id,
            "consensus_risk": self.consensus_risk,
            "shared_map_version": self.shared_map_version,
            "tasks": [{"id": t.task_id, "uav": t.assigned_uav, "type": t.task_type} for t in self.active_tasks],
        }


class SwarmCognitionEngine:
    """Distributed task orchestration + collaborative routing."""

    def __init__(self, fleet_id: str, member_ids: List[str]):
        self.fleet_id = fleet_id
        self.members = member_ids
        self._member_states: Dict[str, Dict] = {}
        self._tasks: List[SwarmTask] = []
        self._map_version = "swarm-v1"

    def update_member(self, uav_id: str, snapshot: Dict[str, Any]):
        self._member_states[uav_id] = {
            "risk": float(snapshot.get("risk", {}).get("value", 0)),
            "battery": float(snapshot.get("physics", {}).get("battery", 100)),
            "position": snapshot.get("navigation_state", {}).get("position_ned", [0, 0, 0]),
            "ts": time.time(),
        }

    def compute_consensus(self) -> SwarmConsensus:
        risks = [s["risk"] for s in self._member_states.values()]
        consensus_risk = max(risks) if risks else 0.0
        return SwarmConsensus(
            fleet_id=self.fleet_id,
            consensus_risk=consensus_risk,
            shared_map_version=self._map_version,
            active_tasks=self._tasks,
        )

    def allocate_task(self, task_type: str, priority: float = 0.5) -> SwarmTask:
        # Assign to lowest-risk, highest-battery member
        best = None
        best_score = -1.0
        for uid in self.members:
            st = self._member_states.get(uid, {})
            score = (1.0 - st.get("risk", 1)) * 0.6 + st.get("battery", 0) / 100.0 * 0.4
            if score > best_score:
                best_score = score
                best = uid
        task = SwarmTask(
            task_id=f"task-{int(time.time())}",
            task_type=task_type,
            assigned_uav=best or self.members[0],
            priority=priority,
        )
        self._tasks.append(task)
        return task

    def collision_free_velocity(self, uav_id: str, desired_vel: List[float]) -> List[float]:
        """Repulsive adjustment from peer positions."""
        vx, vy, vz = desired_vel[0], desired_vel[1], desired_vel[2]
        my_pos = self._member_states.get(uav_id, {}).get("position", [0, 0, 0])
        for oid, st in self._member_states.items():
            if oid == uav_id:
                continue
            op = st.get("position", [0, 0, 0])
            dx = my_pos[0] - op[0]
            dy = my_pos[1] - op[1]
            dist = max(0.5, (dx*dx + dy*dy) ** 0.5)
            if dist < 5.0:
                vx += dx / dist * 0.5
                vy += dy / dist * 0.5
        return [vx, vy, vz]
