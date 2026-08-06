import asyncio
import sys
from pathlib import Path

# Add root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.intelligence.mission.semantic_planner import SemanticMissionPlanner

async def test_mission_corridors():
    print("[TEST] Initializing Semantic Mission Planner...")
    planner = SemanticMissionPlanner()
    
    intent = "Inspect the factory perimeter at 50m altitude."
    origin = {"lat": 12.97, "lon": 77.59, "alt_m": 0.0}
    
    plan = planner.plan_from_intent(intent, origin)
    print(f"[OK] Mission generated: {plan.plan_id}")
    print(f"[DATA] Intent: {plan.intent}")
    print(f"[DATA] Recovery Strategy: {plan.recovery_strategy}")
    print(f"[DATA] Max Risk: {plan.max_risk}")
    
    # Check waypoints for corridor generation
    if len(plan.waypoints) >= 2:
        print(f"[OK] {len(plan.waypoints)} waypoints generated for corridor rendering.")
        for i, wp in enumerate(plan.waypoints):
            print(f"  - WP{i}: {wp.lat}, {wp.lon} @ {wp.alt_m}m")
    else:
        print("[FAIL] Insufficient waypoints for a corridor.")

    print("[SUCCESS] Mission Corridor data source verified.")

if __name__ == "__main__":
    asyncio.run(test_mission_corridors())
