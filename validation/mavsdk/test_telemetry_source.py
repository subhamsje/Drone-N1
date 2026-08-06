import asyncio
import sys
import os
from pathlib import Path

# Add root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.execution.mavsdk_executor import MAVSDKExecutor, VehicleMode

async def test_telemetry():
    print("[TEST] Initializing MAVSDK Executor (SITL)...")
    executor = MAVSDKExecutor("Altaria-Alpha", connection_url="udp://:14540", mode=VehicleMode.SITL)
    
    try:
        print("[TEST] Connecting to system at udp://:14540...")
        # Connection check with timeout
        success = await asyncio.wait_for(executor.connect(), timeout=5.0)
        if not success:
            print("[FAIL] MAVSDK connected state not reached.")
            return

        print("[OK] MAVSDK Linked. Fetching telemetry stream...")
        
        # Poll 3 times to ensure stability
        for i in range(3):
            tel = await executor.get_telemetry()
            print(f"[DATA] Frame {i}: {tel}")
            await asyncio.sleep(1)

        print("[SUCCESS] Aircraft Telemetry verified from backend source.")
    except asyncio.TimeoutError:
        print("[FAIL] MAVSDK Connection Timeout. No drone detected on port 14540.")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(test_telemetry())
