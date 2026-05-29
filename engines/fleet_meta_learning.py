"""Fleet-wide meta learning — collective survival policy evolution."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("fleet_meta_learning")


@dataclass
class SurvivalPolicyGene:
    policy_id: str
    strategy_weights: Dict[str, float]
    environment_tag: str
    success_rate: float
    deployments: int = 0


@dataclass
class EnvironmentalSignature:
    turbulence_p50: float
    spoof_rate: float
    rf_interference_p50: float
    optimal_routes: List[Dict[str, Any]] = field(default_factory=list)


class FleetMetaLearningEngine:
    """
    Collective fleet adaptation — shared survival policies, spoof signatures,
    turbulence maps, route optimizations.
    """

    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self._policies: Dict[str, SurvivalPolicyGene] = {}
        self._env_signature = EnvironmentalSignature(0.2, 0.0, 0.1)
        self._spoof_signatures: List[Dict] = []
        self._turbulence_cells: Dict[str, float] = {}
        self._generation = 0

    def ingest_fleet_cycle(self, uav_id: str, snapshot: Dict[str, Any]):
        turb = float(snapshot.get("twin_physics", {}).get("turbulence_index", 0))
        cell = f"{int(snapshot.get('physics', {}).get('altitude', 0))//10}"
        self._turbulence_cells[cell] = 0.9 * self._turbulence_cells.get(cell, 0) + 0.1 * turb

        if snapshot.get("cybersecurity", {}).get("is_spoofed"):
            self._spoof_signatures.append({
                "uav_id": uav_id, "ts": time.time(),
                "trust": snapshot.get("sensor_trust", {}),
            })
            if len(self._spoof_signatures) > 200:
                self._spoof_signatures = self._spoof_signatures[-100:]

        survival = snapshot.get("survival", {})
        strategy = survival.get("strategy", "HOLD")
        success = float(survival.get("survival_score", 0)) > 0.6
        self._update_policy(strategy, success, snapshot)

    def _update_policy(self, strategy: str, success: bool, snapshot: Dict):
        pid = f"policy-{self.fleet_id}-{strategy}"
        if pid not in self._policies:
            self._policies[pid] = SurvivalPolicyGene(
                pid, {strategy: 1.0}, self.fleet_id, 0.5
            )
        p = self._policies[pid]
        p.deployments += 1
        p.success_rate = 0.95 * p.success_rate + 0.05 * (1.0 if success else 0.0)

    def get_recommended_policy_weights(self) -> Dict[str, float]:
        if not self._policies:
            return {"EMERGENCY_LAND": 0.2, "RETURN_HOME": 0.3, "THRUST_REALLOC": 0.25, "HOLD": 0.25}
        weights = {}
        for p in self._policies.values():
            for s, w in p.strategy_weights.items():
                weights[s] = weights.get(s, 0) + w * p.success_rate
        total = sum(weights.values()) + 1e-9
        return {k: v / total for k, v in weights.items()}

    def get_fleet_intelligence_export(self) -> Dict[str, Any]:
        self._generation += 1
        return {
            "fleet_id": self.fleet_id,
            "generation": self._generation,
            "policy_count": len(self._policies),
            "spoof_signatures": len(self._spoof_signatures),
            "turbulence_hotspots": len([v for v in self._turbulence_cells.values() if v > 0.6]),
            "recommended_weights": self.get_recommended_policy_weights(),
            "top_policies": sorted(
                [{"id": p.policy_id, "success": p.success_rate} for p in self._policies.values()],
                key=lambda x: x["success"], reverse=True,
            )[:5],
        }
