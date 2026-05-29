"""Inference gateway — orchestrates streaming inference, edge/cloud routing, Triton."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from backend.inference.registry import get_model_registry
from backend.inference.predictors import FailurePredictor
from backend.events.bus import get_event_bus
from backend.events.schemas import DomainEvent, EventType
from backend.events.topics import Topic
from core.cognitive_models import FailurePrediction

logger = logging.getLogger("inference.gateway")


class InferenceGateway:
    """
    Low-latency inference orchestration.
    Routes to: local ONNX → Triton (cloud) → heuristic fallback.
    Supports canary/shadow comparison.
    """

    def __init__(self, uav_id: str, edge_mode: bool = True):
        self.uav_id = uav_id
        self.edge_mode = edge_mode
        self._registry = get_model_registry()
        self._failure_predictor = FailurePredictor()
        self._bus = get_event_bus()
        self._triton_url = None  # http://triton:8000
        self._stats = {"requests": 0, "latency_ms": [], "shadow_diff": []}

    async def infer_failure(
        self,
        feature_vector: List[float],
        snapshot: Dict[str, Any],
        sensor_trust: Optional[Dict] = None,
    ) -> FailurePrediction:
        self._stats["requests"] += 1

        await self._bus.publish(
            DomainEvent.create(
                EventType.INFERENCE_REQUEST,
                self.uav_id,
                {"model": "failure_predictor", "features": len(feature_vector)},
            ),
            Topic.ML_INFERENCE_REQUEST,
        )

        if self._triton_url and not self.edge_mode:
            result = await self._triton_infer(feature_vector, snapshot)
        else:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._failure_predictor.predict,
                feature_vector,
                snapshot,
                sensor_trust,
            )

        # Canary comparison
        canary = self._registry.get_canary("failure_predictor")
        if canary:
            canary_result = self._failure_predictor._heuristic_infer(snapshot, sensor_trust)
            diff = abs(canary_result["crash_probability"] - result.crash_probability)
            self._stats["shadow_diff"].append(diff)

        self._stats["latency_ms"].append(result.inference_latency_ms)

        await self._bus.publish(
            DomainEvent.create(
                EventType.INFERENCE_RESULT,
                self.uav_id,
                result.to_dict(),
            ),
            Topic.ML_INFERENCE_RESULT,
        )
        return result

    async def _triton_infer(self, fv: List[float], snapshot: Dict) -> FailurePrediction:
        """Triton HTTP/gRPC client stub — production implements full protocol."""
        logger.debug("Triton routing stub — falling back to local")
        return self._failure_predictor.predict(fv, snapshot)

    def set_triton_endpoint(self, url: str):
        self._triton_url = url

    @property
    def stats(self) -> Dict[str, Any]:
        lat = self._stats["latency_ms"]
        return {
            "requests": self._stats["requests"],
            "avg_latency_ms": sum(lat) / len(lat) if lat else 0,
            "p99_latency_ms": sorted(lat)[int(len(lat) * 0.99)] if len(lat) > 10 else 0,
            "models": self._registry.list_models(),
        }
