"""
Deterministic Safety Invariants Engine (Non-Negotiable System Hard Constraints).
Evaluated synchronously before any command execution and continuously during 50Hz telemetry cycles.
"""

from typing import Dict, Any, List, Optional
import math
import logging

logger = logging.getLogger("altaria.safety_invariants")

class SafetyInvariantViolation(Exception):
    """Raised when a hard system invariant is breached."""
    def __init__(self, invariant_name: str, message: str, severity: str = "CRITICAL"):
        self.invariant_name = invariant_name
        self.message = message
        self.severity = severity
        super().__init__(f"[{severity}] Safety Invariant Violated ({invariant_name}): {message}")

class SafetyInvariantEngine:
    """Deterministic constraint validator enforcing hard safety envelopes."""
    
    CRITICAL_BATTERY_PCT = 10.0
    MAX_CENTRIFUGAL_ROLL_DEG = 35.0
    MAX_ALLOWABLE_WIND_MPS = 22.0
    MIN_GPS_SATS_FOR_OFFBOARD = 8
    
    # Example restricted geofence polygon (Latitude, Longitude)
    RESTRICTED_AIRSPACES = [
        {"name": "ALPHA_CRITICAL_INFRASTRUCTURE", "lat_min": 30.260, "lat_max": 30.270, "lon_min": -97.750, "lon_max": -97.740, "floor_m": 0, "ceiling_m": 400}
    ]

    @classmethod
    def assert_invariants(cls, state: Dict[str, Any], intended_command: Optional[str] = None) -> None:
        """
        Pure deterministic evaluation:
        Raises SafetyInvariantViolation if any hard system invariant fails.
        """
        # 1. Critical Battery Invariant
        battery_pct = state.get("battery_pct", 100.0)
        if battery_pct < cls.CRITICAL_BATTERY_PCT:
            if intended_command and intended_command not in ["EMERGENCY_LAND", "LAND", "RTL"]:
                raise SafetyInvariantViolation(
                    "BATTERY_CRITICAL_RESERVE",
                    f"Battery at {battery_pct:.1f}% (<{cls.CRITICAL_BATTERY_PCT}%). Only emergency touchdown permitted."
                )

        # 2. Geofence Boundary Invariant
        lat = state.get("lat", 0.0)
        lon = state.get("lon", 0.0)
        alt = state.get("alt_m", 0.0)
        for zone in cls.RESTRICTED_AIRSPACES:
            if zone["lat_min"] <= lat <= zone["lat_max"] and zone["lon_min"] <= lon <= zone["lon_max"]:
                if zone["floor_m"] <= alt <= zone["ceiling_m"]:
                    raise SafetyInvariantViolation(
                        "RESTRICTED_GEOFENCE_BREACH",
                        f"Vehicle position ({lat:.4f}, {lon:.4f}, {alt:.1f}m) penetrates restricted zone: {zone['name']}"
                    )

        # 3. GPS Loss without Fallback Invariant
        gps_sats = state.get("gps_sats", 12)
        has_vio_fallback = state.get("has_vio_fallback", True)
        if gps_sats < cls.MIN_GPS_SATS_FOR_OFFBOARD and not has_vio_fallback:
            if intended_command in ["OFFBOARD_TRAJECTORY", "CRUISE"]:
                raise SafetyInvariantViolation(
                    "GPS_INSUFFICIENT_NO_FALLBACK",
                    f"GPS satellites ({gps_sats} < {cls.MIN_GPS_SATS_FOR_OFFBOARD}) and no optical flow fallback available."
                )

        # 4. Aerodynamic Centrifugal Roll Envelope Invariant
        roll_deg = abs(state.get("roll_deg", 0.0))
        if roll_deg > cls.MAX_CENTRIFUGAL_ROLL_DEG:
            raise SafetyInvariantViolation(
                "AERODYNAMIC_ROLL_LIMIT_EXCEEDED",
                f"Centrifugal roll ({roll_deg:.1f} deg) exceeds airframe structural stability limit ({cls.MAX_CENTRIFUGAL_ROLL_DEG} deg)."
            )

        logger.debug(f"[SafetyInvariantEngine] All safety invariants verified nominal for command: {intended_command}")

safety_invariant_engine = SafetyInvariantEngine()
