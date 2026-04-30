"""4-Quadrant Integrated Risk Engine."""

import numpy as np
from collections import deque
from core.models import (
    TelemetryFrame, PredictionOutput, FusedAnomalyOutput,
    EKFState, IntegratedRiskOutput, RiskLevel, FailureSource
)
from config.settings import SystemConfig


class IntegratedRiskEngine:
    def __init__(self, config: SystemConfig):
        cfg = config.risk
        self._alpha = cfg.ema_alpha
        self._k = cfg.sigmoid_k
        self._x0 = cfg.sigmoid_x0
        self._w_mech = cfg.w_mechanical
        self._w_sens = cfg.w_sensor
        self._w_comms = cfg.w_comms
        self._w_ai = cfg.w_ai
        self._ema_risk = 0.0
        self._risk_history: deque = deque(maxlen=cfg.gradient_window)

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + np.exp(-self._k * (x - self._x0)))

    def compute(
        self,
        telemetry: TelemetryFrame,
        prediction: PredictionOutput,
        anomaly: FusedAnomalyOutput,
        ekf: EKFState,
        fault_losses: np.ndarray,
        comm_delay: float,
        battery_roc: float,
        rpm_roc: float,
    ) -> IntegratedRiskOutput:

        # Mechanical risk: fault losses + RPM deviation
        fault_mag = float(np.max(fault_losses))
        rpm_dev = abs(telemetry.rpm - prediction.rpm) / max(1.0, prediction.rpm)
        r_mech = float(np.clip(
            self._sigmoid(0.6 * fault_mag + 0.4 * rpm_dev), 0.0, 1.0
        ))

        # Sensor risk: EKF covariance inflation + battery deviation
        bat_dev = abs(telemetry.battery - prediction.battery) / max(1.0, abs(prediction.battery))
        cov_norm = float(np.clip(ekf.covariance_trace / 50.0, 0.0, 1.0))
        r_sens = float(np.clip(
            self._sigmoid(0.5 * bat_dev + 0.3 * cov_norm + 0.2 * ekf.innovation_mag), 0.0, 1.0
        ))

        # Comms risk: delay + loss proxy
        delay_norm = float(np.clip(comm_delay / 0.1, 0.0, 1.0))
        r_comms = float(np.clip(self._sigmoid(delay_norm), 0.0, 1.0))

        # AI risk: anomaly score + uncertainty
        r_ai = float(np.clip(
            0.7 * anomaly.score + 0.3 * anomaly.uncertainty, 0.0, 1.0
        ))

        raw = (
            self._w_mech  * r_mech +
            self._w_sens  * r_sens +
            self._w_comms * r_comms +
            self._w_ai    * r_ai
        )

        # EMA smoothing
        self._ema_risk = self._alpha * raw + (1 - self._alpha) * self._ema_risk
        value = float(np.clip(self._ema_risk, 0.0, 1.0))
        self._risk_history.append(value)

        # Risk level
        if value >= 0.80:
            level = RiskLevel.CRITICAL
        elif value >= 0.55:
            level = RiskLevel.HIGH
        elif value >= 0.30:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        # Dominant failure source
        src_scores = {
            FailureSource.ACTUATOR_FAILURE: r_mech,
            FailureSource.SENSOR_DRIFT:     r_sens,
            FailureSource.NETWORK_LATENCY:  r_comms,
            FailureSource.AI_UNCERTAINTY:   r_ai,
        }
        dominant = max(src_scores, key=src_scores.get)
        if value < 0.25:
            dominant = FailureSource.NOMINAL

        return IntegratedRiskOutput(
            value=value,
            level=level,
            r_mechanical=r_mech,
            r_sensor=r_sens,
            r_comms=r_comms,
            r_ai=r_ai,
            dominant_source=dominant,
        )

    def get_risk_gradient(self) -> float:
        h = list(self._risk_history)
        if len(h) < 2:
            return 0.0
        return float(np.mean(np.diff(h)))
