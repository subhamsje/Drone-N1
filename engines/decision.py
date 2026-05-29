"""
MPC Decision Engine + TTF Estimator
"""

import math
import time
import logging
import numpy as np
from collections import deque
from typing import List, Tuple

from core.models import (
    IntegratedRiskOutput, FusedAnomalyOutput, EKFState,
    TTFOutput, DecisionOutput, MPCOutput, DecisionAction, RiskLevel
)
from engines.physics import UnifiedDynamics
from config.settings import SystemConfig

logger = logging.getLogger("decision")


class TTFEstimator:
    def __init__(self, config: SystemConfig):
        self.cfg           = config.ttf
        self._prev_ttf     = config.ttf.base_ttf_minutes
        self._min_ttf_seen = config.ttf.base_ttf_minutes

    def estimate(self, risk: IntegratedRiskOutput, battery: float, risk_gradient: float) -> TTFOutput:
        base             = self.cfg.base_ttf_minutes
        risk_factor      = max(0.0, 1.0 - risk.value) ** self.cfg.gradient_sensitivity
        batt_factor      = max(0.1, battery / 100.0)
        gradient_penalty = max(0.0, 1.0 - 5.0 * max(0.0, risk_gradient))

        raw_ttf = base * risk_factor * batt_factor * gradient_penalty
        raw_ttf = max(self.cfg.min_ttf, raw_ttf)

        if risk_gradient < -0.02:
            ttf = min(raw_ttf * 1.1, self._prev_ttf * 1.15)
        else:
            ttf = min(raw_ttf, self._prev_ttf * 1.05)

        self._min_ttf_seen = min(self._min_ttf_seen, ttf)
        if ttf > self._min_ttf_seen * 1.5:
            ttf = self._min_ttf_seen * 1.3

        self._prev_ttf = ttf
        confidence     = min(1.0, 0.5 + 0.5 * risk.value)
        return TTFOutput(minutes=ttf, confidence=confidence)


