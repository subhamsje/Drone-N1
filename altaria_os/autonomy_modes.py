"""Autonomy mode controller — governs aggression and human-in-the-loop thresholds."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict


class AutonomyMode(str, Enum):
    MANUAL = "MANUAL"
    ASSISTED = "ASSISTED"
    SUPERVISED = "SUPERVISED"
    AUTONOMOUS = "AUTONOMOUS"
    SURVIVAL = "SURVIVAL"  # full self-preservation authority


@dataclass
class ModePolicy:
    max_risk_tolerance: float
    auto_recovery: bool
    operator_required_above_uncertainty: float
    survival_override: bool


MODE_POLICIES: Dict[AutonomyMode, ModePolicy] = {
    AutonomyMode.MANUAL: ModePolicy(0.9, False, 0.3, False),
    AutonomyMode.ASSISTED: ModePolicy(0.7, False, 0.5, False),
    AutonomyMode.SUPERVISED: ModePolicy(0.5, True, 0.65, False),
    AutonomyMode.AUTONOMOUS: ModePolicy(0.4, True, 0.75, True),
    AutonomyMode.SURVIVAL: ModePolicy(0.2, True, 0.9, True),
}


class AutonomyModeController:
    def __init__(self, initial: AutonomyMode = AutonomyMode.AUTONOMOUS):
        self._mode = initial

    @property
    def mode(self) -> AutonomyMode:
        return self._mode

    @property
    def policy(self) -> ModePolicy:
        return MODE_POLICIES[self._mode]

    def escalate_to_survival(self):
        self._mode = AutonomyMode.SURVIVAL

    def set_mode(self, mode: AutonomyMode):
        self._mode = mode

    def should_auto_recover(self, uncertainty: float) -> bool:
        p = self.policy
        if not p.auto_recovery:
            return False
        if uncertainty > p.operator_required_above_uncertainty and self._mode != AutonomyMode.SURVIVAL:
            return False
        return True
