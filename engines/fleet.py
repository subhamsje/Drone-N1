"""
Altaria OS Swarm & Fleet Intelligence Engine.
──────────────────────────────────────────────────────────────────────────
Simulates collaborative fleet cognition, decentralized swarm health scores,
and mutual threat anomaly propagation across multiple airborne nodes.
"""

import numpy as np
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("fleet")


@dataclass
class SwarmMemberState:
    uav_id: str
    altitude: float
    battery: float
    health_score: float
    active_action: str
    risk_level: str


@dataclass
class FleetHealthStatus:
    fleet_health_score: float        # ∈ [0, 1]
    active_swarm_members: int
    swarm_threat_propagated: bool
    swarm_diagnostics: Dict[str, Any]
    member_states: List[SwarmMemberState]


class FleetCognitionLayer:
    """
    Simulates real-time peer-to-peer fleet health scoring and 
    distributed risk propagation over local swarm mesh networks.
    """

    def __init__(self, primary_uav_id: str = "Altaria-Alpha"):
        self.primary_uav_id = primary_uav_id
        # Fleet of companions flying in a swarm configuration
        self._members: Dict[str, SwarmMemberState] = {
            "UAV-101 (Beta)": SwarmMemberState("UAV-101", 5.0, 95.0, 0.98, "NONE", "LOW"),
            "UAV-102 (Gamma)": SwarmMemberState("UAV-102", 5.2, 92.0, 0.95, "NONE", "LOW"),
            "UAV-103 (Delta)": SwarmMemberState("UAV-103", 4.8, 97.0, 0.99, "NONE", "LOW"),
        }
        self.swarm_threat_propagated = False

    def evaluate_fleet(
        self,
        primary_battery: float,
        primary_risk: float,
        primary_action: str,
        cycle: int
    ) -> FleetHealthStatus:
        """
        Aggregates states across swarm nodes and updates peer companion
        degradation profiles over the course of the simulation.
        """
        # Dynamic simulation of companion drone behavior:
        # UAV-102 (Gamma) experiences motor thermal degradation at cycle 160
        if cycle >= 120:
            self._members["UAV-102 (Gamma)"].health_score = max(0.20, self._members["UAV-102 (Gamma)"].health_score - 0.008)
            self._members["UAV-102 (Gamma)"].battery = max(35.0, self._members["UAV-102 (Gamma)"].battery - 0.12)
            if self._members["UAV-102 (Gamma)"].health_score < 0.50:
                self._members["UAV-102 (Gamma)"].active_action = "THRUST_ADJUST"
                self._members["UAV-102 (Gamma)"].risk_level = "HIGH"
            if self._members["UAV-102 (Gamma)"].health_score < 0.35:
                self._members["UAV-102 (Gamma)"].active_action = "RETURN_HOME"
                self._members["UAV-102 (Gamma)"].risk_level = "CRITICAL"
                # Anomaly propagates to our primary drone!
                self.swarm_threat_propagated = True

        # UAV-103 drifts in battery normally
        self._members["UAV-103 (Delta)"].battery = max(10.0, self._members["UAV-103 (Delta)"].battery - 0.03)
        self._members["UAV-101 (Beta)"].battery = max(10.0, self._members["UAV-101 (Beta)"].battery - 0.03)

        # Compile list of states
        states = list(self._members.values())
        
        # Add primary state to fleet calculations
        p_lvl = "LOW"
        if primary_risk > 0.80:
            p_lvl = "CRITICAL"
        elif primary_risk > 0.55:
            p_lvl = "HIGH"
        elif primary_risk > 0.30:
            p_lvl = "MEDIUM"

        primary_state = SwarmMemberState(
            uav_id=self.primary_uav_id,
            altitude=5.0,
            battery=primary_battery,
            health_score=1.0 - primary_risk,
            active_action=primary_action,
            risk_level=p_lvl
        )
        all_states = states + [primary_state]

        # Calculate fleet health score
        avg_health = float(np.mean([m.health_score for m in all_states]))
        active_count = sum(1 for m in all_states if m.active_action != "RETURN_HOME")

        diagnostics = {
            "average_swarm_battery": float(np.mean([m.battery for m in all_states])),
            "degraded_peers_count": sum(1 for m in states if m.health_score < 0.70),
            "threat_vector": "SWARM_COLLABORATIVE_DANGER" if self.swarm_threat_propagated else "NOMINAL"
        }

        return FleetHealthStatus(
            fleet_health_score=avg_health,
            active_swarm_members=active_count,
            swarm_threat_propagated=self.swarm_threat_propagated,
            swarm_diagnostics=diagnostics,
            member_states=states  # Keep companion lists for dashboard rendering
        )