class AdaptiveBudgetMPC:
    def __init__(self, config: SystemConfig):
        cfg      = config.mpc
        self.cfg = cfg
        self.N   = cfg.horizon
        self.U   = np.full((self.N, 4), config.physics.hover_thrust)
        self._hover = config.physics.hover_thrust

    def optimize(
        self,
        x_init: np.ndarray,
        target_z: float,
        dt: float,
        dynamics: 'UnifiedDynamics',
        fault_losses: np.ndarray,
        fault_taus: np.ndarray,
        risk_value: float,
    ) -> MPCOutput:
        cfg = self.cfg

        if risk_value < 0.30:
            time_budget = cfg.budget_low_ms / 1000.0
            max_iters   = cfg.max_iters_low
        else:
            time_budget = cfg.budget_high_ms / 1000.0
            max_iters   = cfg.max_iters_high

        t0        = time.perf_counter()
        iters     = 0
        converged = False
        cost      = float('inf')

        while iters < max_iters and (time.perf_counter() - t0) < time_budget:
            iters += 1

            X = np.zeros((self.N + 1, 20))
            X[0] = x_init
            for k in range(self.N):
                X[k+1] = dynamics.step(X[k], self.U[k], dt, fault_losses, fault_taus)

            cost = self._compute_cost(X, target_z)

            Lambda   = np.zeros(20)
            grad_U   = np.zeros((self.N, 4))
            for k in range(self.N - 1, -1, -1):
                x_k = X[k+1]
                dL_dx          = np.zeros(20)
                dL_dx[2]       = 2 * cfg.altitude_cost  * (x_k[2] - target_z)
                dL_dx[10:12]   = 2 * cfg.attitude_cost  * x_k[10:12]
                dL_dx[12]      = 2 * cfg.yaw_cost        * x_k[12]
                dL_dx[7:9]     = 2 * cfg.quaternion_cost * x_k[7:9]
                dL_du          = 2 * cfg.control_cost    * (self.U[k] - self._hover)
                if k > 0:
                    dL_du += 2 * cfg.delta_control_cost * (self.U[k] - self.U[k-1])

                F_x, F_u = dynamics.symbolic_jacobian(X[k], dt, fault_losses, fault_taus)
                Lambda    = dL_dx + F_x.T @ Lambda
                grad_U[k] = dL_du + F_u.T @ Lambda

            grad_norm = float(np.linalg.norm(grad_U))
            if grad_norm < cfg.grad_norm_tol:
                converged = True
                break

            alpha      = 0.5
            cost_old   = cost
            dir_deriv  = -float(np.sum(grad_U ** 2))
            step_ok    = False
            for _ in range(cfg.line_search_steps):
                U_new = np.clip(self.U - alpha * grad_U, 0.0, 15.0)
                X_new = np.zeros((self.N + 1, 20))
                X_new[0] = x_init
                for k in range(self.N):
                    X_new[k+1] = dynamics.step(X_new[k], U_new[k], dt, fault_losses, fault_taus)
                cost_new = self._compute_cost(X_new, target_z)
                if cost_new <= cost_old + cfg.armijo_c * alpha * dir_deriv:
                    self.U = U_new
                    step_ok = True
                    break
                alpha *= 0.5
            if not step_ok:
                break

        u_opt  = self.U[0].copy()
        self.U = np.roll(self.U, -1, axis=0)
        self.U[-1] = self.U[-2]

        t_used  = (time.perf_counter() - t0) * 1000.0
        implied = self._infer_action(x_init, u_opt, risk_value)

        return MPCOutput(
            u_optimal      = [float(v) for v in u_opt],
            converged      = converged,
            iterations     = iters,
            time_budget_ms = time_budget * 1000.0,
            time_used_ms   = t_used,
            cost           = float(cost),
            implied_action = implied,
        )

    def _compute_cost(self, X: np.ndarray, target_z: float) -> float:
        cfg  = self.cfg
        cost = 0.0
        for k in range(self.N):
            x_k = X[k+1]
            cost += cfg.altitude_cost        * (x_k[2] - target_z) ** 2
            cost += cfg.attitude_cost        * np.sum(x_k[10:12] ** 2)
            cost += cfg.yaw_cost             * x_k[12] ** 2
            cost += cfg.quaternion_cost      * np.sum(x_k[7:9] ** 2)
            cost += cfg.control_cost         * np.sum((self.U[k] - self._hover) ** 2)
            if k > 0:
                cost += cfg.delta_control_cost * np.sum((self.U[k] - self.U[k-1]) ** 2)
        return cost

    def _infer_action(self, x: np.ndarray, u_opt: np.ndarray, risk: float) -> DecisionAction:
        avg_thr  = float(np.mean(u_opt))
        thr_diff = float(np.max(u_opt) - np.min(u_opt))

        if risk > 0.80:
            return DecisionAction.EMERGENCY_LAND
        if risk > 0.40:
            return DecisionAction.RETURN_HOME
        if thr_diff > 2.0 or avg_thr < 4.0:
            return DecisionAction.THRUST_ADJUST
        return DecisionAction.NONE


