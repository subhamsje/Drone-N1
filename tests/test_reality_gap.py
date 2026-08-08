import pytest
from backend.learning.reality_gap_calibration import RealityGapCalibrationEngine

def test_reality_gap_calibration_nominal():
    engine = RealityGapCalibrationEngine()
    actual = {"lat": 30.26720, "lon": -97.74310, "alt_m": 48.5, "airspeed_ms": 14.8}
    predicted = {"lat": 30.26721, "lon": -97.74311, "alt_m": 48.4, "airspeed_ms": 14.9}

    res = engine.evaluate_step(actual, predicted)
    assert res["status"] == "CALIBRATED_NOMINAL"
    assert res["spatial_drift_meters"] < 2.0
    assert "calibrated_cd" in res["parameters"]

def test_reality_gap_environment_mismatch():
    engine = RealityGapCalibrationEngine()
    # Large altitude discrepancy (e.g. updraft or severe unmodeled wind shear)
    actual = {"lat": 30.2672, "lon": -97.7431, "alt_m": 48.5, "airspeed_ms": 14.8}
    predicted = {"lat": 30.2672, "lon": -97.7431, "alt_m": 35.0, "airspeed_ms": 22.0}

    res = engine.evaluate_step(actual, predicted)
    assert res["spatial_drift_meters"] > 10.0
