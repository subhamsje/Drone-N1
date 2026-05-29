"""
Flight stack adapter — Altaria's only interface to aircraft.

Delegates to MAVSDK (PX4/ArduPilot) and MAVLink gateway. Does not implement autopilot logic.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.execution.mavsdk_executor import MAVSDKExecutor, VehicleMode
from backend.execution.px4_bridge import PX4Bridge
from backend.mavlink.gateway import MAVLinkGateway
from backend.config import BACKEND_CONFIG

logger = logging.getLogger("flight_stack")


class FlightStackType(str, Enum):
    PX4 = "px4"
    ARDUPILOT = "ardupilot"
    AUTO = "auto"


class FlightStackAdapter:
    """
    Unified connection + mission upload + emergency commands.
    ArduPilot and PX4 both speak MAVLink; MAVSDK is the primary command path.
    """

    def __init__(self, uav_id: str, px4_bridge: PX4Bridge):
        self.uav_id = uav_id
        self._bridge = px4_bridge
        self._executor: MAVSDKExecutor = px4_bridge.executor
        self._mavlink = MAVLinkGateway(uav_id, BACKEND_CONFIG.mavlink.connection)
        self._stack_type = FlightStackType.PX4
        self._connection_uri = "udp://:14540"
        self._telemetry_task = None

    @property
    def connected(self) -> bool:
        return self._executor._connected

    @property
    def mode(self) -> str:
        return self._executor.mode.value

    def status(self) -> Dict[str, Any]:
        return {
            "uav_id": self.uav_id,
            "connected": self.connected,
            "mode": self.mode,
            "stack": self._stack_type.value,
            "connection_uri": self._connection_uri,
            "mavlink_packets": self._mavlink._packet_count,
            "audit_tail": self._executor.get_audit_log(5),
        }

    async def connect(
        self,
        connection_type: str = "udp",
        uri: Optional[str] = None,
        stack: str = "px4",
        vehicle_mode: str = "sitl",
    ) -> Dict[str, Any]:
        """CONNECT — bind to SITL/HITL/live without replacing autopilot."""
        self._stack_type = FlightStackType(stack.lower()) if stack.lower() in ("px4", "ardupilot") else FlightStackType.PX4

        if uri:
            self._connection_uri = uri if "://" in uri else f"{connection_type}://{uri}"
        elif connection_type == "serial":
            self._connection_uri = "serial:///dev/ttyACM0:57600"
        else:
            self._connection_uri = "udp://:14540"

        mode_map = {
            "simulation": VehicleMode.SIMULATION,
            "sitl": VehicleMode.SITL,
            "hitl": VehicleMode.HITL,
            "live": VehicleMode.LIVE,
        }
        self._executor.connection_url = self._connection_uri
        self._executor.mode = mode_map.get(vehicle_mode, VehicleMode.SITL)

        ok = await self._executor.connect()
        if ok and not self._bridge._running:
            await self._bridge.start()
            self._bridge._running = True

        logger.info(
            "[%s] flight stack connect stack=%s uri=%s ok=%s",
            self.uav_id, self._stack_type.value, self._connection_uri, ok,
        )
        return {**self.status(), "success": ok}

    async def disconnect(self) -> Dict[str, Any]:
        self._bridge.stop()
        self._executor._connected = False
        self._executor._drone = None
        return self.status()

    async def upload_mission(self, waypoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upload georeferenced route to autopilot via MAVSDK (goto sequence v1)."""
        if not waypoints:
            return {"success": False, "message": "no waypoints"}
        await self._bridge.execute_mission_route(waypoints)
        return {
            "success": True,
            "waypoints_uploaded": len(waypoints),
            "stack": self._stack_type.value,
            "note": "MAVSDK goto sequence; use Mission Planner for full .plan in field ops",
        }

    async def execute_command(self, command: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        verdict = await self._mavlink.submit_command(command, params or {}, source="operator")
        if not verdict.allowed:
            return {"success": False, "message": verdict.reason, "threat_score": verdict.threat_score}
        result = await self._executor.execute(command, params)
        return result.to_dict()

    async def get_live_telemetry(self) -> Dict[str, Any]:
        return await self._executor.get_telemetry()
