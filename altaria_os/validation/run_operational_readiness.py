#!/usr/bin/env python3
"""Full operational readiness assessment — fault + environmental + readiness score."""
import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT))

from altaria_os.validation.operational_readiness import OperationalReadinessValidator
from backend.pipeline.autonomous_workflow import AutonomousWorkflowEngine


async def main():
    w = AutonomousWorkflowEngine()
    base = await w.run_single_cycle()
    assert base.get("os_version") == "8.0.0", f"Expected v8, got {base.get('os_version')}"

    validator = OperationalReadinessValidator()

    async def process(snap):
        return await w.bridge.os_kernel.process(snap)

    report = await validator.run_full_assessment(process, base, deployment_tier="sitl")
    r = report["readiness"]
    print("Altaria Operational Readiness Assessment")
    print("=" * 50)
    print(f"OS Version: {base['os_version']}")
    print(f"Survivability benchmark: {r['survivability_benchmark']:.4f}")
    print(f"Reliability score: {r['reliability_score']*100:.0f}%")
    print(f"Operational readiness: {r['operational_readiness']*100:.0f}%")
    print(f"Certification ready: {r['certification_ready']}")
    print(f"Deployment tier: {r['deployment_tier']}")
    return 0 if r["operational_readiness"] >= 0.6 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
