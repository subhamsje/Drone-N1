"""
Real-World Intelligence Adapters
Fetches live environmental data (Weather, Airspace) using actual HTTP REST queries.
"""

import logging
import asyncio
import httpx
from typing import Dict, Any

logger = logging.getLogger("real_world_intel")

class EnvironmentalIntelligence:
    def __init__(self):
        self._cache = {}

    async def fetch_metar(self, lat: float, lon: float) -> Dict[str, Any]:
        """Real query to open-meteo for live surface conditions."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,wind_direction_10m,precipitation&timezone=auto",
                    timeout=2.0
                )
                resp.raise_for_status()
                data = resp.json()
                current = data.get("current", {})
                
                return {
                    "source": "open-meteo",
                    "wind_speed_kt": current.get("wind_speed_10m", 0.0) * 0.539957, # km/h to knots
                    "wind_direction_deg": current.get("wind_direction_10m", 0),
                    "visibility_sm": 10.0, # open-meteo doesn't always provide visibility
                    "cloud_cover": "OVC",
                    "temperature_c": current.get("temperature_2m", 0.0),
                    "turbulence_probability": 0.05 if current.get("wind_speed_10m", 0.0) < 15 else 0.3
                }
        except Exception as e:
            logger.error(f"Failed to fetch real weather: {e}")
            return {
                "source": "offline",
                "wind_speed_kt": 0.0,
                "wind_direction_deg": 0,
                "visibility_sm": 0.0,
                "cloud_cover": "CLR",
                "temperature_c": 0.0,
                "turbulence_probability": 0.0
            }
        
    async def fetch_adsb(self, lat: float, lon: float, radius_nm: float = 10.0) -> Dict[str, Any]:
        """Real query to OpenSky Network for live traffic."""
        try:
            lamin = lat - 0.5
            lomin = lon - 0.5
            lamax = lat + 0.5
            lomax = lon + 0.5
            async with httpx.AsyncClient() as client:
                # Note: Unauthenticated opensky limits strictly.
                resp = await client.get(
                    f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}",
                    timeout=2.0
                )
                resp.raise_for_status()
                data = resp.json()
                states = data.get("states") or []
                
                return {
                    "source": "opensky",
                    "traffic_density": "HIGH" if len(states) > 5 else "LOW",
                    "active_aircraft_in_radius": len(states),
                    "conflict_risk_score": min(1.0, len(states) * 0.05)
                }
        except Exception as e:
            logger.warning(f"Failed to fetch live ADS-B (possibly rate limited): {e}")
            return {
                "source": "offline",
                "traffic_density": "UNKNOWN",
                "active_aircraft_in_radius": 0,
                "conflict_risk_score": 0.0
            }
        
    async def get_fused_environment(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fuses real-world API data into the Altaria world model context."""
        metar, adsb = await asyncio.gather(
            self.fetch_metar(lat, lon),
            self.fetch_adsb(lat, lon)
        )
        return {
            "weather": metar,
            "airspace": adsb
        }
