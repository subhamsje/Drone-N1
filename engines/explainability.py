"""Hybrid Explainability Engine — root cause narrative generation."""

import numpy as np
from core.models import (
    TelemetryFrame, PredictionOutput, FusedAnomalyOutput,
    IntegratedRiskOutput, DecisionOutput, EKFState,
    ExplainabilityOutput, FailureSource, DecisionAction
)
from config.settings import SystemConfig


class HybridExplainabilityEngine:
    def __init__(self, config: SystemConfig):
        pass

    def explain(
        self,
        telemetry: TelemetryFrame,
        prediction: PredictionOutput,
        anomaly: FusedAnomalyOutput,
        risk: IntegratedRiskOutput,
        decision: DecisionOutput,
        ekf: EKFState,
        battery_roc: float,
        rpm_roc: float,
    ) -> ExplainabilityOutput:

        action = decision.action
        m = decision.mpc_output

        # Signal contributions (normalized weights)
        total = risk.r_mechanical + risk.r_sensor + risk.r_comms + risk.r_ai + 1e-9
        contributions = {
            "mechanical": risk.r_mechanical / total,
            "sensor":     risk.r_sensor / total,
            "comms":      risk.r_comms / total,
            "ai":         risk.r_ai / total,
        }

        # Dominant signal string
        bat_dev = telemetry.battery - prediction.battery
        rpm_dev = telemetry.rpm - prediction.rpm
        if abs(bat_dev) > abs(rpm_dev / 100):
            pct = bat_dev / max(1.0, abs(prediction.battery)) * 100
            dominant_signal = f"Battery deviation ({pct:+.1f}%)"
        else:
            dominant_signal = f"RPM deviation ({rpm_dev:+.0f} RPM)"

        # AI uncertainty from anomaly
        ai_uncertainty = float(anomaly.uncertainty)

        # Root cause narrative
        if action == DecisionAction.EMERGENCY_LAND:
            root_cause = (
                f"[CRITICAL] Actuator failure {risk.r_mechanical*100:.0f}%! "
                f"Battery: {telemetry.battery:.1f}%. "
                f"EKF confidence {ekf.confidence*100:.0f}% — state estimate degraded. "
                f"MPC commanded emergency descent. "
                f"Dominant: {risk.dominant_source.value}."
            )
        elif action == DecisionAction.RETURN_HOME:
            root_cause = (
                f"[HIGH] Multi-signal degradation detected. "
                f"Battery {bat_dev:+.1f}% vs prediction. "
                f"Mechanical risk {risk.r_mechanical:.3f}. "
                f"EKF covariance {ekf.covariance_trace:.2f}. "
                f"Initiating controlled return. Source: {risk.dominant_source.value}."
            )
        elif action == DecisionAction.THRUST_ADJUST:
            root_cause = (
                f"[{'HIGH' if risk.value > 0.55 else 'MEDIUM'}] "
                f"Motor RPM deviation {rpm_dev:+.0f} RPM. "
                f"Mechanical risk: {risk.r_mechanical*100:.0f}%. "
                f"EKF conf: {ekf.confidence:.3f}. "
                f"MPC commanding thrust rebalance. Source: {risk.dominant_source.value}."
            )
        else:
            root_cause = (
                f"System nominal — all parameters within bounds. "
                f"EKF confidence: {ekf.confidence:.2f}. "
                f"Risk: {risk.value:.4f}. No corrective action required."
            )

        return ExplainabilityOutput(
            root_cause=root_cause,
            dominant_signal=dominant_signal,
            failure_source=risk.dominant_source,
            ekf_confidence=ekf.confidence,
            ekf_covariance_trace=ekf.covariance_trace,
            mpc_iters=m.iterations if m else 0,
            mpc_converged=m.converged if m else False,
            mpc_implied_action=m.implied_action.value if m else "NONE",
            ai_uncertainty=ai_uncertainty,
            r_mechanical=risk.r_mechanical,
            r_sensor=risk.r_sensor,
            r_comms=risk.r_comms,
            r_ai=risk.r_ai,
            signal_contributions=contributions,
        )
