"""Tier-1 cognitive OS data models — sensor trust, survival, inference, vision."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SensorTrustState:
    gps_confidence: float
    imu_confidence: float
    baro_confidence: float
    vision_confidence: float
    lidar_confidence: float
    magnetometer_confidence: float
    fusion_confidence: float
    imu_drift_risk: str  # LOW | MEDIUM | HIGH
    degraded_sensors: List[str] = field(default_factory=list)
    primary_nav_source: str = "gps"  # gps | visual_odometry | dead_reckoning

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gps_confidence": round(self.gps_confidence, 3),
            "imu_confidence": round(self.imu_confidence, 3),
            "vision_confidence": round(self.vision_confidence, 3),
            "fusion_confidence": round(self.fusion_confidence, 3),
            "imu_drift_risk": self.imu_drift_risk,
            "degraded_sensors": self.degraded_sensors,
            "primary_nav_source": self.primary_nav_source,
        }


@dataclass
class FailurePrediction:
    battery_collapse_prob: float
    motor_degradation_prob: float
    esc_overheat_prob: float
    vibration_anomaly_prob: float
    gps_spoof_prob: float
    comm_failure_prob: float
    crash_probability: float
    mission_failure_prob: float
    turbulence_risk: float
    thermal_overload_prob: float
    model_confidence: float
    inference_latency_ms: float
    model_version: str = "v1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {k: round(v, 4) if isinstance(v, float) else v
                for k, v in self.__dict__.items()}


@dataclass
class ScenarioOutcome:
    action: str
    survival_probability: float
    payload_safety: float
    human_risk: float
    energy_cost: float
    time_to_execute_s: float


@dataclass
class SurvivalPlan:
    strategy: str
    urgency: str
    survival_score: float
    scenarios_evaluated: int
    best_outcome: ScenarioOutcome
    backup_nav: str
    thrust_redistribution: bool
    emergency_power_mode: bool
    landing_site_rank: Optional[Dict[str, Any]] = None
    verification_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy,
            "urgency": self.urgency,
            "survival_score": round(self.survival_score, 4),
            "scenarios_evaluated": self.scenarios_evaluated,
            "best_outcome": {
                "action": self.best_outcome.action,
                "survival_probability": round(self.best_outcome.survival_probability, 4),
                "payload_safety": round(self.best_outcome.payload_safety, 4),
                "human_risk": round(self.best_outcome.human_risk, 4),
            },
            "backup_nav": self.backup_nav,
            "thrust_redistribution": self.thrust_redistribution,
            "emergency_power_mode": self.emergency_power_mode,
            "landing_site_rank": self.landing_site_rank,
        }


@dataclass
class CognitionOutput:
    recommended_action: str
    confidence: float
    utility_scores: Dict[str, float]
    aggression_mode: str
    uncertainty: float
    reasoning_factors: Dict[str, float]
    operator_intervention: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommended_action": self.recommended_action,
            "confidence": round(self.confidence, 4),
            "utility_scores": {k: round(v, 4) for k, v in self.utility_scores.items()},
            "aggression_mode": self.aggression_mode,
            "uncertainty": round(self.uncertainty, 4),
            "reasoning_factors": {k: round(v, 4) for k, v in self.reasoning_factors.items()},
            "operator_intervention": self.operator_intervention,
        }


@dataclass
class VisionAutonomyState:
    visual_odometry_active: bool
    slam_confidence: float
    obstacle_density: float
    landing_zones_detected: int
    gps_denied_mode: bool
    depth_available: bool
    semantic_hazards: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in self.__dict__.items()}


@dataclass
class RouteGovernanceState:
    reroute_required: bool
    corridor_risk: float
    battery_feasible: bool
    no_fly_violation: bool
    semantic_compliance: float
    recommended_altitude_m: float
    congestion_level: float

    def to_dict(self) -> Dict[str, Any]:
        return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in self.__dict__.items()}


@dataclass
class TwinPhysicsForecast:
    wind_field_estimate: List[float]
    turbulence_index: float
    vibration_propagation: float
    thrust_degradation_forecast: float
    instability_horizon_s: float
    replay_available: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "wind_field_estimate": [round(v, 3) for v in self.wind_field_estimate],
            "turbulence_index": round(self.turbulence_index, 4),
            "vibration_propagation": round(self.vibration_propagation, 4),
            "thrust_degradation_forecast": round(self.thrust_degradation_forecast, 4),
            "instability_horizon_s": round(self.instability_horizon_s, 2),
        }


@dataclass
class FleetIntelligenceState:
    shared_threats: List[str]
    learned_zones: List[Dict[str, Any]]
    cross_drone_anomalies: int
    map_version: str

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__
