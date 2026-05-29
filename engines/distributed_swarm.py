"""Distributed swarm cognition — collective perception, reasoning, survival."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("distributed_swarm")


@dataclass
class SharedPerceptionMemory:
    uav_id: str
    obstacles: List[str]
    threats: List[str]
    landing_zones: List[Dict]
    timestamp: float


@dataclass
class SwarmConsensusDecision:
    consensus_action: str
    confidence: float
    dissenting: List[str]
    collective_risk: float
    emergent_strategy: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "consensus_action": self.consensus_action,
            "confidence": round(self.confidence, 4),
            "dissenting": self.dissenting,
            "collective_risk": round(self.collective_risk, 4),
            "emergent_strategy": self.emergent_strategy,
        }


class DistributedSwarmCognition:
    """
    Beyond coordination — collaborative perceive, reason, route, survive, defend.
    """

    def __init__(self, fleet_id: str, member_ids: List[str]):
        self.fleet_id = fleet_id
        self.members = member_ids
        self._perception_memory: List[SharedPerceptionMemory] = []
        self._collective_map_version = 0
        self._member_snapshots: Dict[str, Dict] = {}

    def ingest_member(self, uav_id: str, snapshot: Dict[str, Any]):
        self._member_snapshots[uav_id] = snapshot
        mem = SharedPerceptionMemory(
            uav_id=uav_id,
            obstacles=(snapshot.get("perception", {}) or {}).get("hazards", []),
            threats=snapshot.get("cyber_fleet", {}).get("actions", []) if isinstance(snapshot.get("cyber_fleet"), dict) else [],
            landing_zones=[snapshot.get("landing_zone", {})] if snapshot.get("landing_zone") else [],
            timestamp=time.time(),
        )
        self._perception_memory.append(mem)
        if len(self._perception_memory) > 200:
            self._perception_memory = self._perception_memory[-100:]
        self._collective_map_version += 1

    def collective_reason(self) -> SwarmConsensusDecision:
        risks = [float(s.get("risk", {}).get("value", 0)) for s in self._member_snapshots.values()]
        actions = [s.get("decision", {}).get("action", "NONE") for s in self._member_snapshots.values()]
        strategies = [s.get("survival", {}).get("strategy", "HOLD") for s in self._member_snapshots.values()]

        collective_risk = max(risks) if risks else 0.0
        # Consensus: majority action or highest-priority survival
        priority = ["EMERGENCY_LAND", "RETURN_HOME", "THRUST_ADJUST", "HOLD", "NONE"]
        consensus_action = "NONE"
        for p in priority:
            if actions.count(p) >= len(actions) / 2 or strategies.count(p.replace("THRUST_ADJUST", "THRUST_REALLOC")) >= 1:
                consensus_action = p
                break

        if collective_risk > 0.7:
            consensus_action = "RETURN_HOME" if consensus_action == "NONE" else consensus_action

        dissenting = [uid for uid, s in self._member_snapshots.items()
                      if s.get("decision", {}).get("action") != consensus_action]

        emergent = "COLLECTIVE_RTL" if collective_risk > 0.75 else "COLLECTIVE_PATROL" if collective_risk < 0.3 else "COLLECTIVE_CAUTION"

        return SwarmConsensusDecision(
            consensus_action=consensus_action,
            confidence=1.0 - len(dissenting) / max(1, len(self.members)),
            dissenting=dissenting,
            collective_risk=collective_risk,
            emergent_strategy=emergent,
        )

    def get_shared_map(self) -> Dict[str, Any]:
        all_obstacles = []
        all_threats = []
        for m in self._perception_memory[-20:]:
            all_obstacles.extend(m.obstacles)
            all_threats.extend(m.threats if isinstance(m.threats, list) else [])
        return {
            "map_version": self._collective_map_version,
            "obstacles": list(set(all_obstacles)),
            "threats": list(set(str(t) for t in all_threats)),
            "members_active": len(self._member_snapshots),
        }

    def collective_simulate(self, world_forecast: Optional[Dict] = None) -> Dict[str, Any]:
        """Collaborative future-state prediction — decentralized, no central orchestrator."""
        forecasts = []
        for uid, snap in self._member_snapshots.items():
            wm = snap.get("world_model", world_forecast or {})
            forecasts.append(float(wm.get("mission_survivability_forecast", 0.75)))
        collective_surv = min(forecasts) if forecasts else 0.75
        return {
            "collective_survivability_forecast": round(collective_surv, 4),
            "members_simulated": len(forecasts),
            "degraded_member": collective_surv < 0.45,
        }

    def emergent_route_adaptation(self) -> Dict[str, Any]:
        """Self-organizing route consensus from member route states."""
        reroutes = sum(
            1 for s in self._member_snapshots.values()
            if (s.get("route_governance") or {}).get("reroute_required")
        )
        air_conflicts = sum(
            float((s.get("airspace") or {}).get("conflict_risk", 0))
            for s in self._member_snapshots.values()
        )
        action = "SWARM_REROUTE" if reroutes >= 2 or air_conflicts > 1.5 else "MAINTAIN_FORMATION"
        return {"emergent_route_action": action, "reroute_votes": reroutes, "conflict_pressure": round(air_conflicts, 4)}

    def distributed_consensus_graph(self) -> Dict[str, Any]:
        """Cognition graph edges between swarm members."""
        nodes = list(self._member_snapshots.keys())
        edges = []
        for i, a in enumerate(nodes):
            for b in nodes[i + 1:]:
                ra = float(self._member_snapshots[a].get("risk", {}).get("value", 0))
                rb = float(self._member_snapshots[b].get("risk", {}).get("value", 0))
                edges.append({"from": a, "to": b, "risk_coupling": round((ra + rb) / 2, 4)})
        return {"nodes": nodes, "edges": edges, "decentralized": True}

    def collective_defend(self) -> Dict[str, Any]:
        """Collaborative cyber/survival defense without central control."""
        threats = sum(
            len((s.get("cyber_warfare") or {}).get("attacks", []))
            for s in self._member_snapshots.values()
        )
        high_risk = [uid for uid, s in self._member_snapshots.items()
                     if float(s.get("risk", {}).get("value", 0)) > 0.65]
        action = "COLLECTIVE_CONTAIN" if threats >= 2 else "COLLECTIVE_CAUTION" if high_risk else "NOMINAL"
        return {"defense_action": action, "threat_count": threats, "high_risk_members": high_risk}

    def collaborative_world_simulation(self, foundation_forecast: Optional[Dict] = None) -> Dict[str, Any]:
        """Merge generative world forecasts across swarm."""
        gen_survs = []
        for snap in self._member_snapshots.values():
            fwm = snap.get("foundation_world_model", foundation_forecast or {})
            gen_survs.append(float(fwm.get("generative_survivability", 0.75)))
        collective_gen = min(gen_survs) if gen_survs else 0.75
        return {
            "collective_generative_survivability": round(collective_gen, 4),
            "members": len(gen_survs),
            "preempt_swarm_rtl": collective_gen < 0.35,
        }

    def optimize_collective_mission(self) -> Dict[str, Any]:
        """Emergent mission optimization from member flight ops."""
        phases = [s.get("flight_operations", {}).get("mission_phase", "cruise") for s in self._member_snapshots.values()]
        recovery_count = sum(1 for p in phases if p == "recovery")
        return {
            "recommended_swarm_phase": "recovery" if recovery_count >= 2 else "cruise",
            "recovery_members": recovery_count,
            "decentralized_optimization": True,
        }
