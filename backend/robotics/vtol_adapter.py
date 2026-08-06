"""VTOL Hybrid Fixed-Wing Transition & Aero-Control Adapter."""

import time
from typing import Dict, Any

class VtolProtocolAdapter:
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        self.flight_mode = "HOVER"  # HOVER | TRANSITION | FIXED_WING

    def transition_flight_mode(self, target_mode: str) -> Dict[str, Any]:
        """Manages aerodynamic transition between Quad-Hover and Fixed-Wing pusher flight."""
        self.flight_mode = target_mode
        return {
            "vehicle_id": self.vehicle_id,
            "domain_type": "VTOL_HYBRID",
            "command": "TRANSITION_FLIGHT_MODE",
            "previous_mode": "HOVER" if target_mode == "FIXED_WING" else "FIXED_WING",
            "active_mode": self.flight_mode,
            "pusher_throttle_pct": 85.0 if target_mode == "FIXED_WING" else 0.0,
            "airspeed_knots": 48.5 if target_mode == "FIXED_WING" else 12.0,
            "status": "TRANSITION_COMPLETED",
            "timestamp": time.time()
        }
