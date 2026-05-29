"""Autonomous recovery orchestrator — policy engine + workflow executor."""

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from backend.events.bus import get_event_bus
from backend.events.schemas import DomainEvent, EventType, RecoveryWorkflowState
from backend.events.topics import Topic
from backend.mavlink.gateway import MAVLinkGateway

logger = logging.getLogger("recovery_service")


class RecoveryPolicy:
    NONE = "NONE"
    THRUST_ADJUST = "THRUST_ADJUST"
    RETURN_HOME = "RETURN_HOME"
    EMERGENCY_LAND = "EMERGENCY_LAND"
    REROUTE = "REROUTE"
    OPERATOR_ESCALATE = "OPERATOR_ESCALATE"
    HOLD = "HOLD"


class RecoveryOrchestrator:
    """
    Observe → Predict → Evaluate Risk → Decide → Recover → Verify → Learn
    Maps cognitive decision outputs to MAVLink commands and workflow events.
    """

    RISK_THRESHOLDS = {
        "CRITICAL": 0.75,
        "HIGH": 0.55,
        "MEDIUM": 0.35,
    }

    def __init__(self, uav_id: str, mavlink: Optional[MAVLinkGateway] = None):
        self.uav_id = uav_id
        self.mavlink = mavlink or MAVLinkGateway(uav_id)
        self._bus = get_event_bus()
        self._active_workflows: Dict[str, RecoveryWorkflowState] = {}
        self._completed: List[RecoveryWorkflowState] = []

    def evaluate_policy(self, snapshot: Dict[str, Any]) -> str:
        risk = snapshot.get("risk", {})
        value = float(risk.get("value", 0))
        level = risk.get("level", "LOW")
        decision = snapshot.get("decision", {})
        action = decision.get("action", "NONE")
        cyber = snapshot.get("cybersecurity", {})
        ttf = float(snapshot.get("ttf", 99))

        if cyber.get("is_spoofed"):
            return RecoveryPolicy.HOLD

        if level == "CRITICAL" or value >= self.RISK_THRESHOLDS["CRITICAL"]:
            if action == "EMERGENCY_LAND" or ttf < 0.5:
                return RecoveryPolicy.EMERGENCY_LAND
            return RecoveryPolicy.RETURN_HOME

        if level == "HIGH" or value >= self.RISK_THRESHOLDS["HIGH"]:
            if action in ("RETURN_HOME", "EMERGENCY_LAND"):
                return action
            return RecoveryPolicy.THRUST_ADJUST

        if level == "MEDIUM" or value >= self.RISK_THRESHOLDS["MEDIUM"]:
            return RecoveryPolicy.THRUST_ADJUST

        return RecoveryPolicy.NONE

    async def process_snapshot(self, snapshot: Dict[str, Any]) -> Optional[RecoveryWorkflowState]:
        policy = self.evaluate_policy(snapshot)
        if policy == RecoveryPolicy.NONE:
            return None

        workflow_id = str(uuid.uuid4())
        severity = snapshot.get("risk", {}).get("level", "UNKNOWN")
        wf = RecoveryWorkflowState(
            workflow_id=workflow_id,
            uav_id=self.uav_id,
            policy=policy,
            severity=severity,
            status="executing",
            started_at=time.time(),
            steps=["evaluate_risk", "select_policy", "authorize_command"],
            metadata={"risk_value": snapshot.get("risk", {}).get("value")},
        )
        self._active_workflows[workflow_id] = wf

        await self._bus.publish(
            DomainEvent.create(
                EventType.RECOVERY_STARTED,
                self.uav_id,
                wf.to_dict(),
                correlation_id=workflow_id,
            ),
            Topic.RECOVERY_WORKFLOW,
        )

        await self._execute_recovery(policy, snapshot, wf)
        return wf

    async def _execute_recovery(
        self,
        policy: str,
        snapshot: Dict[str, Any],
        wf: RecoveryWorkflowState,
    ):
        # Prefer survival strategy from OS kernel when present
        survival = snapshot.get("survival", {})
        strategy = survival.get("strategy", policy)
        landing = snapshot.get("landing_zone", {})

        try:
            from backend.execution.px4_bridge import PX4Bridge
            if not hasattr(self, "_px4"):
                import os
                mode = os.getenv("PX4_MODE", "sitl")
                self._px4 = PX4Bridge(self.uav_id, mode)
                await self._px4.start()
            lz = None
            if landing:
                pos = landing.get("position", [0, 0])
                lz = {"lat": pos[0], "lon": pos[1], "alt": 0}
            exec_result = await self._px4.execute_survival(strategy, lz)
            wf.steps.append(f"mavsdk:{strategy}:{'ok' if exec_result.success else exec_result.message}")
        except Exception as e:
            command_map = {
                RecoveryPolicy.EMERGENCY_LAND: "MAV_CMD_NAV_LAND",
                RecoveryPolicy.RETURN_HOME: "MAV_CMD_NAV_RETURN_TO_LAUNCH",
                RecoveryPolicy.THRUST_ADJUST: "MAV_CMD_DO_MOTOR_TEST",
                RecoveryPolicy.HOLD: "MAV_CMD_NAV_LOITER_UNLIM",
                RecoveryPolicy.REROUTE: "MAV_CMD_DO_REPOSITION",
            }
            cmd = command_map.get(policy)
            if cmd:
                nav = snapshot.get("navigation", {})
                params = {}
                if policy == RecoveryPolicy.EMERGENCY_LAND and nav:
                    params = {
                        "landing_x": nav.get("landing_x"),
                        "landing_y": nav.get("landing_y"),
                        "safety_score": nav.get("landing_safety"),
                    }
                verdict = await self.mavlink.submit_command(
                    cmd, params=params, source="recovery-orchestrator"
                )
                wf.steps.append(f"command:{cmd}:{'ok' if verdict.allowed else verdict.reason}")
            else:
                wf.steps.append(f"exec_error:{e}")

        wf.status = "completed"
        wf.completed_at = time.time()
        self._completed.append(wf)
        del self._active_workflows[wf.workflow_id]

        await self._bus.publish(
            DomainEvent.create(
                EventType.RECOVERY_COMPLETED,
                self.uav_id,
                wf.to_dict(),
                correlation_id=wf.workflow_id,
            ),
            Topic.RECOVERY_WORKFLOW,
        )
        logger.info("[%s] Recovery completed: %s", self.uav_id, policy)

    async def trigger_manual(self, policy: str, reason: str = "operator_override") -> RecoveryWorkflowState:
        snapshot = {"risk": {"value": 1.0, "level": "CRITICAL"}, "decision": {"action": policy}}
        wf = await self.process_snapshot(snapshot)
        if wf:
            wf.metadata["manual"] = True
            wf.metadata["reason"] = reason
        return wf

    def get_active_workflows(self) -> List[Dict]:
        return [w.to_dict() for w in self._active_workflows.values()]
