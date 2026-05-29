"""Hyperscale telemetry intelligence — knowledge graph, survivability archives."""

import logging
import time
from collections import defaultdict
from typing import Any, Dict, List

logger = logging.getLogger("knowledge_graph")


class OperationalKnowledgeGraph:
    """Survivability intelligence archive — turbulence, spoofing, crashes, recoveries."""

    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self._nodes: Dict[str, Dict] = {}
        self._edges: List[Dict] = []
        self._turbulence_map: Dict[str, List[float]] = defaultdict(list)
        self._spoof_signatures: List[Dict] = []
        self._recovery_outcomes: List[Dict] = []

    def ingest(self, snapshot: Dict[str, Any], uav_id: str):
        ts = time.time()
        node_id = f"cycle-{snapshot.get('cycle', 0)}-{uav_id}"
        self._nodes[node_id] = {
            "type": "telemetry_cycle",
            "risk": float(snapshot.get("risk", {}).get("value", 0)),
            "surv": float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0)),
            "ts": ts,
        }

        cell = f"{int(snapshot.get('physics', {}).get('altitude', 0)) // 20}"
        turb = float(snapshot.get("twin_physics", {}).get("turbulence_index", 0))
        self._turbulence_map[cell].append(turb)
        if len(self._turbulence_map[cell]) > 100:
            self._turbulence_map[cell] = self._turbulence_map[cell][-50:]

        if snapshot.get("cybersecurity", {}).get("is_spoofed"):
            self._spoof_signatures.append({"ts": ts, "uav_id": uav_id, "trust": snapshot.get("sensor_trust")})
            self._edges.append({"from": node_id, "to": "spoof_event", "relation": "detected_spoof"})

        if snapshot.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"):
            outcome = {
                "ts": ts, "strategy": snapshot["survival"].get("strategy"),
                "success": float(snapshot["survival"].get("survival_score", 0)) > 0.5,
            }
            self._recovery_outcomes.append(outcome)
            self._edges.append({"from": node_id, "to": f"recovery-{outcome['strategy']}", "relation": "recovery"})

    def query_turbulence_hotspots(self) -> List[Dict]:
        return [
            {"cell": c, "mean": sum(v)/len(v), "samples": len(v)}
            for c, v in self._turbulence_map.items()
            if v and sum(v)/len(v) > 0.5
        ]

    def get_stats(self) -> Dict[str, Any]:
        recovery_success = sum(1 for r in self._recovery_outcomes if r.get("success")) / max(1, len(self._recovery_outcomes))
        return {
            "fleet_id": self.fleet_id,
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "spoof_events": len(self._spoof_signatures),
            "recovery_outcomes": len(self._recovery_outcomes),
            "recovery_success_rate": round(recovery_success, 4),
            "turbulence_cells": len(self._turbulence_map),
        }
