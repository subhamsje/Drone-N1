"""
Autonomy Gradient & Human-AI Control Authority Matrix.
Enforces explicit authority levels and command permissions across the operational spectrum.
"""

from enum import Enum
from typing import Dict, Any, Optional

class AutonomyLevel(str, Enum):
    MANUAL = "MANUAL"                   # 100% Human Pilot, AI purely passive monitor
    ASSISTED = "ASSISTED"               # Human flies setpoints, AI enforces active geofence & obstacle bounce
    SUPERVISED = "SUPERVISED"           # AI executes DAG waypoints, Human approves critical nodes & can pause
    FULLY_AUTONOMOUS = "FULLY_AUTONOMOUS" # AI executes all actions & emergency contingencies, Human monitors

class AutonomyAuthorityManager:
    """Evaluates whether a command is authorized under the active autonomy level."""

    def __init__(self, initial_level: AutonomyLevel = AutonomyLevel.SUPERVISED):
        self.current_level = initial_level

    def set_level(self, level: AutonomyLevel) -> None:
        self.current_level = level

    def validate_command_authority(self, command_name: str, issuer: str) -> Dict[str, Any]:
        """
        issuer: 'HUMAN_OPERATOR' | 'AI_COGNITIVE_KERNEL' | 'SAFETY_OVERRIDE_SYSTEM'
        """
        # Safety overrides always possess unilateral execution authority
        if issuer == "SAFETY_OVERRIDE_SYSTEM":
            return {"authorized": True, "reason": "Safety system override has absolute precedence."}

        if self.current_level == AutonomyLevel.MANUAL:
            if issuer == "AI_COGNITIVE_KERNEL":
                return {"authorized": False, "reason": "System is in MANUAL mode. Autonomous trajectory commands disabled."}
            return {"authorized": True, "reason": "Human manual flight permitted."}

        if self.current_level == AutonomyLevel.ASSISTED:
            return {"authorized": True, "reason": "Assisted flight mode active."}

        if self.current_level == AutonomyLevel.SUPERVISED:
            # High-risk autonomous actions require operator approval
            if issuer == "AI_COGNITIVE_KERNEL" and command_name in ["ARM", "TAKEOFF", "LAND_OFFLINE"]:
                return {"authorized": True, "requires_human_ack": True, "reason": "Supervised mode requires operator ACK."}
            return {"authorized": True, "reason": "Supervised autonomous flight active."}

        if self.current_level == AutonomyLevel.FULLY_AUTONOMOUS:
            return {"authorized": True, "reason": "Full autonomous cognitive authority engaged."}

        return {"authorized": True, "reason": "Default pass."}

autonomy_manager = AutonomyAuthorityManager()
