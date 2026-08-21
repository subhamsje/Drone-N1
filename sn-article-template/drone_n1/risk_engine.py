"""
Subsystem 1 & 4: Risk Intelligence Engine for Drone-N1 (Altaria OS)
Computes real-time 4-category operational risk scores (0.0 to 1.0) and aggregate threat metrics.
"""

import math
import time
from typing import Dict, Any

class RiskCategory:
    ENVIRONMENTAL = "environmental"
    HARDWARE = "hardware"
    CYBER_GNSS = "cyber_gnss"
    MISSION = "mission"

class RiskEngine:
    def __init__(self, wind_threshold: float = 12.0, min_battery: float = 0.20):
        self.wind_threshold = wind_threshold
        self.min_battery = min_battery
        self.weights = {
            RiskCategory.ENVIRONMENTAL: 0.25,
            RiskCategory.HARDWARE: 0.30,
            RiskCategory.CYBER_GNSS: 0.25,
            RiskCategory.MISSION: 0.20
        }

    def evaluate_environmental_risk(self, wind_speed: float, visibility_km: float) -> float:
        """Evaluates environmental threat based on wind gusts and visibility."""
        wind_risk = min(1.0, max(0.0, wind_speed / self.wind_threshold))
        vis_risk = min(1.0, max(0.0, (10.0 - visibility_km) / 10.0))
        return 0.7 * wind_risk + 0.3 * vis_risk

    def evaluate_hardware_risk(self, battery_soc: float, motor_vibration_g: float, temp_c: float) -> float:
        """Evaluates hardware integrity (battery, vibration, motor temp)."""
        bat_risk = 1.0 - min(1.0, max(0.0, battery_soc / 1.0))
        vib_risk = min(1.0, max(0.0, motor_vibration_g / 3.0))
        temp_risk = min(1.0, max(0.0, (temp_c - 40.0) / 40.0)) if temp_c > 40.0 else 0.0
        return 0.5 * bat_risk + 0.3 * vib_risk + 0.2 * temp_risk

    def evaluate_cyber_gnss_risk(self, sprt_residual: float, num_satellites: int, hdop: float) -> float:
        """Evaluates GNSS spoofing, satellite count, and dilution of precision."""
        sprt_risk = min(1.0, max(0.0, sprt_residual / 5.0))
        sat_risk = min(1.0, max(0.0, (12.0 - num_satellites) / 8.0))
        hdop_risk = min(1.0, max(0.0, (hdop - 1.0) / 4.0))
        return 0.5 * sprt_risk + 0.3 * sat_risk + 0.2 * hdop_risk

    def evaluate_mission_risk(self, distance_to_geofence_m: float, execution_delay_s: float) -> float:
        """Evaluates proximity to geofences and timeline slip."""
        geo_risk = max(0.0, 1.0 - (distance_to_geofence_m / 50.0)) if distance_to_geofence_m < 50.0 else 0.0
        delay_risk = min(1.0, max(0.0, execution_delay_s / 30.0))
        return 0.6 * geo_risk + 0.4 * delay_risk

    def compute_aggregate_risk(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Computes per-category and total weighted risk index."""
        r_env = self.evaluate_environmental_risk(
            telemetry.get("wind_speed", 0.0),
            telemetry.get("visibility_km", 10.0)
        )
        r_hw = self.evaluate_hardware_risk(
            telemetry.get("battery_soc", 1.0),
            telemetry.get("motor_vibration_g", 0.2),
            telemetry.get("temp_c", 35.0)
        )
        r_cyber = self.evaluate_cyber_gnss_risk(
            telemetry.get("sprt_residual", 0.1),
            telemetry.get("num_satellites", 14),
            telemetry.get("hdop", 0.9)
        )
        r_mission = self.evaluate_mission_risk(
            telemetry.get("distance_to_geofence_m", 100.0),
            telemetry.get("execution_delay_s", 0.0)
        )

        total_risk = (
            self.weights[RiskCategory.ENVIRONMENTAL] * r_env +
            self.weights[RiskCategory.HARDWARE] * r_hw +
            self.weights[RiskCategory.CYBER_GNSS] * r_cyber +
            self.weights[RiskCategory.MISSION] * r_mission
        )

        level = "GREEN"
        if total_risk > 0.70:
            level = "RED (CRITICAL - INITIATE SELF-HEAL)"
        elif total_risk > 0.45:
            level = "YELLOW (ELEVATED)"

        return {
            "total_risk": round(total_risk, 4),
            "threat_level": level,
            "categories": {
                RiskCategory.ENVIRONMENTAL: round(r_env, 4),
                RiskCategory.HARDWARE: round(r_hw, 4),
                RiskCategory.CYBER_GNSS: round(r_cyber, 4),
                RiskCategory.MISSION: round(r_mission, 4)
            },
            "timestamp": time.time()
        }
