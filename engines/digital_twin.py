"""Digital Twin State Manager — sliding window + rate of change."""

import numpy as np
from collections import deque
from typing import List

from core.models import PhysicsFrame, EKFState, TelemetryFrame
from config.settings import SystemConfig


class DigitalTwinStateManager:
    def __init__(self, config: SystemConfig):
        cfg = config.digital_twin
        self._window_size = cfg.window_size
        self._alpha = cfg.roc_alpha
        self._history: deque = deque(maxlen=cfg.window_size)
        self.battery_roc = 0.0
        self.rpm_roc = 0.0
        self.alt_roc = 0.0
        self._prev_battery = None
        self._prev_rpm = None
        self._prev_alt = None

    def update(self, frame: PhysicsFrame, ekf: EKFState) -> TelemetryFrame:
        if self._prev_battery is not None:
            db = frame.battery - self._prev_battery
            dr = frame.rpm - self._prev_rpm
            da = frame.altitude - self._prev_alt
            self.battery_roc = self._alpha * db + (1 - self._alpha) * self.battery_roc
            self.rpm_roc = self._alpha * dr + (1 - self._alpha) * self.rpm_roc
            self.alt_roc = self._alpha * da + (1 - self._alpha) * self.alt_roc

        self._prev_battery = frame.battery
        self._prev_rpm = frame.rpm
        self._prev_alt = frame.altitude

        tel = TelemetryFrame(
            altitude=frame.altitude,
            battery=frame.battery,
            rpm=frame.rpm,
            imu=frame.imu,
            battery_roc=self.battery_roc,
            rpm_roc=self.rpm_roc,
            alt_roc=self.alt_roc,
        )
        self._history.append(tel)
        return tel

    def get_window(self) -> List[TelemetryFrame]:
        return list(self._history)

    def get_feature_vector(
        self, tel: TelemetryFrame, pred_battery: float, pred_rpm: float, ekf: EKFState
    ) -> List[float]:
        return [
            tel.altitude,
            tel.battery,
            tel.rpm,
            tel.battery_roc,
            tel.rpm_roc,
            tel.alt_roc,
            pred_battery - tel.battery,
            pred_rpm - tel.rpm,
            ekf.confidence,
            ekf.innovation_mag,
            ekf.covariance_trace,
            float(ekf.x[10]),
            float(ekf.x[11]),
            float(ekf.x[12]),
        ]
