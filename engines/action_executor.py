"""Action Executor — maps decisions to physics feedback."""

import logging
from core.models import DecisionAction, DecisionOutput, IntegratedRiskOutput, ActionEffect, SystemState, RiskLevel
from config.settings import SystemConfig

logger = logging.getLogger("action_executor")


class ActionExecutor:
    def __init__(self, config: SystemConfig):
        self.target_z = config.physics.initial_altitude
        self._recovery = 0.0

    def execute(
        self,
        action: DecisionAction,
        risk: IntegratedRiskOutput,
        mpc_dt: float,
        physics_engine,
    ):
        if action == DecisionAction.EMERGENCY_LAND:
            self._recovery = 0.30
            self.target_z = 0.0
            desc = "Emergency landing engaged — fault mitigation active"
        elif action == DecisionAction.RETURN_HOME:
            self._recovery = 0.12
            desc = "Return home — stabilization mode"
        elif action == DecisionAction.THRUST_ADJUST:
            self._recovery = 0.07
            desc = "Thrust rebalancing — partial fault mitigation"
        else:
            self._recovery = max(0.0, self._recovery * 0.9)
            desc = "Nominal operation"

        physics_engine.apply_action_feedback(action.value, self._recovery)

        effect = ActionEffect(
            action=action.value,
            recovery_factor=self._recovery,
            description=desc,
        )

        if risk.level == RiskLevel.CRITICAL:
            state = SystemState.CRITICAL
        elif risk.level == RiskLevel.HIGH:
            state = SystemState.HIGH
        elif risk.level == RiskLevel.MEDIUM:
            state = SystemState.WARNING
        else:
            state = SystemState.NOMINAL

        return effect, state, self._recovery
