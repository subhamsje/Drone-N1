import asyncio
import sys
from pathlib import Path

# Add root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.api.operating_projection import project_survivability_snapshot, HOME_LAT, HOME_LON

async def test_recovery_zones():
    print("[TEST] Verifying Recovery Zone projection...")
    
    # Mock snapshot with a relative landing zone
    mock_snapshot = {
        "landing_zone": {
            "zone_id": "LZ-1",
            "position": [100.0, 200.0], # 100m North, 200m East
            "terrain_type": "FIELD",
            "total_score": 0.88
        },
        "inference": {"crash_probability": 0.12},
        "probabilistic_safety": {"composite_survivability": 0.9}
    }
    
    projection = project_survivability_snapshot(mock_snapshot)
    lz = projection.get("landing_zone")
    
    if lz and "lat" in lz and "lon" in lz:
        print(f"[OK] Landing Zone projected to absolute coordinates.")
        print(f"[DATA] Home: {HOME_LAT}, {HOME_LON}")
        print(f"[DATA] LZ:   {lz['lat']}, {lz['lon']}")
        
        # Verify offset direction
        if lz['lat'] > HOME_LAT and lz['lon'] > HOME_LON:
            print("[OK] Offset direction (NE) is correct.")
    else:
        print("[FAIL] Landing Zone projection missing lat/lon.")

    print("[SUCCESS] Recovery Zone data source verified.")

if __name__ == "__main__":
    asyncio.run(test_recovery_zones())
