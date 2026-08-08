import pytest
from backend.operations.self_healing_engine import SelfHealingEngine

def test_motor_harmonic_load_shedding():
    engine = SelfHealingEngine()
    # High harmonic vibration indicating bearing wear
    telemetry = {"vibration_ms2": 0.042, "battery_volts": 15.6, "wind_mps": 6.0}
    res = engine.evaluate_health_telemetry(telemetry)
    assert res["system_health_status"] == "PROACTIVE_LOAD_SHEDDING"
    assert res["proactive_actions_count"] >= 1
    assert any("PROPULSION_STATORS" in m["subsystem"] for m in res["mitigations"])

def test_nominal_health_telemetry():
    engine = SelfHealingEngine()
    telemetry = {"vibration_ms2": 0.012, "battery_volts": 15.8, "wind_mps": 5.0}
    res = engine.evaluate_health_telemetry(telemetry)
    assert res["system_health_status"] == "HEALTHY_OPTIMAL"
