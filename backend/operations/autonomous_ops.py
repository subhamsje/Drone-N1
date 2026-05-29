"""Autonomous operations AI — fleet allocation, maintenance forecast, deployment optimization."""

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("autonomous_ops")


@dataclass
class MissionAllocation:
    mission_id: str
    assigned_uav: str
    priority: int
    estimated_survivability: float
    airspace_corridor: str

    def to_dict(self) -> Dict:
        return {k: round(v, 4) if isinstance(v, float) else v for k, v in self.__dict__.items()}


class AutonomousOperationsOrchestrator:
    """
    Fleet-level operational AI — mission allocation, rebalance, maintenance prediction.
    Complements FlightOperationsOrchestrator (per-UAV) and OperationalEconomicsEngine.
    """

    def __init__(self, fleet_id: str, fleet_size: int = 4):
        self.fleet_id = fleet_id
        self.fleet_size = fleet_size
        self._uav_health: Dict[str, float] = {}
        self._pending_missions: List[Dict] = []
        self._allocations: List[MissionAllocation] = []
        self._maintenance_scores: Dict[str, float] = {}

    def register_uav_cycle(self, uav_id: str, snapshot: Dict[str, Any]):
        surv = float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0.75))
        self._uav_health[uav_id] = 0.85 * self._uav_health.get(uav_id, 0.75) + 0.15 * surv
        crash_p = float(snapshot.get("inference", {}).get("crash_probability", 0))
        maint = 1.0 - crash_p * 0.5 - (1.0 - surv) * 0.3
        self._maintenance_scores[uav_id] = 0.9 * self._maintenance_scores.get(uav_id, 0.8) + 0.1 * maint

    def submit_mission(self, intent: str, priority: int = 5) -> str:
        mid = str(uuid.uuid4())[:8]
        self._pending_missions.append({"mission_id": mid, "intent": intent, "priority": priority, "ts": time.time()})
        return mid

    def allocate_fleet(self, airspace_state: Optional[Dict] = None) -> Dict[str, Any]:
        if not self._pending_missions:
            return {"allocations": [], "rebalance": False}

        sorted_uavs = sorted(self._uav_health.items(), key=lambda x: -x[1])
        allocations = []
        corridor = (airspace_state or {}).get("corridor_id", "open")

        for i, mission in enumerate(sorted(self._pending_missions, key=lambda m: -m["priority"])):
            if i >= len(sorted_uavs):
                break
            uav_id, health = sorted_uavs[i % len(sorted_uavs)]
            alloc = MissionAllocation(
                mission_id=mission["mission_id"],
                assigned_uav=uav_id,
                priority=mission["priority"],
                estimated_survivability=health,
                airspace_corridor=corridor,
            )
            allocations.append(alloc)
            self._allocations.append(alloc)

        self._pending_missions = self._pending_missions[len(allocations):]
        rebalance = len(sorted_uavs) > 1 and max(self._uav_health.values()) - min(self._uav_health.values()) > 0.25

        return {
            "fleet_id": self.fleet_id,
            "allocations": [a.to_dict() for a in allocations],
            "rebalance_recommended": rebalance,
            "maintenance_forecast": {
                uid: round(1.0 - score, 4) for uid, score in self._maintenance_scores.items()
            },
            "deployment_optimization": {
                "healthy_uavs": sum(1 for h in self._uav_health.values() if h > 0.6),
                "fleet_utilization": round(len(allocations) / max(1, self.fleet_size), 4),
            },
        }

    def rebalance_regions(self, regional_health: Dict[str, float]) -> Dict[str, Any]:
        """Cross-region fleet rebalance recommendations."""
        if not regional_health:
            return {"rebalance": False}
        vals = list(regional_health.values())
        spread = max(vals) - min(vals) if vals else 0
        return {
            "rebalance": spread > 0.2,
            "regional_spread": round(spread, 4),
            "target_shift": "low_to_high_health" if spread > 0.2 else "stable",
        }

    def optimize_energy_distribution(self, snapshots: Dict[str, Dict]) -> Dict[str, Any]:
        batteries = {
            uid: float(s.get("physics", {}).get("battery", 100))
            for uid, s in snapshots.items()
        }
        if not batteries:
            return {"distribution": "uniform"}
        low = [u for u, b in batteries.items() if b < 30]
        return {
            "low_battery_uavs": low,
            "mean_battery": round(sum(batteries.values()) / len(batteries), 2),
            "recommend_rtl": low,
        }

    def airspace_throughput(self, airspace: Dict[str, Any]) -> Dict[str, Any]:
        congestion = float(airspace.get("congestion_level", 0))
        return {
            "throughput_factor": round(1.0 - congestion * 0.5, 4),
            "corridor": airspace.get("corridor_id", "open"),
            "optimize_altitude": congestion > 0.6,
        }

    def compute_operational_economics(self, enterprise_roi: Optional[Dict] = None) -> Dict[str, Any]:
        roi = enterprise_roi or {}
        crashes_prevented = roi.get("crashes_prevented", 0)
        return {
            "cost_avoidance_usd": roi.get("total_cost_avoidance_usd", 0),
            "crashes_prevented": crashes_prevented,
            "mission_continuity_score": round(
                sum(self._uav_health.values()) / max(1, len(self._uav_health)), 4
            ),
            "mission_throughput": len(self._allocations),
            "fleet_health_mean": round(
                sum(self._uav_health.values()) / max(1, len(self._uav_health)), 4
            ),
            "maintenance_savings_pct": roi.get("maintenance_optimization_pct", 0),
            "pilot_reduction_estimate_pct": roi.get("human_intervention_reduction_pct", 0),
            "survivability_economics_index": round(
                (crashes_prevented * 0.3 + (roi.get("fleet_uptime_pct", 0) or 0) * 0.01) * 10, 4
            ),
        }
