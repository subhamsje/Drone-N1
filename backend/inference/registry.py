"""Model registry — versioning, canary, shadow deployment metadata."""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class ModelStage(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    CANARY = "canary"
    PRODUCTION = "production"
    SHADOW = "shadow"
    DEPRECATED = "deprecated"


@dataclass
class ModelArtifact:
    model_id: str
    name: str
    version: str
    stage: ModelStage
    backend: str  # onnx | triton | pytorch | torchscript
    path: Optional[str] = None
    triton_model_name: Optional[str] = None
    input_features: int = 14
    output_heads: List[str] = field(default_factory=list)
    fp16: bool = True
    quantized: bool = False
    edge_deployable: bool = True
    created_at: float = field(default_factory=time.time)
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "version": self.version,
            "stage": self.stage.value,
            "backend": self.backend,
            "path": self.path,
            "triton_model_name": self.triton_model_name,
            "edge_deployable": self.edge_deployable,
            "metrics": self.metrics,
        }


class ModelRegistry:
    """In-memory registry — production syncs from MLflow."""

    def __init__(self):
        self._models: Dict[str, ModelArtifact] = {}
        self._register_defaults()

    def _register_defaults(self):
        heads = [
            "battery_collapse", "motor_degradation", "esc_overheat",
            "vibration_anomaly", "gps_spoof", "comm_failure",
            "crash_probability", "mission_failure", "turbulence", "thermal",
        ]
        for name, version, stage in [
            ("failure_predictor", "1.0.0", ModelStage.PRODUCTION),
            ("anomaly_autoencoder", "1.0.0", ModelStage.PRODUCTION),
            ("battery_lstm", "1.1.0", ModelStage.CANARY),
            ("failure_predictor", "1.2.0", ModelStage.SHADOW),
        ]:
            mid = f"{name}:{version}"
            self._models[mid] = ModelArtifact(
                model_id=mid,
                name=name,
                version=version,
                stage=stage,
                backend="onnx" if "1.0" in version else "pytorch",
                triton_model_name=name.replace("_", "-"),
                output_heads=heads if "failure" in name else ["anomaly_score"],
                path=f"models/{name}_{version}.onnx",
            )

    def get_production(self, name: str) -> Optional[ModelArtifact]:
        candidates = [m for m in self._models.values()
                      if m.name == name and m.stage == ModelStage.PRODUCTION]
        return candidates[0] if candidates else None

    def get_canary(self, name: str) -> Optional[ModelArtifact]:
        candidates = [m for m in self._models.values()
                      if m.name == name and m.stage == ModelStage.CANARY]
        return candidates[0] if candidates else None

    def get_shadow(self, name: str) -> Optional[ModelArtifact]:
        candidates = [m for m in self._models.values()
                      if m.name == name and m.stage == ModelStage.SHADOW]
        return candidates[0] if candidates else None

    def list_models(self) -> List[Dict]:
        return [m.to_dict() for m in self._models.values()]


_registry: Optional[ModelRegistry] = None


def get_model_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
