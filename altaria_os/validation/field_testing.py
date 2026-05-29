"""Field testing framework — environmental stress, HITL scoring, reliability reports."""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from altaria_os.validation.framework import FailureInjector, InjectionType

logger = logging.getLogger("field_testing")


@dataclass
class FieldTestResult:
    test_name: str
    environment: str
    cycles: int
    recovery_latency_ms: float
    survivability_mean: float
    confidence_mean: float
    passed: bool

    def to_dict(self) -> Dict:
        return self.__dict__


class FieldTestingFramework:
    """HITL-ready environmental stress matrix."""

    ENVIRONMENT_TESTS = [
        ("wind_stress", InjectionType.TURBULENCE, 0.85),
        ("rain_degraded", InjectionType.PERCEPTION_DEGRADE, 0.7),
        ("fog_gps_denied", InjectionType.GPS_SPOOF, 0.75),
        ("rf_attack", InjectionType.RF_INTERFERENCE, 0.8),
        ("gps_spoof_field", InjectionType.GPS_SPOOF, 0.9),
        ("sensor_failure", InjectionType.SENSOR_CORRUPTION, 0.7),
        ("actuator_fault", InjectionType.ACTUATOR_DEGRADE, 0.8),
        ("thermal_stress", InjectionType.BATTERY_COLLAPSE, 0.6),
    ]

    def __init__(self):
        self.injector = FailureInjector()
        self._results: List[FieldTestResult] = []

    async def run_environmental_matrix(
        self,
        process_fn: Callable,
        base_snapshot: Dict,
        cycles_per_test: int = 10,
    ) -> Dict[str, Any]:
        for name, inj, sev in self.ENVIRONMENT_TESTS:
            latencies = []
            survs = []
            confs = []
            recovery_triggered = False
            t0 = time.monotonic()

            for _ in range(cycles_per_test):
                injected = self.injector.inject(base_snapshot, inj, sev)
                if asyncio.iscoroutinefunction(process_fn):
                    snap = await process_fn(injected)
                else:
                    snap = process_fn(injected)
                survs.append(float(snap.get("probabilistic_safety", {}).get("composite_survivability", 0)))
                confs.append(1.0 - float(snap.get("confidence", {}).get("global_uncertainty", 0.5)))
                if snap.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"):
                    recovery_triggered = True
                    latencies.append((time.monotonic() - t0) * 1000)

            mean_surv = sum(survs) / len(survs) if survs else 0
            mean_conf = sum(confs) / len(confs) if confs else 0
            rec_lat = sum(latencies) / len(latencies) if latencies else 0

            passed = mean_surv > 0.35 and (recovery_triggered or mean_surv > 0.55)
            self._results.append(FieldTestResult(
                name, inj.value, cycles_per_test, rec_lat, mean_surv, mean_conf, passed
            ))

        passed_n = sum(1 for r in self._results if r.passed)
        return {
            "total": len(self._results),
            "passed": passed_n,
            "pass_rate": passed_n / max(1, len(self._results)),
            "mean_survivability": sum(r.survivability_mean for r in self._results) / max(1, len(self._results)),
            "tests": [r.to_dict() for r in self._results],
        }

    def generate_reliability_report(self) -> Dict[str, Any]:
        return {
            "field_tests": len(self._results),
            "reliability_score": sum(1 for r in self._results if r.passed) / max(1, len(self._results)),
            "confidence_analytics": {
                "mean": sum(r.confidence_mean for r in self._results) / max(1, len(self._results)),
            },
            "recovery_latency_ms": {
                "mean": sum(r.recovery_latency_ms for r in self._results if r.recovery_latency_ms) / max(1, len([r for r in self._results if r.recovery_latency_ms])),
            },
            "details": [r.to_dict() for r in self._results],
        }
