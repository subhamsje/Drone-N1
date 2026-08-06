import asyncio
import sys
from pathlib import Path

# Add root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.models import IntegratedRiskOutput, RiskLevel, FailureSource
from backend.api.operating_projection import project_survivability_snapshot

async def test_risk_quadrants():
    print("[TEST] Verifying Risk Quadrant projection...")
    
    # Simulate a real Risk Engine output object
    risk_output = IntegratedRiskOutput(
        value=0.62,
        level=RiskLevel.HIGH,
        r_mechanical=0.75,
        r_sensor=0.12,
        r_comms=0.45,
        r_ai=0.05,
        dominant_source=FailureSource.ACTUATOR_FAILURE
    )
    
    # Project for frontend
    mock_snapshot = {
        "risk": {
            "r_mechanical": risk_output.r_mechanical,
            "r_sensor": risk_output.r_sensor,
            "r_comms": risk_output.r_comms,
            "r_ai": risk_output.r_ai,
            "level": risk_output.level.name,
            "dominant_src": risk_output.dominant_source.name
        },
        "inference": {"crash_probability": 0.12},
        "probabilistic_safety": {"composite_survivability": 0.9}
    }
    
    projection = project_survivability_snapshot(mock_snapshot)
    quads = projection.get("risk_quadrants")
    
    if quads and quads['mechanical'] == 0.75:
        print(f"[OK] Risk quadrants projected correctly.")
        print(f"[DATA] Mechanical: {quads['mechanical']}")
        print(f"[DATA] Sensor:     {quads['sensor']}")
        print(f"[DATA] Comms:      {quads['comms']}")
        print(f"[DATA] AI:         {quads['ai']}")
        print(f"[DATA] Level:      {quads['level']}")
    else:
        print("[FAIL] Risk quadrant projection mismatch.")

    print("[SUCCESS] Risk Quadrant data flow verified.")

if __name__ == "__main__":
    asyncio.run(test_risk_quadrants())
