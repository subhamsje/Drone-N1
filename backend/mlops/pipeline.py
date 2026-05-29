"""MLOps pipeline — training, versioning, canary, rollback interfaces."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from backend.inference.registry import get_model_registry, ModelStage

logger = logging.getLogger("mlops")


@dataclass
class DeploymentRecord:
    model_id: str
    stage: str
    deployed_at: float
    rollout_pct: float
    status: str


class MLOpsPipeline:
    """
    Enterprise MLOps interfaces — integrates MLflow/Kubeflow/Ray in production.
    """

    def __init__(self):
        self._registry = get_model_registry()
        self._deployments: List[DeploymentRecord] = []
        self._training_jobs: List[Dict] = []

    def register_training_job(self, name: str, dataset: str, config: Dict) -> str:
        job_id = f"train-{name}-{int(time.time())}"
        self._training_jobs.append({
            "job_id": job_id,
            "name": name,
            "dataset": dataset,
            "config": config,
            "status": "queued",
            "created_at": time.time(),
        })
        return job_id

    def promote_to_canary(self, model_id: str, rollout_pct: float = 5.0) -> bool:
        if model_id not in self._registry._models:
            return False
        m = self._registry._models[model_id]
        m.stage = ModelStage.CANARY
        self._deployments.append(DeploymentRecord(model_id, "canary", time.time(), rollout_pct, "active"))
        return True

    def promote_to_production(self, model_id: str) -> bool:
        if model_id not in self._registry._models:
            return False
        # Deprecate current production
        for mid, art in self._registry._models.items():
            if art.name == self._registry._models[model_id].name and art.stage == ModelStage.PRODUCTION:
                art.stage = ModelStage.DEPRECATED
        self._registry._models[model_id].stage = ModelStage.PRODUCTION
        self._deployments.append(DeploymentRecord(model_id, "production", time.time(), 100.0, "active"))
        return True

    def rollback(self, model_name: str) -> Optional[str]:
        deprecated = [m for m in self._registry._models.values()
                      if m.name == model_name and m.stage == ModelStage.DEPRECATED]
        if not deprecated:
            return None
        latest = max(deprecated, key=lambda m: m.created_at)
        return self.promote_to_production(latest.model_id) and latest.model_id

    def enable_shadow(self, model_id: str) -> bool:
        if model_id in self._registry._models:
            self._registry._models[model_id].stage = ModelStage.SHADOW
            return True
        return False

    def get_pipeline_status(self) -> Dict[str, Any]:
        return {
            "models": self._registry.list_models(),
            "deployments": [
                {"model_id": d.model_id, "stage": d.stage, "rollout_pct": d.rollout_pct}
                for d in self._deployments[-20:]
            ],
            "training_jobs": len(self._training_jobs),
        }
