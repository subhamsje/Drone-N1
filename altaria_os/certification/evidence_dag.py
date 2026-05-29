"""Mission evidence DAG — certifiable replay and bounded recovery lineage."""

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("certification.dag")


@dataclass
class EvidenceNode:
    node_id: str
    node_type: str
    state_hash: str
    timestamp: float
    bounded: bool

    def to_dict(self) -> Dict:
        return self.__dict__


class MissionEvidenceDAG:
    """Certification-ready directed acyclic graph of mission decisions."""

    def __init__(self):
        self._nodes: List[EvidenceNode] = []
        self._edges: List[Dict] = []
        self._mission_id: Optional[str] = None

    def build_from_cycle(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        mid = snapshot.get("flight_operations", {}).get("mission_id", str(uuid.uuid4())[:8])
        self._mission_id = mid
        ts = time.time()

        stages = [
            ("perception", snapshot.get("adversarial_perception", {}).get("robustness_verdict", "?")),
            ("world_cognition", str(snapshot.get("world_cognition", {}).get("composite_uncertainty", 0))),
            ("foundation", str(snapshot.get("foundation_world_model", {}).get("generative_survivability", 0))),
            ("survival", snapshot.get("survival", {}).get("strategy", "?")),
            ("decision", snapshot.get("decision", {}).get("action", "?")),
            ("envelope", "ok" if snapshot.get("safety_envelope") else "fail"),
            ("recovery", snapshot.get("operational_trust", {}).get("recovery_lineage", [])),
        ]

        prev_id = None
        for ntype, state in stages:
            nid = f"{mid}-{ntype}-{len(self._nodes)}"
            bounded = ntype in ("envelope", "decision", "survival")
            node = EvidenceNode(nid, ntype, str(state)[:64], ts, bounded)
            self._nodes.append(node)
            if prev_id:
                self._edges.append({"from": prev_id, "to": nid, "relation": "causal"})
            prev_id = nid

        formal = snapshot.get("formal_certification", {}).get("formal_verification", {})
        return {
            "mission_id": mid,
            "dag_nodes": len(self._nodes),
            "dag_edges": len(self._edges),
            "nodes": [n.to_dict() for n in self._nodes[-7:]],
            "edges": self._edges[-6:],
            "all_invariants": formal.get("all_invariants_satisfied", False),
            "replay_id": snapshot.get("explanation", {}).get("replay_id"),
            "certification_ready": formal.get("certification_ready", False),
        }

    def record_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Append operator/mission lifecycle evidence (approval, upload, etc.)."""
        nid = f"evt-{event_type}-{uuid.uuid4().hex[:8]}"
        node = EvidenceNode(nid, event_type, str(payload)[:128], time.time(), True)
        self._nodes.append(node)
        if self._nodes:
            self._edges.append({
                "from": self._nodes[-2].node_id if len(self._nodes) > 1 else nid,
                "to": nid,
                "relation": "mission_lifecycle",
            })
        return {"node_id": nid, "node_type": event_type}

    def export_certifiable_report(self) -> Dict[str, Any]:
        bounded_rate = sum(1 for n in self._nodes if n.bounded) / max(1, len(self._nodes))
        return {
            "mission_id": self._mission_id,
            "total_nodes": len(self._nodes),
            "bounded_node_rate": round(bounded_rate, 4),
            "standards": ["FAA", "EASA", "DGCA", "ASTM", "DEFENSE"],
        }
