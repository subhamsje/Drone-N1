"""System configuration for UAV Hybrid Digital Twin."""

from dataclasses import dataclass, field
from typing import List
import numpy as np


@dataclass
class PhysicsConfig:
    mass:               float = 1.5
    gravity:            float = 9.81
    arm_length:         float = 0.23
    c_tau:              float = 0.016
    c_drag:             float = 0.08
    max_motor_cmd:      float = 15.0
    hover_thrust:       float = 5.42
    initial_altitude:   float = 5.0
    wind_std:           float = 0.05
    fault_onset_time:   float = 6.0
    fault_motor_index:  int   = 0
    fault_loss_ramp_rate: float = 0.04
    tau_motors:         List[float] = field(default_factory=lambda: [0.05, 0.05, 0.05, 0.05])


@dataclass
class EKFConfig:
    dt:                   float = 0.02
    process_noise_base:   float = 1e-4
    bias_process_noise:   float = 1e-6
    measurement_noise:    float = 0.01
    rollback_buffer_depth: int  = 20
    mahal_reject_threshold: float = 25.0
    comm_loss_prob:       float = 0.05
    comm_delay_min:       float = 0.01
    comm_delay_max:       float = 0.08


@dataclass
class DigitalTwinConfig:
    window_size: int = 30
    roc_alpha:   float = 0.2


@dataclass
class PredictionConfig:
    lstm_hidden:    int   = 32
    mc_samples:     int   = 10
    dropout_rate:   float = 0.1
    input_features: int   = 6
    output_features: int  = 3


@dataclass
class AnomalyConfig:
    if_contamination:  float = 0.1
    if_n_estimators:   int   = 50
    mcd_threshold:     float = 0.5
    fusion_alpha:      float = 0.5
    anomaly_threshold: float = 0.55
    warmup_cycles:     int   = 15


@dataclass
class RiskConfig:
    ema_alpha:          float = 0.3
    sigmoid_k:          float = 8.0
    sigmoid_x0:         float = 0.5
    gradient_window:    int   = 5
    w_mechanical:       float = 0.35
    w_sensor:           float = 0.25
    w_comms:            float = 0.20
    w_ai:               float = 0.20


@dataclass
class TTFConfig:
    base_ttf_minutes:    float = 8.0
    gradient_sensitivity: float = 3.0
    min_ttf:             float = 0.05


@dataclass
class MPCConfig:
    horizon:            int   = 5
    budget_low_ms:      float = 20.0
    budget_high_ms:     float = 60.0
    max_iters_low:      int   = 5
    max_iters_high:     int   = 15
    altitude_cost:      float = 20.0
    attitude_cost:      float = 1.0
    yaw_cost:           float = 0.5
    quaternion_cost:    float = 0.5
    control_cost:       float = 0.01
    delta_control_cost: float = 0.05
    grad_norm_tol:      float = 0.01
    line_search_steps:  int   = 6
    armijo_c:           float = 1e-4


@dataclass
class DecisionConfig:
    emergency_land_score: float = 0.38
    return_home_score:    float = 0.30
    thrust_adjust_score:  float = 0.18
    confidence_decay:     float = 0.85


@dataclass
class StreamConfig:
    websocket_host:   str = "localhost"
    websocket_port:   int = 8765
    json_output_path: str = "uav_stream.jsonl"
    buffer_size:      int = 100


@dataclass
class SystemConfig:
    physics:     PhysicsConfig     = field(default_factory=PhysicsConfig)
    ekf:         EKFConfig         = field(default_factory=EKFConfig)
    digital_twin: DigitalTwinConfig = field(default_factory=DigitalTwinConfig)
    prediction:  PredictionConfig  = field(default_factory=PredictionConfig)
    anomaly:     AnomalyConfig     = field(default_factory=AnomalyConfig)
    risk:        RiskConfig        = field(default_factory=RiskConfig)
    ttf:         TTFConfig         = field(default_factory=TTFConfig)
    mpc:         MPCConfig         = field(default_factory=MPCConfig)
    decision:    DecisionConfig    = field(default_factory=DecisionConfig)
    stream:      StreamConfig      = field(default_factory=StreamConfig)


CONFIG = SystemConfig()
