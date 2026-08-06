import asyncio
import sys
from pathlib import Path

# Add root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engines.risk import IntegratedRiskEngine
from backend.api.operating_projection import project_survivability_snapshot
from config.settings import CONFIG

async def test_risk_quadrants():
    print("[TEST] Verifying Risk Quadrant data flow...")
    engine = IntegratedRiskEngine(CONFIG)
    
    # Simulate some failures
    # Mech failure (motor wear), Sensor noise, Comm delay
    r = engine.evaluate(
        r_mechanical=0.75, 
        r_sensor=0.12, 
        r_comms=0.45, 
        r_ai=0.05
    )
    
    print(f"[OK] Risk evaluated. Level: {r.level.name}. Value: {r.value}")
    
    # Project for frontend
    mock_snapshot = {"risk": {
        "r_mechanical": 0.75,
        "r_sensor": 0.12,
        "r_comms": 0.45,
        "r_ai": 0.05,
        "level": r.level.name,
        "dominant_src": r.dominant_source
    }}
    
    projection = project_survivability_snapshot(mock_snapshot)
    quads = projection.get("risk_quadrants")
    
    if quads and quads['mechanical'] == 0.75:
        print(f"[OK] Risk quadrants projected correctly.")
        print(f"[DATA] Mechanical: {quads['mechanical']}")
        print(f"[DATA] Sensor:     {quads['sensor']}")
        print(f"[DATA] Comms:      {quads['comms']}")
        print(f"[DATA] AI:         {quads['ai']}")
    else:
        print("[FAIL] Risk quadrant projection mismatch.")

    print("[SUCCESS] Risk Quadrant data source verified.")

if __name__ == "__main__":
    asyncio.run(test_risk_quadrants())
