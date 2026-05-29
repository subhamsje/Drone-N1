"""Kafka / event bus topic registry."""

from enum import Enum


class Topic(str, Enum):
    TELEMETRY_RAW = "telemetry.raw"
    TELEMETRY_NORMALIZED = "telemetry.normalized"
    TELEMETRY_PRIORITY = "telemetry.priority"
    ANOMALY_DETECTED = "anomaly.detected"
    RISK_SCORE = "risk.score"
    PREDICTION_FAILURE = "prediction.failure"
    RECOVERY_WORKFLOW = "recovery.workflow"
    RECOVERY_COMMAND = "recovery.command"
    MISSION_STATE = "mission.state"
    MISSION_REROUTE = "mission.reroute"
    FLEET_HEALTH = "fleet.health"
    FLEET_ALERT = "fleet.alert"
    CYBER_THREAT = "cyber.threat"
    CYBER_BLOCKED = "cyber.blocked"
    TWIN_SNAPSHOT = "twin.snapshot"
    TWIN_REPLAY = "twin.replay"
    EDGE_SYNC = "edge.sync"
    ML_INFERENCE_REQUEST = "ml.inference.request"
    ML_INFERENCE_RESULT = "ml.inference.result"
    COMMAND_MAVLINK = "command.mavlink"
    AUDIT_COMMANDS = "audit.commands"


TOPIC_PARTITIONS = {
    Topic.TELEMETRY_RAW: 64,
    Topic.TELEMETRY_NORMALIZED: 64,
    Topic.TELEMETRY_PRIORITY: 16,
    Topic.ANOMALY_DETECTED: 32,
    Topic.RISK_SCORE: 32,
    Topic.PREDICTION_FAILURE: 32,
    Topic.RECOVERY_WORKFLOW: 16,
    Topic.RECOVERY_COMMAND: 16,
    Topic.MISSION_STATE: 16,
    Topic.MISSION_REROUTE: 16,
    Topic.FLEET_HEALTH: 8,
    Topic.FLEET_ALERT: 8,
    Topic.CYBER_THREAT: 16,
    Topic.CYBER_BLOCKED: 8,
    Topic.TWIN_SNAPSHOT: 32,
    Topic.TWIN_REPLAY: 8,
    Topic.EDGE_SYNC: 16,
    Topic.ML_INFERENCE_REQUEST: 32,
    Topic.ML_INFERENCE_RESULT: 32,
    Topic.COMMAND_MAVLINK: 16,
    Topic.AUDIT_COMMANDS: 4,
}

CONSUMER_GROUPS = {
    "risk-processor": [Topic.TELEMETRY_NORMALIZED, Topic.ANOMALY_DETECTED],
    "recovery-executor": [Topic.RISK_SCORE, Topic.PREDICTION_FAILURE, Topic.RECOVERY_WORKFLOW],
    "fleet-aggregator": [Topic.FLEET_HEALTH, Topic.RISK_SCORE, Topic.FLEET_ALERT],
    "twin-mirror": [Topic.TELEMETRY_NORMALIZED, Topic.TWIN_SNAPSHOT],
    "cyber-analyzer": [Topic.TELEMETRY_RAW, Topic.CYBER_THREAT],
    "ml-inference": [Topic.ML_INFERENCE_REQUEST],
}
