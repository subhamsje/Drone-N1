"""
Altaria OS Navigation Suite — Terrain Landing Zone & Weather Routing.
──────────────────────────────────────────────────────────────────────────
Simulates semantic terrain scanning, safe emergency landing site selection,
and route weather hazard risk estimation.
"""

import numpy as np
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger("navigation")


@dataclass
class LandingSite:
    coord: Tuple[float, float]  # (x, y) relative offset
    safety_score: float         # ∈ [0, 1] (1 = highly safe)
    terrain_type: str
    risk_factors: List[str]


@dataclass
class NavigationRisk:
    weather_hazard_level: float # ∈ [0, 1]
    safe_landing_site: LandingSite
    airspace_congested: bool


class WeatherRoutingEngine:
    """
    Evaluates weather-hazard risks based on EKF reconstructed wind fields
    and turbulence vectors.
    """

    def __init__(self, wind_limit_knots: float = 18.0):
        self.wind_limit = wind_limit_knots
        self.base_turbulence_limit = 0.85

    def evaluate_corridor(self, estimated_wind: np.ndarray) -> float:
        """
        Returns weather hazard level ∈ [0, 1] based on wind speeds and turbulences.
        """
        wind_speed = float(np.linalg.norm(estimated_wind))
        # Convert wind speed metric units to knots approx: 1 m/s = 1.94 knots
        wind_knots = wind_speed * 1.94

        hazard = wind_knots / self.wind_limit
        # Add stochastic turbulence component
        gusts = float(np.random.uniform(0.0, 0.15))
        hazard += gusts

        return float(np.clip(hazard, 0.0, 1.0))


class TerrainLandingEngine:
    """
    Semantic terrain assessment engine. Evaluates a grid of surrounding
    potential landing landing-zones, filtering out humans, buildings,
    trees, and water in favor of open fields or flat empty zones.
    """

    def __init__(self):
        # 5x5 landing candidates surrounding the drone
        self.grid_size = 5
        self.terrain_classes = ["FIELD", "ROAD", "ROOFTOP", "TREES", "WATER", "HUMAN"]
        self.class_safety = {
            "FIELD": 0.95,
            "ROAD": 0.70,     # medium risk (cars)
            "ROOFTOP": 0.60,  # structural damage risk
            "TREES": 0.25,    # battery fire or recovery delay
            "WATER": 0.10,    # total electronic loss
            "HUMAN": 0.01,    # maximum human risk (DO NOT LAND)
        }

    def generate_terrain_mesh(self, drone_pos: Tuple[float, float]) -> List[LandingSite]:
        """Generates a semantic coordinate grid relative to current position."""
        px, py = drone_pos
        sites = []
        
        # Deterministic pseudo-random generation based on coordinate to keep
        # landing sites consistent as the drone drifts
        for dx in [-20.0, -10.0, 0.0, 10.0, 20.0]:
            for dy in [-20.0, -10.0, 0.0, 10.0, 20.0]:
                tx = px + dx
                ty = py + dy

                # Select terrain class based on coordinate hash
                hash_val = int(abs(tx * 31 + ty * 17)) % 100
                if hash_val < 35:
                    t_type = "FIELD"
                elif hash_val < 60:
                    t_type = "TREES"
                elif hash_val < 75:
                    t_type = "ROAD"
                elif hash_val < 88:
                    t_type = "ROOFTOP"
                elif hash_val < 95:
                    t_type = "WATER"
                else:
                    t_type = "HUMAN"

                base_safety = self.class_safety[t_type]
                # Inject micro-noise to safety scores representing slope/obstructions
                noise = float(np.random.normal(0, 0.03))
                safety = float(np.clip(base_safety + noise, 0.0, 1.0))

                risks = []
                if t_type == "HUMAN":
                    risks.append("COLLISION_WITH_CIVILIANS")
                if t_type == "WATER":
                    risks.append("ELECTRONICS_DROWNING")
                if t_type == "TREES":
                    risks.append("ENTANGLEMENT_HAZARD")
                if safety < 0.5:
                    risks.append("SLOPE_ANOMALY")

                sites.append(LandingSite(
                    coord=(tx, ty),
                    safety_score=safety,
                    terrain_type=t_type,
                    risk_factors=risks
                ))

        return sites

    def find_safest_site(self, drone_pos: Tuple[float, float]) -> LandingSite:
        """Finds and returns the safest ranked landing site coordinate."""
        mesh = self.generate_terrain_mesh(drone_pos)
        # Sort by safety score descending, and select best
        mesh.sort(key=lambda s: s.safety_score, reverse=True)
        return mesh[0]


class NavigationSuite:
    """
    Unified Navigation Suite. Interfaces weather corridor evaluation 
    and safest landing calculations.
    """

    def __init__(self):
        self.weather_engine = WeatherRoutingEngine()
        self.landing_engine = TerrainLandingEngine()

    def evaluate_navigation(
        self,
        drone_pos: Tuple[float, float],
        wind_vector: np.ndarray
    ) -> NavigationRisk:
        """Evaluates dynamic routing hazards and emergency landing sites."""
        hazard = self.weather_engine.evaluate_corridor(wind_vector)
        best_site = self.landing_engine.find_safest_site(drone_pos)
        
        # Swarm/airspace congestion indicator (derived from wind or static)
        congested = float(np.linalg.norm(wind_vector)) > 1.8

        return NavigationRisk(
            weather_hazard_level=hazard,
            safe_landing_site=best_site,
            airspace_congested=congested
        )
