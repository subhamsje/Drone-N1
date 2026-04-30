"""LSTM Prediction Engine + MC Dropout uncertainty."""

import numpy as np
from typing import List
from core.models import TelemetryFrame, PredictionOutput
from config.settings import SystemConfig


class LSTMPredictionEngine:
    """
    Lightweight LSTM simulation using exponential smoothing.
    MC Dropout approximated via noise sampling for uncertainty.
    """

    def __init__(self, config: SystemConfig):
        cfg = config.prediction
        self._mc_samples = cfg.mc_samples
        self._dropout = cfg.dropout_rate
        self._bat_alpha = 0.15
        self._rpm_alpha = 0.15
        self._alt_alpha = 0.10
        self._pred_battery = None
        self._pred_rpm = None
        self._pred_alt = None

    def predict(self, window: List[TelemetryFrame]) -> PredictionOutput:
        if not window:
            return PredictionOutput(
                battery=100.0, rpm=4500.0, altitude=5.0,
                confidence=0.5, battery_std=1.0, rpm_std=100.0
            )

        latest = window[-1]

        # Initialize from first reading
        if self._pred_battery is None:
            self._pred_battery = latest.battery
            self._pred_rpm = latest.rpm
            self._pred_alt = latest.altitude

        # EMA update (simulates LSTM tracking)
        self._pred_battery = (self._bat_alpha * latest.battery
                              + (1 - self._bat_alpha) * self._pred_battery)
        self._pred_rpm = (self._rpm_alpha * latest.rpm
                          + (1 - self._rpm_alpha) * self._pred_rpm)
        self._pred_alt = (self._alt_alpha * latest.altitude
                          + (1 - self._alt_alpha) * self._pred_alt)

        # MC Dropout uncertainty — sample N times with dropout noise
        bat_samples = self._pred_battery + np.random.normal(0, max(0.5, abs(latest.battery_roc) * 5), self._mc_samples)
        rpm_samples = self._pred_rpm + np.random.normal(0, max(30, abs(latest.rpm_roc) * 20), self._mc_samples)

        bat_std = float(np.std(bat_samples))
        rpm_std = float(np.std(rpm_samples))

        # Confidence: drops when variance is high
        uncertainty = float(np.clip((bat_std / 5.0 + rpm_std / 200.0) / 2.0, 0.0, 1.0))
        confidence = float(np.clip(1.0 - uncertainty, 0.3, 1.0))

        return PredictionOutput(
            battery=float(np.clip(self._pred_battery, 0, 100)),
            rpm=float(max(0, self._pred_rpm)),
            altitude=float(max(0, self._pred_alt)),
            confidence=confidence,
            battery_std=bat_std,
            rpm_std=rpm_std,
        )
