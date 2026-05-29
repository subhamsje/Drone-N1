"""Planetary geospatial engine — weather, airspace, RF, infrastructure layers."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict

logger = logging.getLogger("geospatial")


@dataclass
class GeoLayer:
    layer_id: str
    kind: str  # weather | airspace | rf | infrastructure | terrain
    enabled: bool = True
    source: str = "stub"
    data: Dict[str, Any] = field(default_factory=dict)


class PlanetaryGeospatialEngine:
    """
    Feeds mission planning and world simulation.
    Production: OpenWeather/NOAA, FAA UTM/LATM, RF propagation models, OSM/Cesium Ion.
    """

    def __init__(self):
        self._layers: Dict[str, GeoLayer] = {
            "weather": GeoLayer("weather", "weather", source="stub"),
            "airspace": GeoLayer("airspace", "airspace", source="stub"),
            "rf": GeoLayer("rf", "rf", source="stub"),
            "infrastructure": GeoLayer("infrastructure", "infrastructure", source="stub"),
        }

    def set_weather_api_key(self, _key: str):
        self._layers["weather"].source = "openweather"
        logger.info("Weather provider configured (wire API in production)")

    def get_context(self, lat: float, lon: float, alt_m: float = 100.0) -> Dict[str, Any]:
        """Operational context at a point — used by planner and world model."""
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
        # Stub — replace with METAR/OpenWeather
        return {
            "wind_mps": 4.2,
            "gust_mps": 7.1,
            "visibility_km": 10.0,
            "precip_mm_h": 0.0,
            "turbulence_index": 0.15,
            "source": self._layers["weather"].source,
        }

    def _airspace_at(self, lat: float, lon: float, alt_m: float) -> Dict[str, Any]:
        return {
            "controlled": alt_m > 120,
            "restriction_level": "low" if alt_m < 60 else "medium",
            "notam_active": False,
            "source": self._layers["airspace"].source,
        }

    def _rf_at(self, lat: float, lon: float) -> Dict[str, Any]:
        return {
            "jamming_risk": 0.08,
            "gps_denied_probability": 0.05,
            "comm_degradation": 0.1,
        }

    def _infrastructure_near(self, lat: float, lon: float) -> Dict[str, Any]:
        return {
            "powerline_proximity_m": None,
            "urban_density": "low",
        }
