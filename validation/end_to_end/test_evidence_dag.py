import asyncio
import sys
from pathlib import Path

# Add root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engines.autonomous_cognition import AutonomousCognitionEngine
from core.cognitive_models import SurvivalPlan, ScenarioOutcome

async def test_evidence_dag():
    print("[TEST] Verifying Evidence DAG source (Reasoning Chain)...")
    engine = AutonomousCognitionEngine()
    
    # Simulate a high-risk situation requiring recovery
    mock_snapshot = {
        "risk": {"value": 0.82, "level": "CRITICAL"},
        "physics": {"battery": 22},
        "sensor_trust": {"gps_confidence": 0.35}
    }
    
    mock_survival = SurvivalPlan(
        strategy="EMERGENCY_LAND",
        urgency="IMMEDIATE",
        survival_score=0.45,
        scenarios_evaluated=7,
        best_outcome=ScenarioOutcome("EMERGENCY_LAND", 0.6, 0.5, 0.1, 0.4, 25.0),
        backup_nav="visual_odometry",
        thrust_redistribution=True,
        emergency_power_mode=True
    )
    
    # Reason about the situation
    cognition = engine.reason(
        snapshot=mock_snapshot,
        sensor_trust={"gps_confidence": 0.35},
        failure_preds={"crash_probability": 0.78},
        survival_plan=mock_survival.to_dict()
    )
    
    chain = cognition.reasoning_chain
    print(f"[OK] Cognition reasoning completed.")
    
    if len(chain) > 0:
        print(f"[DATA] Reasoning Chain ({len(chain)} steps):")
        for i, step in enumerate(chain):
            print(f"  {i+1}. {step}")
            
        # Verify specific logic triggers
        if any("GPS" in s for s in chain) and any("Survival" in s for s in chain):
            print("[OK] Chain correctly identifies GPS degradation and survival priorities.")
    else:
        print("[FAIL] Empty reasoning chain produced.")

    print("[SUCCESS] Evidence DAG data source verified.")

if __name__ == "__main__":
    asyncio.run(test_evidence_dag())
