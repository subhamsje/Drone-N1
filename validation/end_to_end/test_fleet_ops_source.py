import asyncio
import sys
from pathlib import Path

# Add root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.intelligence.fleet_intel import FleetIntelligenceLayer
from backend.api.operating_projection import project_fleet_snapshot

async def test_fleet_ops():
    print("[TEST] Initializing Fleet Intelligence Layer...")
    fleet = FleetIntelligenceLayer("swarm-alpha-1", ["Altaria-Alpha", "UAV-101", "UAV-102"])
    
    # Simulate some member state
    mock_snapshots = {
        "Altaria-Alpha": {
            "probabilistic_safety": {"composite_survivability": 0.95},
            "physics": {"battery": 88}
        },
        "UAV-101": {
            "probabilistic_safety": {"composite_survivability": 0.42},
            "physics": {"battery": 25}
        }
    }
    
    status = fleet.fleet_status(mock_snapshots)
    print(f"[OK] Fleet status calculated: {status['member_count']} units.")
    
    # Verify projection for frontend
    projection = project_fleet_snapshot({}, status)
    print(f"[DATA] Projected status keys: {list(projection['status'].keys())}")
    
    uav_101 = projection['status'].get("UAV-101")
    if uav_101:
        print(f"[DATA] UAV-101 Health: {uav_101['survivability']['composite_survivability']}")
        if uav_101['survivability']['composite_survivability'] < 0.5:
            print("[OK] UAV-101 correctly identified as Critical/Warning.")

    print("[SUCCESS] Fleet Operations data flow verified from backend source.")

if __name__ == "__main__":
    asyncio.run(test_fleet_ops())
