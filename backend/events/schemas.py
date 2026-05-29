"""Event schemas for the autonomous event-driven backbone."""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
import time
import uuid


class EventType(str, Enum):
    TELEMETRY_INGESTED = "telemetry.ingested"
    TELEMETRY_NORMALIZED = "telemetry.normalized"
    ANOMALY_DETECTED = "anomaly.detected"
    RISK_UPDATED = "risk.updated"
    PREDICTION_FAILURE = "prediction.failure"
    RECOVERY_STARTED = "recovery.started"
    RECOVERY_COMPLETED = "recovery.completed"
    RECOVERY_FAILED = "recovery.failed"
    MISSION_UPDATED = "mission.updated"
    MISSION_REROUTE = "mission.reroute"
    FLEET_HEALTH = "fleet.health"
    FLEET_ALERT = "fleet.alert"
    CYBER_THREAT = "cyber.threat"
    CYBER_BLOCKED = "cyber.blocked"
    TWIN_SNAPSHOT = "twin.snapshot"
    COMMAND_AUTHORIZED = "command.authorized"
    COMMAND_REJECTED = "command.rejected"
    EDGE_SYNC = "edge.sync"
    INFERENCE_REQUEST = "inference.request"
    INFERENCE_RESULT = "inference.result"


@dataclass
class DomainEvent:
    event_id: str
    event_type: EventType
    uav_id: str
    timestamp: float
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    fleet_id: Optional[str] = None
    source: str = "altaria-backend"

    @classmethod
    def create(
        cls,
        event_type: EventType,
        uav_id: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        fleet_id: Optional[str] = None,
    ) -> "DomainEvent":
        return cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            uav_id=uav_id,
            timestamp=time.time(),
            payload=payload,
            correlation_id=correlation_id,
            fleet_id=fleet_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "uav_id": self.uav_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "fleet_id": self.fleet_id,
            "source": self.source,
        }


@dataclass
class RecoveryWorkflowState:
    workflow_id: str
    uav_id: str
    policy: str
    severity: str
    status: str  # pending | executing | completed | failed
    started_at: float
    completed_at: Optional[float] = None
    steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
