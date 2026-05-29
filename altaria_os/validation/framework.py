"""
Autonomy Validation Framework — failure injection, survivability benchmarks.
"""

import asyncio
import logging
import time
import copy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum

import numpy as np

logger = logging.getLogger("validation")


class InjectionType(str, Enum):
    TURBULENCE = "turbulence"
    GPS_SPOOF = "gps_spoof"
    MAVLINK_ATTACK = "mavlink_attack"
    PERCEPTION_DEGRADE = "perception_degrade"
    SENSOR_CORRUPTION = "sensor_corruption"
    ACTUATOR_DEGRADE = "actuator_degrade"
    RF_INTERFERENCE = "rf_interference"
    BATTERY_COLLAPSE = "battery_collapse"


@dataclass
class ValidationResult:
    scenario: str
    injection: str
    cycles: int
    recovery_triggered: bool
    survival_maintained: bool
    landing_success_prob: float
    mean_survivability: float
    autonomy_confidence_collapse: bool
    passed: bool
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario,
            "injection": self.injection,
            "cycles": self.cycles,
            "recovery_triggered": self.recovery_triggered,
            "survival_maintained": self.survival_maintained,
            "landing_success_prob": round(self.landing_success_prob, 4),
            "mean_survivability": round(self.mean_survivability, 4),
            "passed": self.passed,
            "metrics": {k: round(v, 4) for k, v in self.metrics.items()},
        }


class FailureInjector:
    """Applies controlled faults to snapshot dicts for validation."""

    def inject(self, snapshot: Dict[str, Any], itype: InjectionType, severity: float = 0.8) -> Dict[str, Any]:
        s = copy.deepcopy(snapshot)
        sev = float(np.clip(severity, 0, 1))

        if itype == InjectionType.TURBULENCE:
            nav = s.setdefault("navigation", {})
            nav["weather_hazard"] = sev
            s.setdefault("twin_physics", {})["turbulence_index"] = sev

        elif itype == InjectionType.GPS_SPOOF:
            s.setdefault("cybersecurity", {})["is_spoofed"] = True
            s.setdefault("cybersecurity", {})["threat_level"] = sev
            s.setdefault("sensor_trust", {})["gps_confidence"] = 0.05

        elif itype == InjectionType.MAVLINK_ATTACK:
            s.setdefault("cybersecurity", {})["firewall_blocks"] = int(10 * sev)
            s.setdefault("cybersecurity", {})["threat_level"] = sev

        elif itype == InjectionType.PERCEPTION_DEGRADE:
            s.setdefault("perception", {})["obstacle_density"] = sev
            s.setdefault("vision", {})["slam_confidence"] = 1.0 - sev

        elif itype == InjectionType.SENSOR_CORRUPTION:
            s.setdefault("ekf", {})["confidence"] = 1.0 - sev * 0.7
            s.setdefault("ekf", {})["innovation_mag"] = 5.0 * sev
            imu = s.setdefault("physics", {}).setdefault("imu", [0, 0, 9.81])
            imu[0] = float(np.random.normal(0, 3 * sev))

        elif itype == InjectionType.ACTUATOR_DEGRADE:
            thrusts = s.setdefault("physics", {}).setdefault("motor_thrusts", [5.42] * 4)
            thrusts[0] = thrusts[0] * (1.0 - sev * 0.6)
            s.setdefault("physics", {})["rpm"] = 4000 * (1.0 - sev * 0.3)

        elif itype == InjectionType.RF_INTERFERENCE:
            s.setdefault("cybersecurity", {})["threat_level"] = sev * 0.9
            s.setdefault("sensor_trust", {})["fusion_confidence"] = 1.0 - sev * 0.5

        elif itype == InjectionType.BATTERY_COLLAPSE:
            s.setdefault("physics", {})["battery"] = max(5, 100 * (1.0 - sev))

        s["risk"] = s.get("risk", {})
        s["risk"]["value"] = min(1.0, float(s["risk"].get("value", 0.3)) + sev * 0.4)
        s["risk"]["level"] = "CRITICAL" if s["risk"]["value"] > 0.75 else "HIGH" if s["risk"]["value"] > 0.5 else "MEDIUM"
        return s


