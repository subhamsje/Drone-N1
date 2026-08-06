"""4-Quadrant Probabilistic Risk Matrix (Mechanical, Weather, Traffic, Cyber)."""

import time
from typing import Dict, Any

class FourQuadrantRiskEngine:
    def __init__(self):
        self.weights = {"mechanical": 0.35, "weather": 0.25, "traffic": 0.25, "cyber": 0.15}

    def compute_risk(self, motor_wear: float = 0.05, wind_mps: float = 5.2, traffic_count: int = 12) -> Dict[str, Any]:
        """Calculates 4-quadrant risk scores and composite survivability index."""
        mech_risk = min(1.0, motor_wear * 2.0)
        weather_risk = min(1.0, wind_mps / 20.0)
        traffic_risk = min(1.0, traffic_count / 100.0)
        cyber_risk = 0.02

        composite = (
            self.weights["mechanical"] * mech_risk +
            self.weights["weather"] * weather_risk +
            self.weights["traffic"] * traffic_risk +
            self.weights["cyber"] * cyber_risk
        )

        survivability = max(0.0, 1.0 - composite)

        return {
            "timestamp": time.time(),
            "quadrants": {
                "mechanical": round(mech_risk, 3),
                "weather": round(weather_risk, 3),
                "traffic": round(traffic_risk, 3),
                "cyber": round(cyber_risk, 3)
            },
            "composite_risk_score": round(composite, 3),
            "composite_survivability": round(survivability, 3),
            "threat_level": "LOW" if composite < 0.25 else ("MEDIUM" if composite < 0.55 else "CRITICAL")
        }
