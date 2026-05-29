#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from altaria_os.validation.survivability_benchmark import SurvivabilityBenchmarkEngine
from backend.pipeline.autonomous_workflow import AutonomousWorkflowEngine


async def main():
    w = AutonomousWorkflowEngine()
    base = await w.run_single_cycle()
    assert base.get("os_version") == "7.0.0", base.get("os_version")

    async def process(snap):
        return await w.bridge.os_kernel.process(snap)

    report = await SurvivabilityBenchmarkEngine().run_benchmark(process, base, cycles=25)
    b = report["benchmark"]
    print("Survivability Production Benchmark")
    print("=" * 50)
    print(f"OS: 6.0.0 | Cycles: {report['cycles']}")
    print(f"P50 survivability: {b['composite_survivability_p50']:.4f}")
    print(f"P99 survivability: {b['composite_survivability_p99']:.4f}")
    print(f"Cert pass rate: {b['certification_pass_rate']*100:.0f}%")
    print(f"Production grade: {b['production_grade_score']*100:.0f}%")
    return 0 if b["production_grade_score"] >= 0.6 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
