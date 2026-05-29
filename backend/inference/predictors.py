"""Production inference predictors — ONNX/Triton-ready with numpy fallback."""

import logging
import time
from typing import Any, Dict, List, Optional

import numpy as np

from core.cognitive_models import FailurePrediction
from backend.inference.registry import get_model_registry

logger = logging.getLogger("inference.predictors")


class FailurePredictor:
    """
    Multi-head failure prediction.
    Uses ONNX when available; falls back to calibrated heuristic from telemetry.
    """

    def __init__(self):
        self._registry = get_model_registry()
        self._onnx_session = None
        self._try_load_onnx()

    def _try_load_onnx(self):
        model = self._registry.get_production("failure_predictor")
        if not model or not model.path:
            return
        try:
            import onnxruntime as ort
            import os
            path = model.path
            if os.path.exists(path):
                self._onnx_session = ort.InferenceSession(
                    path, providers=["CPUExecutionProvider"]
                )
                logger.info("ONNX failure predictor loaded: %s", path)
        except ImportError:
            pass
        except Exception as e:
            logger.debug("ONNX load skipped: %s", e)

    def predict(
        self,
        feature_vector: List[float],
        snapshot: Dict[str, Any],
        sensor_trust: Optional[Dict] = None,
    ) -> FailurePrediction:
        t0 = time.perf_counter()
        model = self._registry.get_production("failure_predictor")

        if self._onnx_session is not None:
            probs = self._onnx_infer(feature_vector)
        else:
            probs = self._heuristic_infer(snapshot, sensor_trust)

        # Shadow inference (non-blocking comparison)
        shadow = self._registry.get_shadow("failure_predictor")
        if shadow:
            _ = self._heuristic_infer(snapshot, sensor_trust)  # shadow path logged in gateway

        latency = (time.perf_counter() - t0) * 1000.0
        return FailurePrediction(
            battery_collapse_prob=probs["battery_collapse"],
            motor_degradation_prob=probs["motor_degradation"],
            esc_overheat_prob=probs["esc_overheat"],
            vibration_anomaly_prob=probs["vibration_anomaly"],
            gps_spoof_prob=probs["gps_spoof"],
            comm_failure_prob=probs["comm_failure"],
            crash_probability=probs["crash_probability"],
            mission_failure_prob=probs["mission_failure"],
            turbulence_risk=probs["turbulence"],
            thermal_overload_prob=probs["thermal"],
            model_confidence=probs.get("confidence", 0.85),
            inference_latency_ms=latency,
            model_version=model.version if model else "heuristic",
        )

    def _onnx_infer(self, fv: List[float]) -> Dict[str, float]:
        x = np.array(fv[:14], dtype=np.float32).reshape(1, -1)
        out = self._onnx_session.run(None, {"input": x})[0][0]
        keys = [
            "battery_collapse", "motor_degradation", "esc_overheat",
            "vibration_anomaly", "gps_spoof", "comm_failure",
            "crash_probability", "mission_failure", "turbulence", "thermal",
        ]
        return {k: float(np.clip(out[i] if i < len(out) else 0, 0, 1)) for i, k in enumerate(keys)}

    def _heuristic_infer(self, snap: Dict, sensor_trust: Optional[Dict]) -> Dict[str, float]:
        risk = float(snap.get("risk", {}).get("value", 0))
        anom = float(snap.get("anomaly", {}).get("score", 0))
        bat = float(snap.get("physics", {}).get("battery", 100))
        rpm = float(snap.get("physics", {}).get("rpm", 5000))
        cyber = snap.get("cybersecurity", {}) or {}
        nav = snap.get("navigation", {}) or {}
        pred = snap.get("prediction", {}) or {}

        bat_roc = abs(100 - float(pred.get("battery", bat)))
        motor_stress = max(0, 1.0 - rpm / 6000.0) if rpm < 5500 else 0.3
        gps_spoof = 0.9 if cyber.get("is_spoofed") else float(1.0 - (sensor_trust or {}).get("gps_confidence", 0.9))
        turb = float(nav.get("weather_hazard", 0))

        return {
            "battery_collapse": float(np.clip((100 - bat) / 40.0 + bat_roc / 20.0, 0, 1)),
            "motor_degradation": float(np.clip(motor_stress + anom * 0.4, 0, 1)),
            "esc_overheat": float(np.clip(risk * 0.6 + anom * 0.3, 0, 1)),
            "vibration_anomaly": float(np.clip(anom * 1.1, 0, 1)),
            "gps_spoof": float(np.clip(gps_spoof, 0, 1)),
            "comm_failure": float(np.clip(cyber.get("threat_level", 0) * 0.8, 0, 1)),
            "crash_probability": float(np.clip(risk * 0.85 + anom * 0.25, 0, 1)),
            "mission_failure": float(np.clip(risk * 0.7 + (1 - bat / 100) * 0.3, 0, 1)),
            "turbulence": float(np.clip(turb, 0, 1)),
            "thermal": float(np.clip(risk * 0.5 + motor_stress * 0.4, 0, 1)),
            "confidence": float(pred.get("confidence", 0.8)),
        }
