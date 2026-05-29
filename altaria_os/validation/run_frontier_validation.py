#!/usr/bin/env python3
"""Altaria v7 frontier validation — readiness + contested + survivability + SITL readiness."""
import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from altaria_os.validation.operational_readiness import OperationalReadinessValidator
from altaria_os.validation.contested_environment import ContestedEnvironmentValidator
from altaria_os.validation.survivability_benchmark import SurvivabilityBenchmarkEngine
from altaria_os.validation.sitl_bridge import PX4SITLBridge
from backend.pipeline.autonomous_workflow import AutonomousWorkflowEngine


async def main():
    w = AutonomousWorkflowEngine()
    base = await w.run_single_cycle()
    ver = base.get("os_version", "?")
    print(f"Altaria Frontier Validation (OS {ver})")
    print("=" * 55)
    if ver != "8.0.0":
        print(f"WARN: expected 8.0.0, got {ver}")

    sitl = PX4SITLBridge()
    print(f"SITL: {sitl.get_readiness()}")

    async def process(snap):
        return await w.bridge.os_kernel.process(snap)

    readiness = await OperationalReadinessValidator().run_full_assessment(process, base, "sitl")
    contested = await ContestedEnvironmentValidator().run_contested_matrix(process, base, cycles=6)
    bench = await SurvivabilityBenchmarkEngine().run_benchmark(process, base, cycles=20)

    r = readiness["readiness"]
    print(f"Operational readiness: {r['operational_readiness']*100:.0f}% | cert_ready={r['certification_ready']}")
    print(f"Contested pass rate: {contested['pass_rate']*100:.0f}% | continuity={contested['mean_mission_continuity']:.3f}")
    print(f"Production grade: {bench['benchmark']['production_grade_score']*100:.0f}%")
    ok = r["operational_readiness"] >= 0.6 and contested["pass_rate"] >= 0.6
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
