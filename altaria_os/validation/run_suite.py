#!/usr/bin/env python3
"""Run autonomy validation suite — failure injection benchmarks."""

import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from altaria_os.validation.framework import AutonomyValidationFramework, InjectionType
from backend.pipeline.autonomous_workflow import AutonomousWorkflowEngine


async def main():
    workflow = AutonomousWorkflowEngine()
    base = await workflow.run_single_cycle()
    framework = AutonomyValidationFramework()

    async def process(snap):
        return await workflow.bridge.os_kernel.process(snap)

    scenarios = [
        ("turbulence_stress", InjectionType.TURBULENCE),
        ("gps_spoof", InjectionType.GPS_SPOOF),
        ("mavlink_attack", InjectionType.MAVLINK_ATTACK),
        ("perception_degrade", InjectionType.PERCEPTION_DEGRADE),
        ("actuator_fault", InjectionType.ACTUATOR_DEGRADE),
        ("battery_collapse", InjectionType.BATTERY_COLLAPSE),
        ("rf_interference", InjectionType.RF_INTERFERENCE),
    ]

    print("Altaria Autonomy Validation Suite")
    print("=" * 50)
    for name, inj in scenarios:
        r = await framework.run_scenario(name, inj, process, base_snapshot=base, cycles=15)
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {name}: surv={r.mean_survivability:.3f} recovery={r.recovery_triggered}")

    report = framework.generate_report()
    print("=" * 50)
    print(f"Pass rate: {report['pass_rate']*100:.1f}% ({report['passed']}/{report['total_scenarios']})")
    print(f"Mean survivability: {report['mean_survivability']:.4f}")
    return 0 if report["pass_rate"] >= 0.5 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
