"""
Deterministic Safety Envelope — hard constraints cognition cannot violate.
Independent of ML outputs; policy-enforced flight limits.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("safety.envelope")


class ProtectedState(str, Enum):
    NOMINAL_FLIGHT = "NOMINAL_FLIGHT"
    DEGRADED_NAV = "DEGRADED_NAV"
    RECOVERY_ACTIVE = "RECOVERY_ACTIVE"
    EMERGENCY_ONLY = "EMERGENCY_ONLY"
    GROUNDED = "GROUNDED"


@dataclass
class SafetyEnvelope:
    max_altitude_m: float = 120.0
    max_speed_ms: float = 25.0
    min_battery_rtl_pct: float = 20.0
    min_battery_land_pct: float = 10.0
    max_risk_allowed: float = 0.92
    max_uncertainty_allowed: float = 0.88
    geofence_enabled: bool = True
    allowed_commands_in_emergency: Tuple[str, ...] = ("EMERGENCY_LAND", "LAND", "HOLD", "RTL", "RETURN_HOME")


class DeterministicSafetyController:
    """
    Independent safety controller — enforces envelopes before any command reaches MAVSDK.
    """

    def __init__(self, envelope: Optional[SafetyEnvelope] = None):
        self.envelope = envelope or SafetyEnvelope()
        self._protected_state = ProtectedState.NOMINAL_FLIGHT
        self._violations: List[Dict] = []

    @property
    def protected_state(self) -> ProtectedState:
        return self._protected_state

    def evaluate_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Update protected state from telemetry — deterministic rules only."""
        risk = float(snapshot.get("risk", {}).get("value", 0))
        batt = float(snapshot.get("physics", {}).get("battery", 100))
        unc = float(snapshot.get("confidence", {}).get("global_uncertainty", 0))
        survival_u = snapshot.get("survival", {}).get("urgency", "NORMAL")

        if batt < self.envelope.min_battery_land_pct:
            self._protected_state = ProtectedState.EMERGENCY_ONLY
        elif survival_u in ("IMMEDIATE", "HIGH") or risk > 0.75:
            self._protected_state = ProtectedState.RECOVERY_ACTIVE
        elif unc > 0.7 or snapshot.get("navigation_state", {}).get("mode") != "gps":
            self._protected_state = ProtectedState.DEGRADED_NAV
        else:
            self._protected_state = ProtectedState.NOMINAL_FLIGHT

        return {
            "protected_state": self._protected_state.value,
            "envelope_ok": self._check_envelope(snapshot),
        }

    def _check_envelope(self, snapshot: Dict[str, Any]) -> bool:
        alt = float(snapshot.get("physics", {}).get("altitude", 0))
        risk = float(snapshot.get("risk", {}).get("value", 0))
        if alt > self.envelope.max_altitude_m:
            self._record_violation("altitude_cap", alt)
            return False
        if risk > self.envelope.max_risk_allowed:
            self._record_violation("risk_cap", risk)
            return False
        return True

    def authorize_command(self, command: str, snapshot: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Returns (authorized, reason).
        Cognition layer MUST pass commands through this gate.
        """
        self.evaluate_snapshot(snapshot)

        if self._protected_state == ProtectedState.EMERGENCY_ONLY:
            if command not in self.envelope.allowed_commands_in_emergency:
                return False, "emergency_only_landing_allowed"

        if self._protected_state == ProtectedState.GROUNDED:
            return False, "aircraft_grounded"

        batt = float(snapshot.get("physics", {}).get("battery", 100))
        if command in ("NONE", "THRUST_ADJUST") and batt < self.envelope.min_battery_rtl_pct:
            return False, "battery_rtl_required"

        unc = float(snapshot.get("confidence", {}).get("global_uncertainty", 0))
        if unc > self.envelope.max_uncertainty_allowed and command == "NONE":
            return False, "uncertainty_mandates_action"

        alt = float(snapshot.get("physics", {}).get("altitude", 0))
        if alt > self.envelope.max_altitude_m:
            return False, "altitude_violation"

        return True, "authorized"

    def _record_violation(self, vtype: str, value: float):
        self._violations.append({"type": vtype, "value": value})
        if len(self._violations) > 500:
            self._violations = self._violations[-250:]

    def get_violations(self, limit: int = 20) -> List[Dict]:
        return self._violations[-limit:]