class AutonomyValidationFramework:
    """Runs injection scenarios and produces statistical safety reports."""

    def __init__(self):
        self.injector = FailureInjector()
        self._results: List[ValidationResult] = []

    async def run_scenario(
        self,
        name: str,
        injection: InjectionType,
        process_fn: Callable,
        base_snapshot: Optional[Dict] = None,
        cycles: int = 25,
        severity: float = 0.8,
    ) -> ValidationResult:
        survivabilities = []
        landing_probs = []
        recovery_count = 0
        confidences = []

        if base_snapshot is None:
            if asyncio.iscoroutinefunction(process_fn):
                base_snapshot = await process_fn()
            else:
                base_snapshot = process_fn()

        for _ in range(cycles):
            injected = self.injector.inject(base_snapshot, injection, severity)
            if asyncio.iscoroutinefunction(process_fn):
                snap = await process_fn(injected)
            else:
                snap = process_fn(injected)

            prob = snap.get("probabilistic_safety", {})
            survivabilities.append(float(prob.get("composite_survivability", 0)))
            landing_probs.append(float(prob.get("landing_success_probability", 0)))
            confidences.append(1.0 - float(snap.get("confidence", {}).get("global_uncertainty", 0.5)))

            if snap.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"):
                recovery_count += 1
            if snap.get("decision", {}).get("os_override"):
                recovery_count += 1

        mean_surv = float(np.mean(survivabilities)) if survivabilities else 0
        mean_land = float(np.mean(landing_probs)) if landing_probs else 0
        collapse = float(np.mean(confidences)) < 0.35 if confidences else False

        passed = mean_surv > 0.4 and (recovery_count > 0 or mean_land > 0.5)

        result = ValidationResult(
            scenario=name,
            injection=injection.value,
            cycles=cycles,
            recovery_triggered=recovery_count > 0,
            survival_maintained=mean_surv > 0.35,
            landing_success_prob=mean_land,
            mean_survivability=mean_surv,
            autonomy_confidence_collapse=collapse,
            passed=passed,
            metrics={
                "recovery_rate": recovery_count / max(1, cycles),
                "mean_confidence": float(np.mean(confidences)) if confidences else 0,
            },
        )
        self._results.append(result)
        return result

    async def run_all_scenarios(
        self,
        process_fn: Callable,
        base_snapshot: Dict[str, Any],
        cycles: int = 12,
    ) -> Dict[str, Any]:
        scenarios = [
            ("turbulence_stress", InjectionType.TURBULENCE),
            ("gps_spoof", InjectionType.GPS_SPOOF),
            ("mavlink_attack", InjectionType.MAVLINK_ATTACK),
            ("perception_degrade", InjectionType.PERCEPTION_DEGRADE),
            ("actuator_fault", InjectionType.ACTUATOR_DEGRADE),
            ("battery_collapse", InjectionType.BATTERY_COLLAPSE),
            ("rf_interference", InjectionType.RF_INTERFERENCE),
        ]
        for name, inj in scenarios:
            await self.run_scenario(name, inj, process_fn, base_snapshot=base_snapshot, cycles=cycles)
        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        if not self._results:
            return {"status": "no_results"}
        passed = sum(1 for r in self._results if r.passed)
        return {
            "total_scenarios": len(self._results),
            "passed": passed,
            "pass_rate": passed / len(self._results),
            "mean_survivability": float(np.mean([r.mean_survivability for r in self._results])),
            "mean_landing_prob": float(np.mean([r.landing_success_prob for r in self._results])),
            "scenarios": [r.to_dict() for r in self._results],
        }
