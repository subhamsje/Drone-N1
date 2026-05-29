#!/usr/bin/env python3
"""Environmental field testing matrix."""
import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from altaria_os.validation.field_testing import FieldTestingFramework
from backend.pipeline.autonomous_workflow import AutonomousWorkflowEngine


async def main():
    w = AutonomousWorkflowEngine()
    base = await w.run_single_cycle()
    ft = FieldTestingFramework()

    async def process(snap):
        return await w.bridge.os_kernel.process(snap)

    report = await ft.run_environmental_matrix(process, base, cycles_per_test=8)
    reliability = ft.generate_reliability_report()
    print("Field Testing Matrix")
    print("=" * 50)
    print(f"Pass rate: {report['pass_rate']*100:.0f}%")
    print(f"Mean survivability: {report['mean_survivability']:.4f}")
    print(f"Reliability score: {reliability['reliability_score']*100:.0f}%")
    for t in report["tests"]:
        print(f"  [{'PASS' if t['passed'] else 'FAIL'}] {t['test_name']}: surv={t['survivability_mean']:.3f}")
    return 0 if report["pass_rate"] >= 0.6 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
