"""USV Surface Boat Protocol Adapter (Thruster Dynamics, NMEA Sonar)."""

import time
from typing import Dict, Any

class UsvProtocolAdapter:
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id

    def control_thrust_rudder(self, thrust_pct: float, rudder_angle_deg: float) -> Dict[str, Any]:
        """Dispatches marine thruster and rudder position commands."""
        return {
            "vehicle_id": self.vehicle_id,
            "domain_type": "USV_SURFACE_BOAT",
            "thruster_thrust_pct": thrust_pct,
            "rudder_angle_deg": rudder_angle_deg,
            "hydrographic_sonar": {
                "water_depth_m": 14.8,
                "water_temp_c": 18.2,
                "nmea_sentence": "$SDDBT,48.5,f,14.8,M,8.0,F*29"
            },
            "status": "MARINE_COMMAND_DISPATCHED",
            "timestamp": time.time()
        }
