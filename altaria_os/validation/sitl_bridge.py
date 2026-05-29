"""PX4 SITL operational bridge — readiness hook for real-world hardening."""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger("sitl_bridge")


class PX4SITLBridge:
    """
    SITL connection readiness layer.
    Set ALTARIA_PX4_SITL=1 and PX4_CONNECTION udp://:14540 for live bridge.
    """

    def __init__(self, connection: Optional[str] = None):
        self.connection = connection or os.environ.get("PX4_CONNECTION", "udp://:14540")
        self.enabled = os.environ.get("ALTARIA_PX4_SITL", "0") == "1"
        self._connected = False

    async def connect(self) -> bool:
        if not self.enabled:
            logger.info("SITL bridge disabled (set ALTARIA_PX4_SITL=1)")
            return False
        try:
            # MAVSDK optional — graceful fallback
            from mavsdk import System  # type: ignore
            self._drone = System()
            await self._drone.connect(system_address=self.connection)
            self._connected = True
            return True
        except Exception as e:
            logger.warning("SITL connect failed (simulation mode): %s", e)
            return False

    def get_readiness(self) -> Dict[str, Any]:
        return {
            "sitl_enabled": self.enabled,
            "connection": self.connection,
            "connected": self._connected,
            "deployment_tier": "sitl" if self._connected else "simulation",
            "hardening_note": "Run PX4 SITL + export ALTARIA_PX4_SITL=1",
        }
