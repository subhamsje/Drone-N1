import pytest
import time
from backend.operations.temporal_replay import TemporalReplayEngine

def test_temporal_replay_record_and_seek():
    engine = TemporalReplayEngine()
    engine.record_frame(altitude_m=10.0, airspeed_ms=5.0, pitch_deg=0.0, roll_deg=0.0, battery_pct=98.0)
    time.sleep(0.01)
    target_time = time.time()
    engine.record_frame(altitude_m=20.0, airspeed_ms=10.0, pitch_deg=2.0, roll_deg=1.0, battery_pct=97.0)
    engine.record_frame(altitude_m=30.0, airspeed_ms=15.0, pitch_deg=4.0, roll_deg=2.0, battery_pct=96.0)

    # Seek closest to target_time
    found = engine.seek(target_time)
    assert found is not None
    assert found["altitude_m"] == 20.0

def test_temporal_step_navigation():
    engine = TemporalReplayEngine()
    engine.record_frame(10.0, 5.0, 0.0, 0.0, 99.0)
    engine.record_frame(20.0, 8.0, 1.0, 0.0, 98.0)
    
    engine.seek(0)
    step1 = engine.step_forward()
    assert step1 is not None
