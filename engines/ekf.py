"""
Rollback-Augmented EKF — 20D Bias-Augmented State Estimator
─────────────────────────────────────────────────────────────
Adapted from Code 3 with full config integration and clean API.

Key capabilities:
  - Full 20D state estimation (pos, vel, attitude, actuators, gyro bias)
  - Out-of-sequence measurement handling via history rollback
  - Mahalanobis-gated updates (rejects sensor glitches)
  - Confidence score derived from covariance trace

All downstream modules consume EKFState — NOT raw sensor data.
This is the "truth source" for the entire intelligence pipeline.
"""

import logging
import numpy as np
from collections import deque
from typing import Optional, Tuple

from core.models import EKFState
from engines.physics import UnifiedDynamics
from config.settings import SystemConfig

logger = logging.getLogger("ekf")


class RollbackAugmentedEKF:
    """
    Extended Kalman Filter with:
      1. predict_forward()  — propagates state with symbolic Jacobian
      2. delayed_update()   — handles out-of-sequence measurements via
                              rollback to insertion point, then replay forward

    State x (20D):
      [pos(3), vel(3), quat(4), ang_vel(3), u_act(4), gyro_bias(3)]

    Measurement z (10D):
      [pos(3), quat(4), omega_biased(3)]
      H maps: pos→x[0:3], quat→x[6:10], omega_biased→x[10:13]+x[17:20]
    """

    MEAS_DIM = 10   # observation vector size

    def __init__(self, config: SystemConfig):
        cfg     = config.ekf
        phys    = config.physics
        self.dt = cfg.dt

        # Initialize state from physics config
        self.x = np.zeros(20)
        self.x[2]     = phys.initial_altitude
        self.x[6]     = 1.0                  # quaternion identity
        self.x[13:17] = phys.hover_thrust

        # Covariance
        self.P = np.eye(20) * 0.1

        # Process noise Q
        self.Q = np.eye(20) * cfg.process_noise_base
        self.Q[17:20, 17:20] = np.eye(3) * cfg.bias_process_noise

        # Measurement noise R
        self.R = np.eye(self.MEAS_DIM) * cfg.measurement_noise

        # Rollback buffer: stores (t, x, P, u) tuples
        self._history: deque = deque(maxlen=cfg.rollback_buffer_depth)

        # Observables
        self.innovation_mag  = 0.0
        self.confidence      = 1.0
        self.covariance_trace = 0.0

        # Mahalanobis threshold
        self._mahal_thresh = cfg.mahal_reject_threshold

        # Dynamics reference (for Jacobian)
        self._dynamics = UnifiedDynamics(config)

        logger.info(f"[EKF] Initialized 20D state | dt={self.dt}s | rollback={cfg.rollback_buffer_depth} steps")

    # ── Public API ────────────────────────────────────────────────────────────

    def predict_forward(
        self,
        t_now: float,
        u_cmd: np.ndarray,
        fault_losses: np.ndarray,
        fault_taus: np.ndarray,
    ):
        """
        EKF predict step:
          x̂ = f(x̂, u)
          P  = F·P·Fᵀ + Q
        
        Stores (t, x, P, u) in rollback buffer.
        """
        F_x, _ = self._dynamics.symbolic_jacobian(self.x, self.dt, fault_losses, fault_taus)
        self.x = self._dynamics.step(self.x, u_cmd, self.dt, fault_losses, fault_taus)
        self.P = F_x @ self.P @ F_x.T + self.Q

        # Normalize quaternion (numerical drift guard)
        q_norm = np.linalg.norm(self.x[6:10])
        if q_norm > 1e-6:
            self.x[6:10] /= q_norm

        # Store checkpoint
        self._history.append((t_now, self.x.copy(), self.P.copy(), u_cmd.copy()))
        self._update_observables()

    def delayed_update(
        self,
        t_z: float,
        z: np.ndarray,
        fault_losses: np.ndarray,
        fault_taus: np.ndarray,
    ):
        """
        Out-of-Sequence Measurement (OOSM) update via rollback:
          1. Find history entry closest to t_z
          2. Apply EKF update there
          3. Replay all subsequent predictions forward
        
        This correctly handles comm delays without state inconsistency.
        """
        if len(self._history) == 0:
            return

        # Find rollback insertion point
        idx = min(
            range(len(self._history)),
            key=lambda i: abs(self._history[i][0] - t_z)
        )
        t_h, x_h, P_h, u_h = self._history[idx]

        # Measurement Jacobian H [10×20]
        H = self._build_H()

        # Innovation
        y = z - (H @ x_h)

        # Mahalanobis gate (chi-squared test)
        S = H @ P_h @ H.T + self.R
        try:
            S_inv = np.linalg.pinv(S)
            mahal_sq = float(y @ S_inv @ y)
        except np.linalg.LinAlgError:
            logger.warning("[EKF] Singular S matrix — skipping update")
            return

        if mahal_sq > self._mahal_thresh:
            logger.debug(f"[EKF] Mahalanobis reject: {mahal_sq:.1f} > {self._mahal_thresh}")
            return

        self.innovation_mag = float(np.mean(np.abs(y)))

        # Joseph-form update (numerically stable)
        K    = P_h @ H.T @ S_inv
        x_u  = x_h + K @ y
        I_KH = np.eye(20) - K @ H
        P_u  = I_KH @ P_h @ I_KH.T + K @ self.R @ K.T

        # Normalize updated quaternion
        q_norm = np.linalg.norm(x_u[6:10])
        if q_norm > 1e-6:
            x_u[6:10] /= q_norm

        # Write back to history at insertion point
        self._history[idx] = (t_h, x_u, P_u, u_h)

        # Replay forward from insertion point
        hist_list = list(self._history)
        for i in range(idx, len(hist_list) - 1):
            t_k, x_k, P_k, u_k = hist_list[i]
            F_k, _ = self._dynamics.symbolic_jacobian(x_k, self.dt, fault_losses, fault_taus)
            x_next = self._dynamics.step(x_k, u_k, self.dt, fault_losses, fault_taus)
            P_next = F_k @ P_k @ F_k.T + self.Q
            hist_list[i + 1] = (hist_list[i + 1][0], x_next, P_next, hist_list[i + 1][3])

        # Rebuild deque from updated list
        self._history = deque(hist_list, maxlen=self._history.maxlen)

        # Adopt latest replayed state
        self.x = self._history[-1][1].copy()
        self.P = self._history[-1][2].copy()
        self._update_observables()

        logger.debug(
            f"[EKF] OOSM update | mahal={mahal_sq:.1f} | inno={self.innovation_mag:.4f} | "
            f"conf={self.confidence:.4f}"
        )

    def get_state(self) -> EKFState:
        return EKFState(
            x               = self.x.copy(),
            P               = self.P.copy(),
            confidence      = self.confidence,
            innovation_mag  = self.innovation_mag,
            covariance_trace= self.covariance_trace,
        )

    # ── Internal ──────────────────────────────────────────────────────────────

    def _build_H(self) -> np.ndarray:
        """
        H [10×20] measurement model:
          pos[0:3]      → x[0:3]
          quat[3:7]     → x[6:10]
          omega_b[7:10] → x[10:13] + x[17:20]  (biased gyro)
        """
        H = np.zeros((10, 20))
        H[0:3, 0:3]   = np.eye(3)       # position
        H[3:7, 6:10]  = np.eye(4)       # quaternion
        H[7:10, 10:13] = np.eye(3)      # angular velocity
        H[7:10, 17:20] = np.eye(3)      # + gyro bias
        return H

    def _update_observables(self):
        """Recompute confidence and covariance trace from current P."""
        trace              = float(np.trace(self.P))
        self.covariance_trace = trace
        self.confidence    = float(np.clip(1.0 / (1.0 + trace / 10.0), 0.0, 1.0))
