import pytest
from backend.analytics.mission_economics import MissionEconomicsEngine

def test_short_inspection_mission_economics():
    res = MissionEconomicsEngine.evaluate_mission_cost(distance_km=4.5, flight_duration_mins=18.0)
    assert res["is_commercially_viable"] is True
    assert res["total_mission_cost_usd"] > 0
    assert "breakdown" in res
    assert "energy_cost_usd" in res["breakdown"]

def test_excessive_mission_rejection():
    # Long distance beyond single battery pack parameter
    res = MissionEconomicsEngine.evaluate_mission_cost(distance_km=140.0, flight_duration_mins=320.0)
    assert res["is_commercially_viable"] is False
    assert "EXCEEDS COST CEILING" in res["advisory"]
