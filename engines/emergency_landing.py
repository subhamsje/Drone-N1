"""Terrain-aware emergency landing — least-risk survival zone selection."""

import logging
import numpy as np
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("emergency_landing")


@dataclass
class LandingZoneScore:
    zone_id: str
    position: Tuple[float, float]
    terrain_type: str
    collision_risk: float
    human_density: float
    terrain_stability: float
    payload_survivability: float
    comm_quality: float
    accessibility: float
    total_score: float
    rank: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "position": list(self.position),
            "terrain_type": self.terrain_type,
            "collision_risk": round(self.collision_risk, 4),
            "human_density": round(self.human_density, 4),
            "total_score": round(self.total_score, 4),
            "rank": self.rank,
        }


TERRAIN_RISK = {
    "HUMAN": (0.99, 0.95, 0.1, 0.3),
    "WATER": (0.85, 0.0, 0.05, 0.1),
    "TREES": (0.7, 0.1, 0.4, 0.5),
    "BUILDING": (0.6, 0.2, 0.5, 0.6),
    "ROOFTOP": (0.45, 0.15, 0.65, 0.75),
    "ROAD": (0.35, 0.4, 0.7, 0.8),
    "FIELD": (0.1, 0.05, 0.95, 0.95),
    "VEHICLE": (0.75, 0.5, 0.5, 0.4),
}


class EmergencyLandingIntelligence:
    """Selects LEAST-RISK SURVIVAL ZONE from perception + terrain data."""

    def rank_zones(
        self,
        sites: List[Dict[str, Any]],
        perception_hazards: Optional[List[str]] = None,
        gps_conf: float = 0.9,
        payload_sensitive: bool = False,
    ) -> List[LandingZoneScore]:
        scores: List[LandingZoneScore] = []
        hazards = set(perception_hazards or [])

        for i, site in enumerate(sites):
            t = site.get("terrain_type", "FIELD")
            coll, human, stab, payload = TERRAIN_RISK.get(t, (0.5, 0.3, 0.5, 0.5))
            if t.lower() in hazards or "human" in hazards:
                human = max(human, 0.9)
            if payload_sensitive:
                payload *= 1.2
            comm = gps_conf * 0.7 + 0.3
            access = stab * 0.8 + (1.0 - coll) * 0.2
            safety = site.get("safety_score", 0.5)

            total = (
                0.30 * (1.0 - coll)
                + 0.25 * (1.0 - human)
                + 0.20 * stab
                + 0.15 * payload
                + 0.05 * comm
                + 0.05 * access
            ) * safety

            scores.append(LandingZoneScore(
                zone_id=f"LZ-{i}",
                position=(site.get("x", site.get("coord", (0, 0))[0] if isinstance(site.get("coord"), tuple) else 0),
                          site.get("y", 0)),
                terrain_type=t,
                collision_risk=coll,
                human_density=human,
                terrain_stability=stab,
                payload_survivability=min(1.0, payload),
                comm_quality=comm,
                accessibility=access,
                total_score=float(np.clip(total, 0, 1)),
            ))

        scores.sort(key=lambda z: z.total_score, reverse=True)
        for r, z in enumerate(scores):
            z.rank = r + 1
        return scores

    def select_best(
        self,
        navigation: Dict[str, Any],
        perception: Optional[Dict] = None,
        gps_conf: float = 0.9,
    ) -> LandingZoneScore:
        sites = [{
            "terrain_type": navigation.get("terrain_type", "FIELD"),
            "safety_score": navigation.get("landing_safety", 0.8),
            "x": navigation.get("landing_x", 0),
            "y": navigation.get("landing_y", 0),
        }]
        # Expand grid candidates
        lx, ly = navigation.get("landing_x", 0), navigation.get("landing_y", 0)
        for dx, dy, tt in [(-10, -10, "FIELD"), (10, 10, "ROAD"), (-10, 10, "TREES")]:
            sites.append({"terrain_type": tt, "safety_score": 0.6, "x": lx + dx, "y": ly + dy})

        hazards = (perception or {}).get("hazards", [])
        ranked = self.rank_zones(sites, hazards, gps_conf)
        return ranked[0] if ranked else LandingZoneScore(
            "LZ-0", (0, 0), "FIELD", 0.1, 0.05, 0.9, 0.9, 0.9, 0.9, 0.85, 1
        )
