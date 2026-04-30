"""Core data models for UAV Hybrid Digital Twin."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
import numpy as np


class RiskLevel(Enum):
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"


class DecisionAction(Enum):
    NONE           = "NONE"
    THRUST_ADJUST  = "THRUST_ADJUST"
    RETURN_HOME    = "RETURN_HOME"
    EMERGENCY_LAND = "EMERGENCY_LAND"


class SystemState(Enum):
    NOMINAL  = "NOMINAL"
    WARNING  = "WARNING"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"


class FailureSource(Enum):
    NOMINAL          = "Nominal"
    NETWORK_LATENCY  = "Network Latency"
    SENSOR_DRIFT     = "Sensor Drift"
    ACTUATOR_FAILURE = "Actuator Failure"
    AI_UNCERTAINTY   = "AI Uncertainty"


@dataclass
class PhysicsFrame:
    altitude:      float
    pos_x:         float
    pos_y:         float
    vx:            float
    vy:            float
    vz:            float
    quat:          List[float]
    roll_rate:     float
    pitch_rate:    float
    yaw_rate:      float
    motor_thrusts: List[float]
    battery:       float
    rpm:           float
    imu:           List[float]


@dataclass
class TelemetryFrame:
    altitude:    float
    battery:     float
    rpm:         float
    imu:         List[float]
    battery_roc: float = 0.0
    rpm_roc:     float = 0.0
    alt_roc:     float = 0.0


@dataclass
class EKFState:
    x:                np.ndarray
    P:                np.ndarray
    confidence:       float
    innovation_mag:   float
    covariance_trace: float


@dataclass
class PredictionOutput:
    battery:     float
    rpm:         float
    altitude:    float
    confidence:  float
    battery_std: float
    rpm_std:     float


@dataclass
class FusedAnomalyOutput:
    score:      float
    is_anomaly: bool
    if_score:   float
    mcd_score:  float
    uncertainty: float


@dataclass
class IntegratedRiskOutput:
    value:          float
    level:          RiskLevel
    r_mechanical:   float
    r_sensor:       float
    r_comms:        float
    r_ai:           float
    dominant_source: FailureSource


@dataclass
class TTFOutput:
    minutes:    float
    confidence: float


@dataclass
class MPCOutput:
    u_optimal:      List[float]
    converged:      bool
    iterations:     int
    time_budget_ms: float
    time_used_ms:   float
    cost:           float
    implied_action: DecisionAction


@dataclass
class DecisionOutput:
    action:          DecisionAction
    confidence:      float
    score_breakdown: Dict[str, float]
    mpc_output:      Optional[MPCOutput] = None


@dataclass
class ExplainabilityOutput:
    root_cause:            str
    dominant_signal:       str
    failure_source:        FailureSource
    ekf_confidence:        float
    ekf_covariance_trace:  float
    mpc_iters:             int
    mpc_converged:         bool
    mpc_implied_action:    str
    ai_uncertainty:        float
    r_mechanical:          float
    r_sensor:              float
    r_comms:               float
    r_ai:                  float
    signal_contributions:  Dict[str, float] = field(default_factory=dict)


@dataclass
class ActionEffect:
    action:          str
    recovery_factor: float
    description:     str


@dataclass
class SystemSnapshot:
    timestamp:     float
    cycle:         int
    physics:       PhysicsFrame
    ekf:           EKFState
    telemetry:     TelemetryFrame
    prediction:    PredictionOutput
    anomaly:       FusedAnomalyOutput
    risk:          IntegratedRiskOutput
    ttf:           TTFOutput
    decision:      DecisionOutput
    explainability: ExplainabilityOutput
    action_effect: ActionEffect
    system_state:  SystemState

    def to_dict(self) -> Dict[str, Any]:
        m = self.decision.mpc_output
        ex = self.explainability
        return {
            "timestamp":   self.timestamp,
            "cycle":       self.cycle,
            "system_state": self.system_state.value,
            "physics": {
                "altitude": self.physics.altitude,
                "battery":  self.physics.battery,
                "rpm":      self.physics.rpm,
                "imu":      self.physics.imu,
                "motor_thrusts": self.physics.motor_thrusts,
            },
            "ekf": {
                "confidence":       self.ekf.confidence,
                "covariance_trace": self.ekf.covariance_trace,
                "innovation_mag":   self.ekf.innovation_mag,
            },
            "prediction": {
                "battery":     self.prediction.battery,
                "rpm":         self.prediction.rpm,
                "altitude":    self.prediction.altitude,
                "confidence":  self.prediction.confidence,
                "battery_std": self.prediction.battery_std,
            },
            "anomaly": {
                "score":      self.anomaly.score,
                "is_anomaly": self.anomaly.is_anomaly,
                "if_score":   self.anomaly.if_score,
                "mcd_score":  self.anomaly.mcd_score,
                "uncertainty": self.anomaly.uncertainty,
                "dominant":   "ISO-FOREST" if self.anomaly.if_score > self.anomaly.mcd_score else "MCD-NPU",
            },
            "risk": {
                "value":        self.risk.value,
                "level":        self.risk.level.value,
                "r_mechanical": self.risk.r_mechanical,
                "r_sensor":     self.risk.r_sensor,
                "r_comms":      self.risk.r_comms,
                "r_ai":         self.risk.r_ai,
                "dominant_src": self.risk.dominant_source.value,
            },
            "ttf": self.ttf.minutes,
            "decision": {
                "action":     self.decision.action.value,
                "confidence": self.decision.confidence,
                "mpc_iters":  m.iterations if m else 0,
                "mpc_cost":   m.cost if m else 0.0,
                "scores":     self.decision.score_breakdown,
            },
            "explainability": {
                "root_cause":      ex.root_cause,
                "dominant_signal": ex.dominant_signal,
                "deviation":       ex.r_mechanical,
                "failure_source":  ex.failure_source.value,
            },
            "action_effect": {
                "action":          self.action_effect.action,
                "recovery_factor": self.action_effect.recovery_factor,
                "description":     self.action_effect.description,
            },
        }
