"""Operational readiness scoring — SITL/HITL/field deployment benchmarks."""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from altaria_os.validation.field_testing import FieldTestingFramework
from altaria_os.validation.framework import AutonomyValidationFramework

logger = logging.getLogger("operational_readiness")


@dataclass
class ReadinessScore:
    survivability_benchmark: float
    reliability_score: float
    confidence_degradation_tolerance: float
    recovery_latency_p50_ms: float
    operational_readiness: float  # 0-1 composite
    certification_ready: bool
    deployment_tier: str  # lab | sitl | hitl | field

    def to_dict(self) -> Dict:
        return {k: round(v, 4) if isinstance(v, float) else v for k, v in self.__dict__.items()}


class OperationalReadinessValidator:
    """World-class autonomy validation — combines fault injection + environmental matrix."""

    def __init__(self):
        self.field = FieldTestingFramework()
        self.fault = AutonomyValidationFramework()

    async def run_full_assessment(
        self,
        process_fn: Callable,
        base_snapshot: Dict[str, Any],
        deployment_tier: str = "sitl",
    ) -> Dict[str, Any]:
        field_report = await self.field.run_environmental_matrix(
            process_fn, base_snapshot, cycles_per_test=6
        )
        fault_report = await self.fault.run_all_scenarios(process_fn, base_snapshot)

        surv_field = field_report.get("mean_survivability", 0)
        surv_fault = fault_report.get("mean_survivability", 0)
        surv_bench = (surv_field + surv_fault) / 2

        rel = field_report.get("pass_rate", 0) * 0.5 + fault_report.get("pass_rate", 0) * 0.5
        conf_tol = 1.0 - abs(surv_field - surv_fault)

        readiness = min(1.0, surv_bench * 0.5 + rel * 0.35 + conf_tol * 0.15)
        cert_ready = readiness > 0.65 and rel >= 0.85

        score = ReadinessScore(
            survivability_benchmark=surv_bench,
            reliability_score=rel,
            confidence_degradation_tolerance=conf_tol,
            recovery_latency_p50_ms=0.0,
            operational_readiness=readiness,
            certification_ready=cert_ready,
            deployment_tier=deployment_tier,
        )

        return {
            "readiness": score.to_dict(),
            "field_tests": field_report,
            "fault_injection": fault_report,
            "report_id": f"readiness-{int(time.time())}",
        }
