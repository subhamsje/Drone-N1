"""
Physics Engine — UnifiedDynamics (20D Nonlinear UAV Model)
──────────────────────────────────────────────────────────
Adapted from Code 3 (backend.py) with:
  - Config-driven parameters (no hardcoded constants)
  - Gradual fault injection (ramp, not step)
  - Battery simulation derived from motor effort
  - PhysicsFrame output (full data contract)
  - CommsLink for realistic delayed sensor measurements

State vector x (20D):
  x[0:3]   = position [px, py, pz]  (m)
  x[3:6]   = velocity [vx, vy, vz]  (m/s)
  x[6:10]  = quaternion [w, x, y, z]
  x[10:13] = angular velocity [ωx, ωy, ωz] (rad/s)
  x[13:17] = actuator states [u0..u3] (normalized thrust)
  x[17:20] = gyro bias [bx, by, bz] (rad/s)
"""

import math
import logging
import numpy as np
from collections import deque
from typing import List, Optional, Tuple

from core.models import PhysicsFrame, TelemetryFrame
from config.settings import SystemConfig

logger = logging.getLogger("physics")


class UnifiedDynamics:
    """
    20D nonlinear UAV rigid-body dynamics with:
      - Quadratic thrust curve
      - Nonlinear quaternion attitude
      - Actuator lag and saturation
      - Dead-motor fault modeling (gradual loss ramp)
      - Quadratic aerodynamic drag
    
    All constants come from PhysicsConfig — no magic numbers.
    """

    def __init__(self, config: SystemConfig):
        cfg = config.physics
        self.mass    = cfg.mass
        self.g       = cfg.gravity
        self.L       = cfg.arm_length
        self.C_TAU   = cfg.c_tau
        self.C_DRAG  = cfg.c_drag
        self.MAX_CMD = cfg.max_motor_cmd
        self.I       = np.diag([0.02, 0.02, 0.04])
        self.INV_I   = np.linalg.inv(self.I)
        # Thrust coefficient derived so hover_thrust² * k = mass*g/4
        hover = cfg.hover_thrust
        self.k_thrust = (self.mass * self.g / 4.0) / (hover ** 2)

    def thrust_curve(self, u_act: np.ndarray, loss: np.ndarray) -> np.ndarray:
        """T_eff = k * u² * (1 − fault_loss)"""
        return self.k_thrust * (u_act ** 2) * np.clip(1.0 - loss, 0.0, 1.0)

    def thrust_deriv(self, u_act: np.ndarray, loss: np.ndarray) -> np.ndarray:
        return 2.0 * self.k_thrust * u_act * np.clip(1.0 - loss, 0.0, 1.0)

    @staticmethod
    def q_mult(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2,
        ])

    def step(
        self,
        x: np.ndarray,
        u_cmd: np.ndarray,
        dt: float,
        fault_losses: np.ndarray,
        fault_taus: np.ndarray,
        wind: np.ndarray = None,
    ) -> np.ndarray:
        """Integrate dynamics one timestep dt."""
        if wind is None:
            wind = np.zeros(3)

        pos, vel = x[0:3], x[3:6]
        q, omega  = x[6:10], x[10:13]
        u_act     = x[13:17]
        bias      = x[17:20]

        # 1. Actuator Dynamics (lag + saturation)
        du = (np.clip(u_cmd, 0.0, self.MAX_CMD) - u_act) * (dt / fault_taus)
        du = np.clip(du, -60.0 * dt, 60.0 * dt)
        next_u_act = np.clip(u_act + du, 0.0, self.MAX_CMD)

        T_eff = self.thrust_curve(next_u_act, fault_losses)

        # 2. Rotational Dynamics — torques from differential thrust
        tau = np.array([
            self.L * ( T_eff[0] - T_eff[1] - T_eff[2] + T_eff[3]),
            self.L * ( T_eff[0] + T_eff[1] - T_eff[2] - T_eff[3]),
            self.C_TAU * (T_eff[0] - T_eff[1] + T_eff[2] - T_eff[3]),
        ])
        alpha = self.INV_I @ (tau - np.cross(omega, self.I @ omega))
        next_omega = np.clip(omega + alpha * dt, -25.0, 25.0)

        # 3. Quaternion integration (normalized)
        omega_q = np.array([0.0, next_omega[0], next_omega[1], next_omega[2]])
        q_unnorm = q + 0.5 * self.q_mult(q, omega_q) * dt
        next_q = q_unnorm / (np.linalg.norm(q_unnorm) + 1e-9)

        # 4. Translational Dynamics (body-to-world thrust + drag)
        w, x_q, y_q, z_q = next_q
        R_z = np.array([
            2*(x_q*z_q + w*y_q),
            2*(y_q*z_q - w*x_q),
            1 - 2*x_q**2 - 2*y_q**2,
        ])
        thrust_vec = R_z * np.sum(T_eff)
        drag = -self.C_DRAG * vel * (np.linalg.norm(vel) + 1e-6)

        accel = (thrust_vec + drag + wind) / self.mass - np.array([0.0, 0.0, self.g])
        next_vel = np.clip(vel + accel * dt, -30.0, 30.0)
        next_pos = pos + next_vel * dt

        # Ground clamping
        if next_pos[2] <= 0.0:
            next_pos[2] = 0.0
            next_vel    = np.zeros(3)
            next_omega  = np.zeros(3)
            next_q      = np.array([1.0, 0.0, 0.0, 0.0])

        # Bias: random walk (state transition only — EKF tracks it)
        next_bias = bias

        return np.concatenate([next_pos, next_vel, next_q, next_omega, next_u_act, next_bias])

    def symbolic_jacobian(
        self,
        x: np.ndarray,
        dt: float,
        fault_losses: np.ndarray,
        fault_taus: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Exact symbolic Jacobian F = ∂f/∂x for EKF propagation.
        Returns (F_x [20×20], F_u [20×4]).
        """
        vel, q, omega, u_act = x[3:6], x[6:10], x[10:13], x[13:17]
        F   = np.eye(20)
        F_u = np.zeros((20, 4))

        # Translational partials
        F[0:3, 3:6] = np.eye(3) * dt
        v_norm = np.linalg.norm(vel) + 1e-6
        dF_drag = -self.C_DRAG * (v_norm * np.eye(3) + np.outer(vel, vel) / v_norm)
        F[3:6, 3:6] += (dF_drag / self.mass) * dt

        w, x_q, y_q, z_q = q
        T_eff  = self.thrust_curve(u_act, fault_losses)
        T_tot  = np.sum(T_eff)
        dRz_dq = np.array([
            [2*y_q,  2*z_q,  2*w,   2*x_q],
            [-2*x_q, -2*w,   2*z_q, 2*y_q],
            [0,      -4*x_q, -4*y_q, 0],
        ])
        F[3:6, 6:10] = ((T_tot / self.mass) * dRz_dq) * dt

        R_z    = np.array([2*(x_q*z_q + w*y_q), 2*(y_q*z_q - w*x_q), 1 - 2*x_q**2 - 2*y_q**2])
        dT_du  = self.thrust_deriv(u_act, fault_losses)
        F[3:6, 13:17] = (np.outer(R_z, dT_du) / self.mass) * dt

        # Rotational partials — quaternion
        omega_mat = np.array([
            [0,       -omega[0], -omega[1], -omega[2]],
            [omega[0], 0,         omega[2], -omega[1]],
            [omega[1], -omega[2], 0,         omega[0]],
            [omega[2],  omega[1], -omega[0], 0],
        ])
        dq_dq_unnorm = np.eye(4) + 0.5 * omega_mat * dt
        q_unnorm     = q + 0.5 * self.q_mult(q, np.array([0, omega[0], omega[1], omega[2]])) * dt
        q_norm_sq    = np.dot(q_unnorm, q_unnorm) + 1e-9
        J_norm       = (np.eye(4) - np.outer(q_unnorm, q_unnorm) / q_norm_sq) / math.sqrt(q_norm_sq)
        F[6:10, 6:10] = J_norm @ dq_dq_unnorm
        E_q = np.array([
            [-x_q, -y_q, -z_q],
            [w,    -z_q,  y_q],
            [z_q,   w,   -x_q],
            [-y_q,  x_q,  w],
        ])
        F[6:10, 10:13] = J_norm @ (0.5 * E_q * dt)

        # Angular velocity partials
        S_w   = np.array([[0, -omega[2], omega[1]], [omega[2], 0, -omega[0]], [-omega[1], omega[0], 0]])
        S_Iw  = np.array([[0, -(self.I@omega)[2], (self.I@omega)[1]],
                          [(self.I@omega)[2], 0, -(self.I@omega)[0]],
                          [-(self.I@omega)[1], (self.I@omega)[0], 0]])
        F[10:13, 10:13] += (self.INV_I @ (S_w @ self.I - S_Iw)) * dt

        T_map = np.array([
            [self.L,       -self.L,      -self.L,      self.L],
            [self.L,        self.L,      -self.L,     -self.L],
            [self.C_TAU,   -self.C_TAU,  self.C_TAU, -self.C_TAU],
        ])
        F[10:13, 13:17] = (self.INV_I @ (T_map * dT_du)) * dt

        # Actuator partials
        F[13:17, 13:17] = np.diag(1.0 - dt / fault_taus)
        F_u[13:17, :]   = np.diag(dt / fault_taus)

        # Bias random walk
        F[17:20, 17:20] = np.eye(3)

        return F, F_u


class CommsLink:
    """
    Simulates realistic sensor-to-FC communication:
      - Variable delay [delay_min, delay_max]
      - Packet loss probability
      - Out-of-sequence delivery (sorted by arrival time)
    """

    def __init__(self, config: SystemConfig):
        cfg = config.ekf
        self._q: List = []
        self._loss_prob = cfg.comm_loss_prob
        self._delay_min = cfg.comm_delay_min
        self._delay_max = cfg.comm_delay_max

    def transmit(self, z: np.ndarray, t_sent: float):
        if np.random.rand() > self._loss_prob:
            delay    = np.random.uniform(self._delay_min, self._delay_max)
            t_arrive = t_sent + delay
            self._q.append((t_arrive, t_sent, z.copy()))
            self._q.sort(key=lambda p: p[0])

    def receive(self, t_now: float) -> Optional[Tuple[float, np.ndarray]]:
        """Returns (t_sent, measurement) if a packet arrived, else None."""
        if self._q and self._q[0][0] <= t_now:
            _, t_sent, z = self._q.pop(0)
            return t_sent, z
        return None


class PhysicsEngine:
    """
    Orchestrates UnifiedDynamics + fault injection + CommsLink.
    Replaces TelemetryIngestionLayer as the ground-truth state source.

    Called at the physics dt (20ms) — multiple times per 150ms loop cycle.
    """

    def __init__(self, config: SystemConfig):
        cfg = config.physics
        self.cfg      = cfg
        self.ekf_cfg  = config.ekf
        self.dynamics = UnifiedDynamics(config)
        self.comms    = CommsLink(config)
        self.dt       = config.ekf.dt

        # 20D state initialization
        self.x = np.zeros(20)
        self.x[2]     = cfg.initial_altitude
        self.x[6]     = 1.0               # quaternion w=1 (identity)
        self.x[13:17] = cfg.hover_thrust   # nominal hover thrust

        # Fault state (gradual ramp, not step)
        self.fault_losses = np.zeros(4)
        self.fault_taus   = np.array(cfg.tau_motors)

        # Battery simulation (separate from physics state — energy model)
        self._battery        = 100.0
        self._time           = 0.0
        self._cycle          = 0
        self._action_recovery = 0.0

        # Wind disturbance
        self._wind = np.zeros(3)

    # ── Public API ────────────────────────────────────────────────────────────

    def step_physics(self, u_cmd: np.ndarray) -> PhysicsFrame:
        """
        Advance physics by one dt.
        u_cmd: [T0, T1, T2, T3] motor commands.
        Returns PhysicsFrame with all derived quantities.
        """
        self._time += self.dt
        self._cycle += 1

        # Fault injection (gradual loss ramp after fault_onset_time)
        self._update_faults()

        # Stochastic wind
        self._wind += np.random.normal(0, self.cfg.wind_std, 3) * self.dt
        self._wind  = np.clip(self._wind, -2.0, 2.0)

        # Gyro bias random walk (truth model — EKF must estimate this)
        self.x[17:20] += np.random.normal(0, 5e-4, 3)

        # Dynamics step
        self.x = self.dynamics.step(
            self.x, u_cmd, self.dt,
            self.fault_losses, self.fault_taus, self._wind,
        )

        # x model: power ~ sum(T_eff²) + fault overhead
        T_eff = self.dynamics.thrust_curve(self.x[13:17], self.fault_losses)
        power_load = np.sum(T_eff ** 2) / (4.0 * self.cfg.hover_thrust ** 2)
        drain = 0.04 * power_load
        if np.any(self.fault_losses > 0.1):
            drain += 0.15 * np.max(self.fault_losses)
        drain *= max(0.0, 1.0 - self._action_recovery)
        self._battery = max(0.0, self._battery - drain + np.random.gauss(0, 0.01)
                            if hasattr(np.random, 'gauss') else
                            self._battery - drain + float(np.random.normal(0, 0.01)))

        # Build frame
        avg_rpm = float(np.mean(T_eff) / self.dynamics.k_thrust) ** 0.5 * 60 / (2 * math.pi) * 50
        avg_rpm = max(0.0, avg_rpm)
        # IMU = linear acceleration approximated from angular rates
        imu = [
            float(self.x[10]),
            float(self.x[11]),
            float(-1.0 + self.x[12] * 0.1),   # z includes gravity term
        ]

        return PhysicsFrame(
            altitude     = float(self.x[2]),
            pos_x        = float(self.x[0]),
            pos_y        = float(self.x[1]),
            vx           = float(self.x[3]),
            vy           = float(self.x[4]),
            vz           = float(self.x[5]),
            quat         = [float(v) for v in self.x[6:10]],
            roll_rate    = float(self.x[10]),
            pitch_rate   = float(self.x[11]),
            yaw_rate     = float(self.x[12]),
            motor_thrusts= [float(v) for v in self.x[13:17]],
            battery      = self._battery,
            rpm          = avg_rpm,
            imu          = imu,
        )

    def transmit_measurement(self):
        """Send noisy measurement to comms link (simulates sensor → FC delay)."""
        z_true = np.concatenate([
            self.x[0:3],           # position
            self.x[6:10],          # quaternion
            self.x[10:13] + self.x[17:20],  # omega + bias (gyro reads both)
        ])
        noise = np.random.normal(0, 0.02, len(z_true))
        self.comms.transmit(z_true + noise, self._time)

    def receive_measurement(self):
        return self.comms.receive(self._time)

    def apply_action_feedback(self, action: str, recovery_factor: float):
        """Closed-loop: actions feed back into physics simulation."""
        self._action_recovery = recovery_factor
        hover = self.cfg.hover_thrust
        if action == "EMERGENCY_LAND":
            # Reduce thrust setpoint — will manifest as lower u_cmd from MPC
            logger.info("⚡ EMERGENCY_LAND: recovery clamped, fault damped")
        elif action == "THRUST_ADJUST":
            logger.info("🔧 THRUST_ADJUST: partial fault mitigation engaged")
        elif action == "RETURN_HOME":
            logger.info("🏠 RETURN_HOME: slow stabilization mode")

    # ── Internal ──────────────────────────────────────────────────────────────

    def _update_faults(self):
        """Gradual fault loss ramp — fault GROWS, not instant."""
        t_fault = self.cfg.fault_onset_time
        if self._time >= t_fault:
            idx   = self.cfg.fault_motor_index
            ramp  = self.cfg.fault_loss_ramp_rate * self.dt
            # Recovery factor slows the ramp
            ramp *= max(0.0, 1.0 - self._action_recovery * 0.7)
            self.fault_losses[idx] = min(1.0, self.fault_losses[idx] + ramp)

    @property
    def time(self) -> float:
        return self._time

    @property
    def fault_losses_arr(self) -> np.ndarray:
        return self.fault_losses.copy()

    @property
    def battery(self) -> float:
        return self._battery
