import pytest
from backend.security.safety_invariants import safety_invariant_engine, SafetyInvariantViolation

def test_battery_critical_invariant():
    # Battery at 8% (<10%) must reject offboard cruise and permit only emergency touchdown
    critical_state = {"battery_pct": 8.0, "lat": 30.26, "lon": -97.74, "alt_m": 20.0, "roll_deg": 2.0}
    with pytest.raises(SafetyInvariantViolation) as exc:
        safety_invariant_engine.assert_invariants(critical_state, intended_command="CRUISE")
    assert "BATTERY_CRITICAL_RESERVE" in str(exc.value)

def test_geofence_breach_invariant():
    # Position inside restricted alpha zone must trigger immediate invariant violation
    breach_state = {"battery_pct": 90.0, "lat": 30.265, "lon": -97.745, "alt_m": 50.0, "roll_deg": 2.0}
    with pytest.raises(SafetyInvariantViolation) as exc:
        safety_invariant_engine.assert_invariants(breach_state, intended_command="FLY_WAYPOINT")
    assert "RESTRICTED_GEOFENCE_BREACH" in str(exc.value)

def test_nominal_invariants_pass():
    nominal_state = {"battery_pct": 92.0, "lat": 30.280, "lon": -97.710, "alt_m": 45.0, "roll_deg": 12.0}
    safety_invariant_engine.assert_invariants(nominal_state, intended_command="WAYPOINT_NAV")
