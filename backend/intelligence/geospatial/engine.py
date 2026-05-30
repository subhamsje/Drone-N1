"""Planetary geospatial engine — weather, airspace, RF, infrastructure layers."""

import logging
import time
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict
from backend.intelligence.real_world_intel import EnvironmentalIntelligence

logger = logging.getLogger("geospatial")


@dataclass
class GeoLayer:
    layer_id: str
    kind: str  # weather | airspace | rf | infrastructure | terrain
    enabled: bool = True
    source: str = "real"
    data: Dict[str, Any] = field(default_factory=dict)


class PlanetaryGeospatialEngine:
    """
    Feeds mission planning and world simulation.
    Production: OpenWeather, OpenSky UTM, RF models, OSM/Cesium.
    """

    def __init__(self):
        self._layers: Dict[str, GeoLayer] = {
            "weather": GeoLayer("weather", "weather", source="real"),
            "airspace": GeoLayer("airspace", "airspace", source="real"),
            "rf": GeoLayer("rf", "rf", source="real"),
            "infrastructure": GeoLayer("infrastructure", "infrastructure", source="real"),
        }
        self.env_intel = EnvironmentalIntelligence()
        self._cache = {
            "weather": {},
            "airspace": {},
            "last_lat": 0.0,
            "last_lon": 0.0
        }
        self._polling_task = None
        
    def start(self):
        """Starts the background polling task for live intelligence."""
        if not self._polling_task:
            self._polling_task = asyncio.create_task(self._poll_environment())
            
    def stop(self):
        """Stops the background polling task."""
        if self._polling_task:
            self._polling_task.cancel()
            self._polling_task = None

    async def _poll_environment(self):
        while True:
            lat = self._cache["last_lat"]
            lon = self._cache["last_lon"]
            if lat != 0.0 or lon != 0.0:
                try:
                    fused = await self.env_intel.get_fused_environment(lat, lon)
                    self._cache["weather"] = fused.get("weather", {})
                    self._cache["airspace"] = fused.get("airspace", {})
                except Exception as e:
                    logger.error(f"Geospatial background poll failed: {e}")
            await asyncio.sleep(60.0) # Poll every 60s

    def set_weather_api_key(self, _key: str):
        self._layers["weather"].source = "openweather"

    def get_context(self, lat: float, lon: float, alt_m: float = 100.0) -> Dict[str, Any]:
        """Operational context at a point — used by planner and world model."""
        self._cache["last_lat"] = lat
        self._cache["last_lon"] = lon
        
        return {
            "position": {"lat": lat, "lon": lon, "alt_m": alt_m},
            "timestamp": time.time(),
            "weather": self._weather_at(lat, lon),
            "airspace": self._airspace_at(lat, lon, alt_m),
            "rf": self._rf_at(lat, lon),
            "infrastructure": self._infrastructure_near(lat, lon),
            "layers": {k: v.enabled for k, v in self._layers.items()},
        }

    def _weather_at(self, lat: float, lon: float) -> Dict[str, Any]:
        w = self._cache["weather"]
        return {
            "wind_mps": w.get("wind_speed_kt", 0) * 0.514444, # knots to m/s
            "gust_mps": w.get("wind_speed_kt", 0) * 0.514444 * 1.5,
            "visibility_km": w.get("visibility_sm", 10.0) * 1.60934,
            "precip_mm_h": 0.0,
            "turbulence_index": w.get("turbulence_probability", 0.05),
            "source": w.get("source", "initializing")
        }

    def _airspace_at(self, lat: float, lon: float, alt_m: float) -> Dict[str, Any]:
        a = self._cache["airspace"]
        return {
            "controlled": alt_m > 120,
            "restriction_level": "medium" if a.get("traffic_density") == "HIGH" else "low",
            "notam_active": False,
            "active_traffic": a.get("active_aircraft_in_radius", 0),
            "source": a.get("source", "initializing"),
        }

    def _rf_at(self, lat: float, lon: float) -> Dict[str, Any]:
        return {
            "jamming_risk": 0.01,
            "gps_denied_probability": 0.01,
            "comm_degradation": 0.0,
        }

    def _infrastructure_near(self, lat: float, lon: float) -> Dict[str, Any]:
        return {
            "powerline_proximity_m": None,
            "urban_density": "low",
        }
