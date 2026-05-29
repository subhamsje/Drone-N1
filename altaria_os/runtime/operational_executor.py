"""Real-time operational execution — survival-priority critical path orchestration."""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from altaria_os.runtime.scheduler import RealTimeScheduler, TaskPriority

logger = logging.getLogger("rt.operational")


class OperationalExecutionOrchestrator:
    """
    Hard real-time cognitive cycle partitioning.
    Critical path (perception trust → world model → survival → envelope → execute)
    always completes before lakehouse/analytics.
    """

    CRITICAL_BUDGET_MS = 45.0
    ANALYTICS_MAX_PRIORITY = int(TaskPriority.FLEET_SYNC)

    def __init__(self, scheduler: RealTimeScheduler):
        self.scheduler = scheduler
        self._last_critical_ms = 0.0
        self._cycles = 0
        self._deadline_misses = 0

    async def run_critical_path(
        self,
        steps: List[tuple],
    ) -> Dict[str, Any]:
        """
        steps: [(task_id, priority, async_fn), ...]
        Executes in priority order within CRITICAL_BUDGET_MS.
        """
        t0 = time.monotonic()
        results = {}
        for task_id, priority, fn in sorted(steps, key=lambda x: x[1]):
            if (time.monotonic() - t0) * 1000 > self.CRITICAL_BUDGET_MS:
                self._deadline_misses += 1
                logger.warning("RT critical budget exceeded at %s", task_id)
                break
            step_t0 = time.monotonic()
            results[task_id] = await fn()
            self.scheduler.schedule(
                priority,
                task_id,
                lambda: asyncio.sleep(0),
                deadline_ms=20.0,
            )

        elapsed = (time.monotonic() - t0) * 1000
        self._last_critical_ms = elapsed
        self._cycles += 1
        met = elapsed <= self.CRITICAL_BUDGET_MS

        return {
            "critical_path_ms": round(elapsed, 2),
            "critical_path_met": met,
            "steps_completed": list(results.keys()),
            "deadline_misses_total": self._deadline_misses,
            "emergency_preempt_ready": self.scheduler._queue and self.scheduler._queue[0].priority <= int(TaskPriority.EMERGENCY_RECOVERY),
        }

    def defer_analytics(self, coro_factory: Callable, task_id: str = "analytics"):
        """Schedule analytics/logging only after critical band."""
        self.scheduler.schedule(TaskPriority.ANALYTICS, task_id, coro_factory, deadline_ms=500.0)

    def get_execution_status(self) -> Dict[str, Any]:
        return {
            "last_critical_path_ms": self._last_critical_ms,
            "cycles": self._cycles,
            "deadline_misses": self._deadline_misses,
            "scheduler": self.scheduler.get_stats(),
        }
