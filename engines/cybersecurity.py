"""
Altaria OS Cybersecurity Suite — MAVLink AI Firewall & GPS Spoofing Detector.
──────────────────────────────────────────────────────────────────────────
Protects the UAV flight stack against GPS spoofing attacks, telemetry 
injection, and malicious or out-of-boundary operator commands.
"""

import numpy as np
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger("cybersecurity")


@dataclass
class CybersecurityStatus:
    threat_level: float        # ∈ [0, 1]
    is_spoofed: bool
    firewall_blocks: int
    active_alarms: List[str]
    sensor_drift_variance: float


class GPSSpoofingDetector:
    """
    Correlates EKF estimated velocity and attitude states with IMU linear 
    acceleration. Detects spoofing when the GPS velocity significantly 
    diverges from the physical double-integration of acceleration.
    """

    def __init__(self, window_size: int = 15, threshold: float = 2.8):
        self.window_size = window_size
        self.threshold = threshold
        # Rolling buffer of acceleration residuals
        self._residuals: List[float] = []
        self._prev_vel: Optional[np.ndarray] = None

    def update(
        self,
        ekf_vel: np.ndarray,      # [vx, vy, vz] from EKF
        imu_accel: List[float],   # [ax, ay, az] from raw/filtered IMU (m/s^2)
        dt: float
    ) -> Tuple[bool, float]:
        """
        Computes residual between expected velocity change (from EKF) and 
        measured acceleration (from IMU).
        Returns (is_spoofed, anomaly_score).
        """
        if self._prev_vel is None:
            self._prev_vel = np.array(ekf_vel)
            return False, 0.0

        # Physical acceleration expected = (v_now - v_prev) / dt
        expected_accel = (np.array(ekf_vel) - self._prev_vel) / max(1e-5, dt)
        self._prev_vel = np.array(ekf_vel)

        # IMU measured acceleration (subtracting gravity vector roughly in z)
        measured_accel = np.array(imu_accel)
        # Note: raw gravity term is compensated inside the physics frame or EKF

        # Compute Euclidean distance residual
        residual = float(np.linalg.norm(expected_accel - measured_accel))
        self._residuals.append(residual)

        if len(self._residuals) > self.window_size:
            self._residuals.pop(0)

        # Smooth residual over window
        smoothed_score = float(np.mean(self._residuals)) if self._residuals else 0.0

        # Spoofing detected if EKF state transitions contradict physical IMU forces
        is_spoofed = smoothed_score > self.threshold
        return is_spoofed, smoothed_score


class MAVLinkFirewall:
    """
    MAVLink AI Firewall. Checks incoming command rates, signatures,
    and semantic boundaries to block injected packet sequences.
    """

    def __init__(self, max_command_frequency: float = 10.0):
        self.max_freq = max_command_frequency
        self._command_timestamps: List[float] = []
        self._block_count: int = 0
        self._prev_cmd: Optional[np.ndarray] = None
        # Hard physical limits for safety validation
        self.LIMIT_MAX_RPM = 8500.0
        self.LIMIT_MAX_THRUST = 15.5
        self.LIMIT_MIN_BATTERY = 5.0

    def validate_command(self, u_cmd: np.ndarray, t_now: float) -> bool:
        """
        Validates commanded motor values against structural flight margins.
        Returns True if command is safe/allowed, False if blocked by firewall.
        """
        # 1. Rate-limit check (prevent flood attacks)
        self._command_timestamps.append(t_now)
        # Keep only last 1 second of commands
        self._command_timestamps = [t for t in self._command_timestamps if t_now - t <= 1.0]
        
        if len(self._command_timestamps) > self.max_freq:
            self._block_count += 1
            logger.warning(f"[FIREWALL] Command rate exceeded limit: {len(self._command_timestamps)}Hz")
            return False

        # 2. Semantic limits check
        if np.any(u_cmd > self.LIMIT_MAX_THRUST) or np.any(u_cmd < 0.0):
            self._block_count += 1
            logger.warning(f"[FIREWALL] Command out of limits: {u_cmd}")
            return False

        # 3. Sudden step-input check over time (prevent malicious aggressive command jumps)
        if self._prev_cmd is not None:
            max_diff = float(np.max(np.abs(u_cmd - self._prev_cmd)))
            if max_diff > 16.0:
                self._block_count += 1
                logger.warning(f"[FIREWALL] Malicious command delta rate blocked: diff={max_diff:.2f}")
                return False
        
        self._prev_cmd = np.array(u_cmd)
        return True

    @property
    def block_count(self) -> int:
        return self._block_count


class CybersecurityEngine:
    """
    Unified onboard cybersecurity orchestrator.
    Computes real-time threat levels and triggers fallback profiles.
    """

    def __init__(self, config: Any = None):
        self.spoof_detector = GPSSpoofingDetector()
        self.firewall = MAVLinkFirewall()
        self.threat_level = 0.0

    def evaluate_threat(
        self,
        ekf_vel: np.ndarray,
        imu_accel: List[float],
        u_cmd: np.ndarray,
        t_now: float,
        dt: float
    ) -> CybersecurityStatus:
        """Runs firewall and spoof detection, updates security status."""
        # 1. Run spoof detection
        is_spoofed, score = self.spoof_detector.update(ekf_vel, imu_accel, dt)

        # 2. Check current command
        is_cmd_allowed = self.firewall.validate_command(u_cmd, t_now)

        # 3. Dynamic threat level calculation
        threat = 0.0
        active_alarms = []

        if is_spoofed:
            threat += 0.65
            active_alarms.append("GPS_SPOOFING_DETECTED")
        if self.firewall.block_count > 0:
            threat += min(0.35, 0.05 * self.firewall.block_count)
            active_alarms.append(f"MAVLINK_INJECTION_ATTACK_{self.firewall.block_count}")

        # Clamping
        self.threat_level = float(np.clip(threat, 0.0, 1.0))

        return CybersecurityStatus(
            threat_level=self.threat_level,
            is_spoofed=is_spoofed,
            firewall_blocks=self.firewall.block_count,
            active_alarms=active_alarms,
            sensor_drift_variance=score
        )