class DecisionIntelligenceLayer:
    def __init__(self, config: SystemConfig):
        self.cfg = config.decision
        self._action_history: deque = deque(maxlen=8)
        self._last_action    = DecisionAction.NONE

    def decide(
        self,
        risk: IntegratedRiskOutput,
        ttf: TTFOutput,
        anomaly: FusedAnomalyOutput,
        battery: float,
        risk_gradient: float,
        mpc_output: MPCOutput,
        ekf_confidence: float = 1.0,
        cyber_threat: float = 0.0,
    ) -> DecisionOutput:
        r = risk.value
        t = max(0.0, 1.0 - ttf.minutes / 8.0)    # urgency
        a = anomaly.score
        b = max(0.0, 1.0 - battery / 100.0)
        g = min(1.0, max(0.0, risk_gradient * 20.0))

        mpc_emergency  = float(mpc_output.implied_action == DecisionAction.EMERGENCY_LAND)
        mpc_return     = float(mpc_output.implied_action == DecisionAction.RETURN_HOME)
        mpc_converged  = float(mpc_output.converged)
        mpc_cost_norm  = min(1.0, mpc_output.cost / 10000.0)

        # ── dynamic flight aggression mode selection ─────────────────────
        unc_val = (1.0 - ekf_confidence) * 0.35 + (1.0 - ttf.confidence) * 0.25 + anomaly.uncertainty * 0.20 + cyber_threat * 0.40
        if unc_val > 0.70 or risk.level == RiskLevel.CRITICAL or cyber_threat > 0.60:
            agg_mode = "SURVIVAL"
        elif unc_val > 0.45 or risk.level == RiskLevel.HIGH or cyber_threat > 0.30:
            agg_mode = "DEFENSIVE"
        elif unc_val > 0.20 or risk.level == RiskLevel.MEDIUM:
            agg_mode = "CONSERVATIVE"
        else:
            agg_mode = "NOMINAL"

        # ── raw factor scores (all in [0,1] range) ────────────────────────
        critical_boost = 1.5 if risk.level == RiskLevel.CRITICAL else 1.0
        high_boost     = 1.2 if risk.level in (RiskLevel.HIGH, RiskLevel.CRITICAL) else 1.0

        emergency_score = (
            0.35 * r + 0.25 * t + 0.15 * a + 0.10 * b + 0.05 * g + 0.10 * mpc_emergency
        ) * critical_boost

        return_score = (
            0.30 * r + 0.20 * (1-t) + 0.20 * a + 0.10 * b + 0.05 * g + 0.15 * mpc_return
        ) * high_boost

        thrust_score = (
            0.25 * r + 0.30 * g + 0.20 * a + 0.15 * (1-t) + 0.05 * b + 0.05 * mpc_cost_norm
        )

        # none_score decays as risk grows — at risk=0.5 it's ≈0.5 which can lose to others
        none_score = max(0.0, (1.0 - r) * (1.0 - 0.5*a) * (1.0 - 0.3*g)) * (
            1.05 if mpc_converged and mpc_output.cost < 1000.0 else 1.0
        )

        # In defensive/survival modes, aggressively prioritize return-to-home or emergency landing
        if agg_mode == "SURVIVAL":
            emergency_score *= 1.35
            none_score *= 0.1
        elif agg_mode == "DEFENSIVE":
            return_score *= 1.20
            none_score *= 0.4

        scores = {
            DecisionAction.EMERGENCY_LAND: emergency_score,
            DecisionAction.RETURN_HOME:    return_score,
            DecisionAction.THRUST_ADJUST:  thrust_score,
            DecisionAction.NONE:           none_score,
        }

        # Softmax
        exp_scores = {k: math.exp(min(5.0, v * 5.0)) for k, v in scores.items()}
        total      = sum(exp_scores.values()) + 1e-9
        probs      = {k: v / total for k, v in exp_scores.items()}

        best_action    = max(probs, key=probs.get)
        raw_confidence = probs[best_action]

        # Threshold gate: reject weak signals for expensive actions
        thresholds = {
            DecisionAction.EMERGENCY_LAND: self.cfg.emergency_land_score,
            DecisionAction.RETURN_HOME:    self.cfg.return_home_score,
            DecisionAction.THRUST_ADJUST:  self.cfg.thrust_adjust_score,
        }
        if best_action in thresholds and scores[best_action] < thresholds[best_action]:
            # Downgrade
            ordered = [DecisionAction.RETURN_HOME, DecisionAction.THRUST_ADJUST, DecisionAction.NONE]
            for candidate in ordered:
                if candidate == best_action:
                    continue
                cand_thresh = thresholds.get(candidate, 0.0)
                if scores[candidate] >= cand_thresh:
                    best_action    = candidate
                    raw_confidence = probs[candidate]
                    break
            else:
                best_action    = DecisionAction.NONE
                raw_confidence = probs[DecisionAction.NONE]

        # Hysteresis
        if (list(self._action_history).count(best_action) == 0
                and self._last_action != DecisionAction.NONE):
            raw_confidence *= self.cfg.confidence_decay

        if mpc_converged and best_action == mpc_output.implied_action:
            raw_confidence = min(1.0, raw_confidence * 1.10)

        self._action_history.append(best_action)
        self._last_action = best_action

        return DecisionOutput(
            action          = best_action,
            confidence      = min(1.0, raw_confidence),
            score_breakdown = {k.value: round(float(v), 4) for k, v in scores.items()},
            mpc_output      = mpc_output,
            aggression_mode = agg_mode,
        )
