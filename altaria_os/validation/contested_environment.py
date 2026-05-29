"""Contested-environment validation — GPS spoof, RF, poisoning, optical attacks."""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from altaria_os.validation.framework import FailureInjector, InjectionType

logger = logging.getLogger("contested_validation")


@dataclass
class ContestedTestResult:
    scenario: str
    survivability_mean: float
    mission_continuity: float
    deception_handled: bool
    passed: bool


class ContestedEnvironmentValidator:
    SCENARIOS = [
        ("gps_spoof_contested", InjectionType.GPS_SPOOF, 0.95),
        ("rf_warfare", InjectionType.RF_INTERFERENCE, 0.9),
        ("mavlink_contested", InjectionType.MAVLINK_ATTACK, 0.85),
        ("perception_adversarial", InjectionType.PERCEPTION_DEGRADE, 0.88),
        ("comm_collapse", InjectionType.RF_INTERFERENCE, 0.95),
    ]

    def __init__(self):
        self.injector = FailureInjector()
        self._results: List[ContestedTestResult] = []

    async def run_contested_matrix(
        self,
        process_fn: Callable,
        base_snapshot: Dict[str, Any],
        cycles: int = 8,
    ) -> Dict[str, Any]:
        for name, inj, sev in self.SCENARIOS:
            survs, continuity = [], []
            for _ in range(cycles):
                injected = self.injector.inject(base_snapshot, inj, sev)
                if inj == InjectionType.PERCEPTION_DEGRADE:
                    injected.setdefault("environment", {})["adversarial_visual"] = 0.7
                snap = await process_fn(injected) if asyncio.iscoroutinefunction(process_fn) else process_fn(injected)
                survs.append(float(snap.get("probabilistic_safety", {}).get("composite_survivability", 0)))
                cont = float((snap.get("adversarial_operations") or {}).get("hardened_continuity", 0.8))
                continuity.append(cont)
            mean_s = sum(survs) / len(survs)
            mean_c = sum(continuity) / len(continuity)
            deception = mean_c > 0.5
            passed = mean_s > 0.35 and mean_c > 0.45
            self._results.append(ContestedTestResult(name, mean_s, mean_c, deception, passed))

        passed_n = sum(1 for r in self._results if r.passed)
        return {
            "pass_rate": passed_n / len(self._results),
            "mean_survivability": sum(r.survivability_mean for r in self._results) / len(self._results),
            "mean_mission_continuity": sum(r.mission_continuity for r in self._results) / len(self._results),
            "tests": [{"scenario": r.scenario, "passed": r.passed, "surv": round(r.survivability_mean, 4)} for r in self._results],
        }
