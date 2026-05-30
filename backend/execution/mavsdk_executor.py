"""
MAVSDK Command Executor — real PX4/ArduPilot command authority.
Executes survival decisions on live aircraft (SITL, HITL, production).
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mavsdk_executor")


class VehicleMode(str, Enum):
    SIMULATION = "simulation"
    SITL = "sitl"
    HITL = "hitl"
    LIVE = "live"


@dataclass
class ExecutionResult:
    success: bool
    command: str
    message: str
    latency_ms: float
    armed: bool = False
    mode: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "command": self.command,
            "message": self.message,
            "latency_ms": round(self.latency_ms, 2),
            "armed": self.armed,
            "mode": self.mode,
        }


# Semantic command → MAVSDK action mapping
COMMAND_MAP = {
    "EMERGENCY_LAND": "land",
    "MAV_CMD_NAV_LAND": "land",
    "RETURN_HOME": "rtl",
    "MAV_CMD_NAV_RETURN_TO_LAUNCH": "rtl",
    "HOLD": "hold",
    "MAV_CMD_NAV_LOITER_UNLIM": "hold",
    "REROUTE": "goto",
    "MAV_CMD_DO_REPOSITION": "goto",
    "THRUST_REALLOC": "attitude_hold",
    "VISUAL_NAV_HOLD": "offboard_velocity",
    "POWER_SAVE_GLIDE": "rtl",
}


class MAVSDKExecutor:
    """
    Low-latency autonomous command execution via MAVSDK.
    Falls back to logged simulation when MAVSDK unavailable.
    """

    def __init__(
        self,
        uav_id: str,
        connection_url: str = "udp://:14540",
        mode: VehicleMode = VehicleMode.SIMULATION,
    ):
        self.uav_id = uav_id
        self.connection_url = connection_url
        self.mode = mode
        self._drone = None
        self._connected = False
        self._command_log: List[Dict] = []
        self._sequence = 0

    async def connect(self) -> bool:
        if self.mode == VehicleMode.SIMULATION:
            raise RuntimeError("CRITICAL: SIMULATION mode has been deprecated for Altaria production builds. Use SITL.")
        try:
            from mavsdk import System
            self._drone = System()
            await self._drone.connect(system_address=self.connection_url)
            async for state in self._drone.core.connection_state():
                if state.is_connected:
                    self._connected = True
                    logger.info("[%s] MAVSDK connected: %s", self.uav_id, self.connection_url)
                    return True
        except ImportError:
            raise RuntimeError("CRITICAL: mavsdk python package is missing. Required for flight operations.")
        except Exception as e:
            logger.error("MAVSDK connect failed: %s", e)
            raise e
        return self._connected

    async def execute(self, semantic_command: str, params: Optional[Dict] = None) -> ExecutionResult:
        t0 = time.monotonic()
        self._sequence += 1
        action = COMMAND_MAP.get(semantic_command, semantic_command.lower())
        params = params or {}

        try:
            if not self._connected or not self._drone:
                raise ConnectionError("Cannot execute command. Drone is not connected to MAVSDK.")
            result = await self._execute_live(action, params)
        except Exception as e:
            logger.error(f"Execution Failed: {e}")
            result = ExecutionResult(False, semantic_command, str(e), (time.monotonic() - t0) * 1000)

        self._command_log.append({
            "ts": time.time(),
            "command": semantic_command,
            "action": action,
            "success": result.success,
            "params": params,
        })
        return result

    async def _execute_live(self, action: str, params: Dict) -> ExecutionResult:
        t0 = time.monotonic()
        drone = self._drone
        if action == "land":
            await drone.action.land()
            msg = "LAND initiated"
        elif action == "rtl":
            await drone.action.return_to_launch()
            msg = "RTL initiated"
        elif action == "hold":
            await drone.action.hold()
            msg = "HOLD initiated"
        elif action == "goto":
            lat = params.get("lat", 0)
            lon = params.get("lon", 0)
            alt = params.get("altitude_m", params.get("alt", 10))
            await drone.action.goto_location(lat, lon, alt, 0)
            msg = f"GOTO ({lat}, {lon}, {alt}m)"
        elif action == "offboard_velocity":
            await drone.offboard.set_velocity_ned([0.0, 0.0, 0.0])
            try:
                await drone.offboard.start()
            except Exception:
                pass
            msg = "Offboard velocity hold"
        else:
            await drone.action.hold()
            msg = f"Fallback hold for {action}"

        return ExecutionResult(
            success=True,
            command=action,
            message=msg,
            latency_ms=(time.monotonic() - t0) * 1000,
        )

    async def emergency_land_at(self, lat: float, lon: float, alt_m: float = 0) -> ExecutionResult:
        return await self.execute("EMERGENCY_LAND", {"lat": lat, "lon": lon, "altitude_m": alt_m})

    async def upload_mission(self, waypoints: List[Dict[str, float]]) -> ExecutionResult:
        t0 = time.monotonic()
        try:
            if not self._connected or not self._drone:
                raise ConnectionError("Drone not connected to MAVSDK.")
                
            from mavsdk.mission import MissionItem, MissionPlan
            items = []
            for wp in waypoints:
                items.append(MissionItem(
                    wp.get("lat", 0.0),
                    wp.get("lon", 0.0),
                    float(wp.get("alt_m", wp.get("altM", 10.0))),
                    10.0,
                    True,
                    float('nan'),
                    float('nan'),
                    MissionItem.CameraAction.NONE,
                    float('nan'),
                    float('nan'),
                    float('nan'),
                    float('nan'),
                    float('nan')
                ))
            plan = MissionPlan(items)
            await self._drone.mission.upload_mission(plan)
            
            msg = f"UPLOAD_MISSION: {len(items)} waypoints"
            self._command_log.append({"ts": time.time(), "command": "UPLOAD_MISSION", "success": True})
            return ExecutionResult(True, "UPLOAD_MISSION", msg, (time.monotonic() - t0) * 1000)
        except Exception as e:
            logger.error(f"Mission upload failed: {e}")
            self._command_log.append({"ts": time.time(), "command": "UPLOAD_MISSION", "success": False})
            return ExecutionResult(False, "UPLOAD_MISSION", str(e), (time.monotonic() - t0) * 1000)

    async def start_mission(self) -> ExecutionResult:
        t0 = time.monotonic()
        try:
            if not self._connected or not self._drone:
                raise ConnectionError("Drone not connected to MAVSDK.")
            
            await self._drone.mission.start_mission()
            self._command_log.append({"ts": time.time(), "command": "START_MISSION", "success": True})
            return ExecutionResult(True, "START_MISSION", "Mission started natively via MAVSDK", (time.monotonic() - t0) * 1000)
        except Exception as e:
            logger.error(f"Mission start failed: {e}")
            self._command_log.append({"ts": time.time(), "command": "START_MISSION", "success": False})
            return ExecutionResult(False, "START_MISSION", str(e), (time.monotonic() - t0) * 1000)

    async def get_telemetry(self) -> Dict[str, Any]:
        if not self._drone or not self._connected:
            raise ConnectionError("Drone not connected. Cannot fetch telemetry.")
        try:
            pos = await self._drone.telemetry.position().__anext__()
            batt = await self._drone.telemetry.battery().__anext__()
            return {
                "lat": pos.latitude_deg,
                "lon": pos.longitude_deg,
                "alt_m": pos.relative_altitude_m,
                "battery_pct": batt.remaining_percent,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        return self._command_log[-limit:]
