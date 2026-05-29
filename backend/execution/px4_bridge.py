"""PX4 SITL/HITL bridge — telemetry ingest + command egress."""

import asyncio
import logging
from typing import Callable, Dict, Optional

from backend.execution.mavsdk_executor import MAVSDKExecutor, VehicleMode

logger = logging.getLogger("px4_bridge")


class ModeMigrationService:
    @staticmethod
    def migrate(mode: str, uav_id: str) -> str:
        original = mode.lower()
        migrated = original
        if original in ("simulation", "sim"):
            migrated = "sitl"
            logger.warning(f"[{uav_id}] [PX4] Legacy mode detected")
            logger.warning(f"[{uav_id}] [PX4] Migrated {original} -> {migrated}")
        return migrated

class PX4Bridge:
    """
    Unified PX4 integration:
    - SITL: udp://:14540
    - HITL: serial or UDP to hardware-in-loop
    - LIVE: Jetson companion → Pixhawk
    """

    SITL_URL = "udp://:14540"
    HITL_URL = "serial:///dev/ttyACM0:57600"

    def __init__(self, uav_id: str, mode: str = "sitl"):
        self.uav_id = uav_id
        
        logger.info(f"[{self.uav_id}] [PX4] Mode requested: {mode}")
        mode = ModeMigrationService.migrate(mode, uav_id)
        
        vm = {
            "sitl": VehicleMode.SITL,
            "hitl": VehicleMode.HITL,
            "live": VehicleMode.LIVE,
        }
        
        if mode not in vm:
            raise ValueError("Invalid PX4_MODE.\n\nSupported modes:\nsitl\nhitl\nlive\n")
            
        logger.info(f"[{self.uav_id}] [PX4] Starting {mode.upper()} execution bridge")
            
        url = self.SITL_URL if mode == "sitl" else self.HITL_URL
        self.executor = MAVSDKExecutor(uav_id, url, vm[mode])
        self._telemetry_cb: Optional[Callable] = None
        self._running = False

    async def start(self):
        await self.executor.connect()
        self._running = True

    def on_telemetry(self, callback: Callable):
        self._telemetry_cb = callback

    async def telemetry_loop(self, interval_s: float = 0.05):
        while self._running:
            tel = await self.executor.get_telemetry()
            if self._telemetry_cb:
                await self._telemetry_cb(tel) if asyncio.iscoroutinefunction(self._telemetry_cb) else self._telemetry_cb(tel)
            await asyncio.sleep(interval_s)

    async def execute_survival(self, strategy: str, landing: Optional[Dict] = None):
        params = {}
        if landing:
            params = {
                "lat": landing.get("lat", 0),
                "lon": landing.get("lon", 0),
                "altitude_m": landing.get("alt", 0),
            }
        return await self.executor.execute(strategy, params)

    async def execute_mission_route(self, waypoints: list[Dict]):
        """Executes a list of georeferenced waypoints via MAVSDK."""
        logger.info(f"[{self.uav_id}] MAVSDK executing {len(waypoints)} generated mission waypoints.")
        for wp in waypoints:
            await self.executor.execute("REROUTE", {
                "lat": wp.get("lat", 0),
                "lon": wp.get("lon", 0),
                "altitude_m": wp.get("altM", 100),
            })

    def stop(self):
        self._running = False
