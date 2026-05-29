"""Planetary governance — regional zones, survivability intelligence, mission governance."""

import logging
from dataclasses import dataclass
from typing import Any, Dict

logger = logging.getLogger("planetary_governance")


@dataclass
class RegionalGovernance:
    zone_id: str
    survivability_index: float
    missions_governed: int
    edge_autonomous: bool
    sync_lag_s: float


class PlanetaryGovernanceEngine:
    """Regional mission governance atop planetary federation."""

    def __init__(self):
        self._zones: Dict[str, RegionalGovernance] = {}
        self._global_survivability = 0.75

    def update_zone(self, zone_id: str, planetary_intel: Dict[str, Any], disconnected: bool = False):
        regions = planetary_intel.get("regions", [])
        zone_surv = planetary_intel.get("global_mean_survivability", 0.75)
        for r in regions:
            if r.get("region") == zone_id or zone_id in str(r.get("region", "")):
                zone_surv = r.get("mean_survivability", zone_surv)
        self._zones[zone_id] = RegionalGovernance(
            zone_id=zone_id,
            survivability_index=zone_surv,
            missions_governed=self._zones.get(zone_id, RegionalGovernance(zone_id, 0.75, 0, False, 0)).missions_governed + 1,
            edge_autonomous=disconnected,
            sync_lag_s=0.0 if not disconnected else 120.0,
        )
        self._global_survivability = 0.9 * self._global_survivability + 0.1 * zone_surv

    def govern_mission(self, mission_id: str, home_zone: str) -> Dict[str, Any]:
        z = self._zones.get(home_zone)
        authority = "edge" if z and z.edge_autonomous else "regional"
        return {
            "mission_id": mission_id,
            "home_zone": home_zone,
            "authority": authority,
            "zone_survivability": z.survivability_index if z else self._global_survivability,
            "governance_active": True,
        }

    def get_planetary_status(self) -> Dict[str, Any]:
        return {
            "global_survivability_intelligence": round(self._global_survivability, 4),
            "zones": [
                {
                    "zone_id": z.zone_id,
                    "survivability_index": round(z.survivability_index, 4),
                    "missions_governed": z.missions_governed,
                    "edge_autonomous": z.edge_autonomous,
                }
                for z in self._zones.values()
            ],
        }
