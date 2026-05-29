"""
Hard Real-Time Scheduler — survival and safety always preempt analytics/logging.
"""

import asyncio
import heapq
import logging
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger("rt.scheduler")


class TaskPriority(IntEnum):
    EMERGENCY_RECOVERY = 0
    COLLISION_AVOIDANCE = 1
    SURVIVAL_INFERENCE = 2
    SAFETY_VETO = 3
    COGNITIVE_CYCLE = 4
    PERCEPTION = 5
    TELEMETRY_INGEST = 6
    FLEET_SYNC = 7
    LAKEHOUSE_PERSIST = 8
    ANALYTICS = 9
    LOGGING = 10


@dataclass(order=True)
class ScheduledTask:
    priority: int
    deadline_ms: float
    task_id: str = field(compare=False)
    coro_factory: Callable = field(compare=False)
    created_at: float = field(default_factory=time.monotonic, compare=False)


class RealTimeScheduler:
    """
    Priority queue scheduler with deadline awareness.
    EMERGENCY_RECOVERY always runs before LOGGING.
    """

    def __init__(self, max_queue: int = 1000):
        self._queue: List[ScheduledTask] = []
        self._running = False
        self._stats: Dict[str, int] = {}
        self._latencies: Dict[str, List[float]] = {}

    def schedule(
        self,
        priority: TaskPriority,
        task_id: str,
        coro_factory: Callable[[], Awaitable],
        deadline_ms: float = 50.0,
    ):
        heapq.heappush(self._queue, ScheduledTask(
            priority=int(priority),
            deadline_ms=deadline_ms,
            task_id=task_id,
            coro_factory=coro_factory,
        ))

    async def run_next(self) -> Optional[Dict[str, Any]]:
        if not self._queue:
            return None
        task = heapq.heappop(self._queue)
        t0 = time.monotonic()
        try:
            await task.coro_factory()
            ok = True
            err = None
        except Exception as e:
            ok = False
            err = str(e)
            logger.error("RT task %s failed: %s", task.task_id, e)
        elapsed = (time.monotonic() - t0) * 1000
        self._stats[task.task_id] = self._stats.get(task.task_id, 0) + 1
        self._latencies.setdefault(task.task_id, []).append(elapsed)
        return {
            "task_id": task.task_id,
            "priority": task.priority,
            "latency_ms": elapsed,
            "deadline_ms": task.deadline_ms,
            "met_deadline": elapsed <= task.deadline_ms,
            "ok": ok,
            "error": err,
        }

    async def drain_priority(self, max_priority: int, budget_ms: float = 100.0):
        """Run all tasks up to max_priority within time budget."""
        t0 = time.monotonic()
        results = []
        while self._queue and (time.monotonic() - t0) * 1000 < budget_ms:
            if self._queue[0].priority > max_priority:
                break
            r = await self.run_next()
            if r:
                results.append(r)
        return results

    def get_stats(self) -> Dict[str, Any]:
        p99 = {}
        for tid, lats in self._latencies.items():
            if lats:
                p99[tid] = sorted(lats)[int(len(lats) * 0.99)]
        return {"queued": len(self._queue), "executed": self._stats, "p99_ms": p99}
