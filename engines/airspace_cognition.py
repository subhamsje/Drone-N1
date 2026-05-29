"""Airspace cognition — corridors, deconfliction, congestion, UAM governance."""

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("airspace")


@dataclass
class AirspaceConflict:
    entity_id: str
    conflict_probability: float
    recommended_separation_m: float
    deconflict_action: str


@dataclass
class AirspaceState:
    corridor_id: str
    altitude_zone_m: float
    congestion_level: float
    conflict_risk: float
    reroute_required: bool
    cooperative_deconflict: List[AirspaceConflict]
    urban_corridor_active: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "corridor_id": self.corridor_id,
            "altitude_zone_m": self.altitude_zone_m,
            "congestion_level": round(self.congestion_level, 4),
            "conflict_risk": round(self.conflict_risk, 4),
            "reroute_required": self.reroute_required,
            "conflicts": len(self.cooperative_deconflict),
            "urban_corridor_active": self.urban_corridor_active,
        }


class AirspaceCognitionEngine:
    """Dynamic aerial traffic intelligence and cooperative deconfliction."""

    def __init__(self):
        self._peer_positions: Dict[str, Tuple[float, float, float]] = {}
        self._corridors: Dict[str, Dict] = {}
        self._no_fly_altitude_m = 0

    def register_peer(self, entity_id: str, position_ned: Tuple[float, float, float]):
        self._peer_positions[entity_id] = position_ned

    def define_corridor(self, corridor_id: str, bounds: Dict, altitude_m: float = 30.0):
        self._corridors[corridor_id] = {"bounds": bounds, "altitude_m": altitude_m}

    def evaluate(
        self,
        own_position: Tuple[float, float, float] = (0, 0, 10),
        own_velocity: Tuple[float, float, float] = (0, 0, 0),
        route_governance: Optional[Dict] = None,
        urban: bool = False,
    ) -> AirspaceState:
        conflicts: List[AirspaceConflict] = []
        min_sep = 999.0

        for eid, pos in self._peer_positions.items():
            dx = own_position[0] - pos[0]
            dy = own_position[1] - pos[1]
            dz = own_position[2] - pos[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            min_sep = min(min_sep, dist)
            if dist < 15.0:
                cp = max(0, 1.0 - dist / 15.0)
                conflicts.append(AirspaceConflict(
                    entity_id=eid,
                    conflict_probability=cp,
                    recommended_separation_m=20.0,
                    deconflict_action="altitude_shift" if dz < 5 else "lateral_offset",
                ))

        congestion = min(1.0, len(self._peer_positions) / 10.0)
        conflict_risk = max((c.conflict_probability for c in conflicts), default=0.0)
        corridor = list(self._corridors.keys())[0] if self._corridors else "open"
        alt_zone = 30.0 if urban else 15.0
        if route_governance:
            alt_zone = float(route_governance.get("recommended_altitude_m", alt_zone))

        reroute = conflict_risk > 0.6 or (route_governance or {}).get("reroute_required", False)

        return AirspaceState(
            corridor_id=corridor,
            altitude_zone_m=alt_zone,
            congestion_level=congestion,
            conflict_risk=conflict_risk,
            reroute_required=reroute,
            cooperative_deconflict=conflicts,
            urban_corridor_active=urban,
        )

    def generate_corridor(
        self,
        corridor_id: str,
        start: Tuple[float, float],
        end: Tuple[float, float],
        altitude_m: float = 30.0,
        width_m: float = 20.0,
    ) -> Dict[str, Any]:
        """Autonomous drone corridor for UAM governance."""
        self.define_corridor(corridor_id, {
            "start": start, "end": end, "width_m": width_m,
        }, altitude_m)
        return {"corridor_id": corridor_id, "altitude_m": altitude_m, "width_m": width_m, "status": "active"}

    def predict_congestion(self, horizon_s: float = 30.0) -> float:
        """Congestion evolution forecast."""
        base = min(1.0, len(self._peer_positions) / 10.0)
        return min(1.0, base * (1.0 + 0.02 * horizon_s))

    def regional_optimize(self, region_id: str, fleet_positions: Dict[str, Tuple]) -> Dict[str, Any]:
        """Regional airspace optimization — planetary federation shard."""
        for eid, pos in fleet_positions.items():
            self.register_peer(eid, pos)
        congestion = self.predict_congestion(60.0)
        return {
            "region_id": region_id,
            "peers_tracked": len(fleet_positions),
            "congestion_forecast_60s": round(congestion, 4),
            "recommended_altitude_shift_m": 5.0 if congestion > 0.6 else 0.0,
        }

    def predict_conflict(self, horizon_s: float = 30.0) -> Dict[str, Any]:
        """Aerial conflict prediction from peer trajectories."""
        conflicts = []
        for eid, pos in self._peer_positions.items():
            dist = (pos[0] ** 2 + pos[1] ** 2 + pos[2] ** 2) ** 0.5
            cp = max(0, 1.0 - dist / (15.0 + horizon_s * 0.1))
            if cp > 0.3:
                conflicts.append({"entity": eid, "probability": round(cp, 4), "horizon_s": horizon_s})
        return {
            "conflict_count": len(conflicts),
            "max_probability": max((c["probability"] for c in conflicts), default=0.0),
            "conflicts": conflicts[:5],
        }

    def traffic_intelligence(self, urban: bool = False) -> Dict[str, Any]:
        congestion = self.predict_congestion(60.0)
        conflict = self.predict_conflict(30.0)
        return {
            "traffic_density": round(congestion, 4),
            "conflict_forecast": conflict,
            "uam_mode": urban,
            "governance": "deconflict_active" if conflict["conflict_count"] > 0 else "nominal",
        }

    def federation_export(self) -> Dict[str, Any]:
        return {
            "corridors": list(self._corridors.keys()),
            "active_peers": len(self._peer_positions),
            "traffic": self.traffic_intelligence(),
            "planetary_airspace_ready": True,
        }
