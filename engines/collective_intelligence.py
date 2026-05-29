"""True decentralized collective intelligence — emergent cognition without central control."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("collective_intelligence")


@dataclass
class EmergentCognitionState:
    emergent_action: str
    collective_confidence: float
    decentralized_reasoning: List[str]
    strategic_adaptation: str
    memory_version: int

    def to_dict(self) -> Dict:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in self.__dict__.items()}


class DecentralizedCollectiveIntelligence:
    """
    Emergent layer over DistributedSwarmCognition — collaborative reason/simulate/defend/evolve.
    """

    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self._collective_memory: List[Dict] = []
        self._memory_version = 0
        self._strategic_doctrine = "PATROL"

    def ingest_collective_snapshot(self, collective_swarm: Dict[str, Any], foundation: Dict[str, Any]):
        self._collective_memory.append({
            "ts": time.time(),
            "consensus": collective_swarm.get("consensus", {}),
            "gen_surv": foundation.get("generative_survivability", 0.75),
            "defend": collective_swarm.get("collective_defend", {}),
        })
        if len(self._collective_memory) > 100:
            self._collective_memory = self._collective_memory[-50:]
        self._memory_version += 1

    def emergent_reason(self, collective_swarm: Dict[str, Any]) -> EmergentCognitionState:
        consensus = collective_swarm.get("consensus", {})
        coll_sim = collective_swarm.get("collaborative_world_sim", {})
        defend = collective_swarm.get("collective_defend", {})
        routing = collective_swarm.get("emergent_routing", {})
        mission = collective_swarm.get("mission_optimize", {})

        reasoning = []
        action = consensus.get("consensus_action", "NONE")
        risk = float(consensus.get("collective_risk", 0))

        if defend.get("defense_action") == "COLLECTIVE_CONTAIN":
            action = "COLLECTIVE_DEFEND"
            reasoning.append("distributed_cyber_consensus")
            self._strategic_doctrine = "CONTESTED"

        if coll_sim.get("preempt_swarm_rtl"):
            action = "SWARM_RTL"
            reasoning.append("collaborative_world_simulation_rtl")

        if routing.get("emergent_route_action") == "SWARM_REROUTE":
            reasoning.append("emergent_route_adaptation")
            if action == "NONE":
                action = "SWARM_REROUTE"

        if mission.get("recommended_swarm_phase") == "recovery":
            self._strategic_doctrine = "RECOVERY"
            reasoning.append("decentralized_mission_recovery")

        conf = float(consensus.get("confidence", 0.8))
        if risk > 0.7:
            conf *= 0.7

        return EmergentCognitionState(
            emergent_action=action,
            collective_confidence=conf,
            decentralized_reasoning=reasoning or ["nominal_collective_patrol"],
            strategic_adaptation=self._strategic_doctrine,
            memory_version=self._memory_version,
        )

    def distributed_strategic_adaptation(self, meta_cognition: Dict[str, Any]) -> Dict[str, Any]:
        mutations = meta_cognition.get("policy_mutations_applied", [])
        if "increase_survival_bias" in mutations:
            self._strategic_doctrine = "SURVIVAL_FIRST"
        return {
            "doctrine": self._strategic_doctrine,
            "fleet_id": self.fleet_id,
            "decentralized": True,
            "memory_entries": len(self._collective_memory),
        }
