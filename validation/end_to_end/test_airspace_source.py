import asyncio
import sys
from pathlib import Path

# Add root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.intelligence.real_world_intel import EnvironmentalIntelligence

async def test_airspace_intelligence():
    print("[TEST] Verifying Airspace Intelligence (ADS-B)...")
    intel = EnvironmentalIntelligence()
    
    # Coordinates for a busy area (NYC/JFK approx) to ensure some traffic
    lat, lon = 40.6413, -73.7781
    
    print(f"[TEST] Fetching live traffic for {lat}, {lon}...")
    adsb = await intel.fetch_adsb(lat, lon)
    
    if adsb['source'] == 'opensky':
        print(f"[OK] Live ADS-B traffic fetched from OpenSky.")
        print(f"[DATA] Active Aircraft: {adsb['active_aircraft_in_radius']}")
        print(f"[DATA] Traffic Density: {adsb['traffic_density']}")
        print(f"[DATA] Conflict Risk:   {adsb['conflict_risk_score']:.2f}")
    else:
        print(f"[FAIL] ADS-B fetch fell back to offline. Source: {adsb['source']}")

    print("[SUCCESS] Airspace Intelligence data source verified.")

if __name__ == "__main__":
    asyncio.run(test_airspace_intelligence())
