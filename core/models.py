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
    aggression_mode: str = "NOMINAL"



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
    cybersecurity: Optional[Any] = None
    navigation:    Optional[Any] = None
    fleet:         Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        m = self.decision.mpc_output
        ex = self.explainability
        
        d = {
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
                "aggression_mode": self.decision.aggression_mode,
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

        if self.cybersecurity is not None:
            d["cybersecurity"] = {
                "threat_level":     self.cybersecurity.threat_level,
                "is_spoofed":       self.cybersecurity.is_spoofed,
                "firewall_blocks":  self.cybersecurity.firewall_blocks,
                "active_alarms":    self.cybersecurity.active_alarms,
            }
        
        if self.navigation is not None:
            d["navigation"] = {
                "weather_hazard":   self.navigation.weather_hazard_level,
                "landing_x":        self.navigation.safe_landing_site.coord[0],
                "landing_y":        self.navigation.safe_landing_site.coord[1],
                "landing_safety":   self.navigation.safe_landing_site.safety_score,
                "terrain_type":     self.navigation.safe_landing_site.terrain_type,
            }

        if self.fleet is not None:
            d["fleet"] = {
                "fleet_health":     self.fleet.fleet_health_score,
                "active_members":   self.fleet.active_swarm_members,
                "threat_propagated": self.fleet.swarm_threat_propagated,
                "member_states": [
                    {
                        "uav_id":        m.uav_id,
                        "battery":       m.battery,
                        "health_score":  m.health_score,
                        "active_action": m.active_action,
                        "risk_level":    m.risk_level
                    } for m in self.fleet.member_states
                ]
            }

        return d

    def enrich_os_fields(self, os_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge Altaria OS kernel outputs into snapshot dict."""
        d = self.to_dict()
        for key in (
            "sensor_trust", "inference", "survival", "cognition", "vision",
            "route_governance", "twin_physics", "fleet_intelligence",
            "autonomy_mode", "os_version", "operator_required",
        ):
            if key in os_data:
                d[key] = os_data[key]
        if os_data.get("decision"):
            d["decision"] = {**d.get("decision", {}), **os_data["decision"]}
        return d
