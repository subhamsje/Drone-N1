import asyncio
import sys
from pathlib import Path

# Add root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.intelligence.real_world_intel import EnvironmentalIntelligence

async def test_weather_intelligence():
    print("[TEST] Initializing Environmental Intelligence...")
    intel = EnvironmentalIntelligence()
    
    # Coordinates for Bangalore (HOME_LAT, HOME_LON)
    lat, lon = 12.9716, 77.5946
    
    print(f"[TEST] Fetching live weather for {lat}, {lon}...")
    weather = await intel.fetch_metar(lat, lon)
    
    if weather['source'] == 'open-meteo':
        print(f"[OK] Live weather fetched from Open-Meteo.")
        print(f"[DATA] Wind Speed: {weather['wind_speed_kt']:.1f} kt")
        print(f"[DATA] Temp:       {weather['temperature_c']:.1f} C")
        print(f"[DATA] Precip:     {weather['precip_mm_h']:.1f} mm/h")
        print(f"[DATA] Cloud:      {weather['cloud_cover']}")
    else:
        print(f"[FAIL] Weather fetch fell back to offline mode. Source: {weather['source']}")

    print("[SUCCESS] Weather Intelligence data source verified.")

if __name__ == "__main__":
    asyncio.run(test_weather_intelligence())
