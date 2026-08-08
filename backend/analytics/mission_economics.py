"""
Mission Economics & Fleet ROI Evaluation Engine.
Computes real-time unit economics per flight hour, per km, and validates commercial mission viability.
"""

from typing import Dict, Any

class MissionEconomicsEngine:
    ELECTRICITY_COST_PER_KWH = 0.16 # USD
    BATTERY_PACK_COST_USD = 850.0   # 6S 22000mAh LiPo
    RATED_LIPO_CYCLES = 300
    OPERATOR_HOURLY_RATE_USD = 45.0
    AIRFRAME_DEPRECIATION_PER_KM = 0.12 # USD

    @classmethod
    def evaluate_mission_cost(cls, distance_km: float, flight_duration_mins: float, avg_power_watts: float = 650.0) -> Dict[str, Any]:
        """
        Calculates exact unit economics and financial feasibility.
        """
        duration_hours = flight_duration_mins / 60.0
        
        # 1. Energy Cost
        energy_kwh = (avg_power_watts * duration_hours) / 1000.0
        energy_cost = energy_kwh * cls.ELECTRICITY_COST_PER_KWH

        # 2. Battery Cycle Degradation Cost
        cycle_cost = cls.BATTERY_PACK_COST_USD / cls.RATED_LIPO_CYCLES

        # 3. Airframe Depreciation & Wear
        airframe_cost = distance_km * cls.AIRFRAME_DEPRECIATION_PER_KM

        # 4. Operator Labor Cost
        labor_cost = duration_hours * cls.OPERATOR_HOURLY_RATE_USD

        # Total Mission Cost
        total_cost_usd = energy_cost + cycle_cost + airframe_cost + labor_cost
        cost_per_km = total_cost_usd / max(0.1, distance_km)

        # Commercial Viability Gatekeeper
        is_viable = total_cost_usd < 250.0 and cost_per_km < 15.0

        return {
            "distance_km": round(distance_km, 2),
            "flight_duration_mins": round(flight_duration_mins, 1),
            "breakdown": {
                "energy_cost_usd": round(energy_cost, 3),
                "battery_cycle_depreciation_usd": round(cycle_cost, 2),
                "airframe_wear_usd": round(airframe_cost, 2),
                "operator_labor_usd": round(labor_cost, 2),
            },
            "total_mission_cost_usd": round(total_cost_usd, 2),
            "cost_per_km_usd": round(cost_per_km, 2),
            "is_commercially_viable": is_viable,
            "advisory": "MISSION ECONOMICALLY VIABLE" if is_viable else "MISSION EXCEEDS COST CEILING (Adjust Corridor)",
        }

mission_economics = MissionEconomicsEngine()
