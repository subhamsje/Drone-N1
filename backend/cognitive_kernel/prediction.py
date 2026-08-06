"""Multi-Horizon Trajectory Forecaster (+5s, +15s, +30s, +60s)."""

import time
import math
from typing import Dict, Any, List

class MultiHorizonPredictor:
    def predict_horizons(self, pose: Dict[str, Any], velocity_mps: float = 12.4) -> List[Dict[str, Any]]:
        """Calculates forward trajectories and GLSL uncertainty cone matrices."""
        horizons = [5, 15, 30, 60]
        predictions = []

        lat = pose.get("geo", {}).get("lat", 12.97)
        lon = pose.get("geo", {}).get("lon", 77.59)
        alt = pose.get("altitude_m", 120.5)

        for sec in horizons:
            dist = velocity_mps * sec
            uncertainty_radius_m = round(1.2 * math.sqrt(sec), 2)
            predicted_lat = lat + (dist / 111320.0) * 0.7
            predicted_lon = lon + (dist / 111320.0) * 0.7

            predictions.append({
                "horizon_sec": sec,
                "predicted_pose": {
                    "geo": {"lat": round(predicted_lat, 6), "lon": round(predicted_lon, 6)},
                    "altitude_m": round(alt, 1)
                },
                "uncertainty_radius_m": uncertainty_radius_m,
                "battery_remaining_pct": max(10, round(98.0 - (sec * 0.15), 1)),
                "glsl_shader_cone": {
                    "radius": uncertainty_radius_m,
                    "opacity": round(max(0.1, 0.8 - (sec / 80.0)), 2),
                    "color_hsl": "hsl(190, 90%, 50%)"
                }
            })

        return predictions
