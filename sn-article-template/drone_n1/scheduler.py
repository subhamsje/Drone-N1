"""
Subsystem 1: Mixed-Criticality Real-Time Task Scheduler (D0-D7 Execution Domains)
Implements Earliest Deadline First (EDF) scheduling under DO-178C DAL-A latency constraints.
"""

import time
import heapq
from typing import List, Dict, Any, Callable

class ExecutionDomain:
    D0_FLIGHT_STABILIZATION = 0  # 8.0 ms budget (DAL-A)
    D1_COLLISION_AVOIDANCE  = 1  # 10.0 ms budget (DAL-A)
    D2_EMERGENCY_SURVIVAL   = 2  # 12.0 ms budget (DAL-B)
    D3_COGNITIVE_REASONING  = 3  # 15.0 ms budget (DAL-B)
    D4_TACTICAL_PERCEPTION  = 4  # 12.0 ms budget (DAL-C)
    D5_FLIGHT_ANALYTICS     = 5  # 200.0 ms budget (DAL-D)
    D6_TELEMETRY_STREAMING  = 6  # 100.0 ms budget (DAL-D)
    D7_BACKGROUND_MINT      = 7  # Best-effort (DAL-E)

DOMAIN_LATENCY_BUDGETS = {
    ExecutionDomain.D0_FLIGHT_STABILIZATION: 8.0,
    ExecutionDomain.D1_COLLISION_AVOIDANCE: 10.0,
    ExecutionDomain.D2_EMERGENCY_SURVIVAL: 12.0,
    ExecutionDomain.D3_COGNITIVE_REASONING: 15.0,
    ExecutionDomain.D4_TACTICAL_PERCEPTION: 12.0,
    ExecutionDomain.D5_FLIGHT_ANALYTICS: 200.0,
    ExecutionDomain.D6_TELEMETRY_STREAMING: 100.0,
    ExecutionDomain.D7_BACKGROUND_MINT: 1000.0
}

class ScheduledTask:
    def __init__(self, task_id: str, domain: int, action: Callable, release_time: float):
        self.task_id = task_id
        self.domain = domain
        self.action = action
        self.release_time = release_time
        self.budget_ms = DOMAIN_LATENCY_BUDGETS.get(domain, 50.0)
        self.absolute_deadline = release_time + (self.budget_ms / 1000.0)

    def __lt__(self, other: 'ScheduledTask'):
        # EDF priority order
        if self.domain != other.domain:
            return self.domain < other.domain
        return self.absolute_deadline < other.absolute_deadline

class MixedCriticalityScheduler:
    def __init__(self):
        self.task_queue: List[ScheduledTask] = []
        self.completed_tasks = 0
        self.deadline_misses = 0

    def add_task(self, task_id: str, domain: int, action: Callable) -> None:
        """Schedules a new task into EDF priority queue."""
        task = ScheduledTask(task_id, domain, action, time.time())
        heapq.heappush(self.task_queue, task)

    def execute_pending_tasks(self) -> Dict[str, Any]:
        """Executes queued tasks in strict EDF domain order."""
        executed = []
        start_t = time.perf_counter()

        while self.task_queue:
            task = heapq.heappop(self.task_queue)
            t_exec_start = time.perf_counter()
            
            try:
                task.action()
            except Exception as e:
                print(f"[SCHEDULER ERROR] Task {task.task_id} failed: {e}")

            duration_ms = (time.perf_counter() - t_exec_start) * 1000.0
            is_overrun = duration_ms > task.budget_ms

            if is_overrun:
                self.deadline_misses += 1
            self.completed_tasks += 1

            executed.append({
                "task_id": task.task_id,
                "domain": task.domain,
                "duration_ms": round(duration_ms, 3),
                "budget_ms": task.budget_ms,
                "overrun": is_overrun
            })

        total_scheduler_time_ms = (time.perf_counter() - start_t) * 1000.0

        return {
            "executed_count": len(executed),
            "deadline_misses": self.deadline_misses,
            "tasks": executed,
            "scheduler_overhead_ms": round(total_scheduler_time_ms, 3)
        }
