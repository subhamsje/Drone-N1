"""Survivability benchmarking — production-grade operational metrics."""

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import numpy as np

logger = logging.getLogger("survivability_benchmark")


@dataclass
class SurvivabilityBenchmark:
    composite_survivability_p50: float
    composite_survivability_p99: float
    recovery_trigger_rate: float
    recovery_latency_p50_ms: float
    confidence_degradation_rate: float
    world_model_accuracy_proxy: float
    certification_pass_rate: float
    production_grade_score: float

    def to_dict(self) -> Dict:
        return {k: round(v, 4) if isinstance(v, float) else v for k, v in self.__dict__.items()}


class SurvivabilityBenchmarkEngine:
    """Aggregates cycle metrics into deployment benchmarks."""

    def __init__(self):
        self._surv_samples: List[float] = []
        self._conf_samples: List[float] = []
        self._recovery_latencies: List[float] = []
        self._recovery_triggers = 0
        self._cycles = 0
        self._cert_pass = 0

    async def run_benchmark(
        self,
        process_fn: Callable,
        base_snapshot: Dict[str, Any],
        cycles: int = 30,
    ) -> Dict[str, Any]:
        import asyncio
        for _ in range(cycles):
            t0 = time.monotonic()
            if asyncio.iscoroutinefunction(process_fn):
                snap = await process_fn(base_snapshot)
            else:
                snap = process_fn(base_snapshot)
            if not isinstance(snap, dict):
                continue

            surv = float(snap.get("probabilistic_safety", {}).get("composite_survivability", 0))
            self._surv_samples.append(surv)
            self._conf_samples.append(1.0 - float(snap.get("confidence", {}).get("global_uncertainty", 0.5)))

            if snap.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"):
                self._recovery_triggers += 1
                self._recovery_latencies.append((time.monotonic() - t0) * 1000)

            fc = snap.get("formal_certification", {}).get("formal_verification", {})
            if fc.get("all_invariants_satisfied"):
                self._cert_pass += 1
            self._cycles += 1

        if not self._surv_samples:
            return {"error": "no_samples"}

        sorted_surv = sorted(self._surv_samples)
        bench = SurvivabilityBenchmark(
            composite_survivability_p50=float(np.median(sorted_surv)),
            composite_survivability_p99=sorted_surv[int(len(sorted_surv) * 0.99)],
            recovery_trigger_rate=self._recovery_triggers / max(1, self._cycles),
            recovery_latency_p50_ms=float(np.median(self._recovery_latencies)) if self._recovery_latencies else 0,
            confidence_degradation_rate=sum(1 for c in self._conf_samples if c < 0.5) / max(1, len(self._conf_samples)),
            world_model_accuracy_proxy=float(np.mean([
                float(s) for s in self._surv_samples
            ])),
            certification_pass_rate=self._cert_pass / max(1, self._cycles),
            production_grade_score=min(1.0, float(np.median(sorted_surv)) * 0.6 + (self._cert_pass / max(1, self._cycles)) * 0.4),
        )
        return {"benchmark": bench.to_dict(), "cycles": self._cycles}
