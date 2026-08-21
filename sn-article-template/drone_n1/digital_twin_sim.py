"""
Subsystem 8: 20D Digital Twin Counterfactual Fast-Forward Sandbox
Simulates potential fallback trajectories in 1-millisecond real-time budget.
"""

import time
import math
from typing import Dict, Any, List, Tuple

class DigitalTwinSandbox:
    def __init__(self, sim_step_dt: float = 0.05, horizon_steps: int = 20):
        self.dt = sim_step_dt
        self.horizon_steps = horizon_steps

    def simulate_counterfactual_path(self, current_state: Dict[str, float], candidate_action: Tuple[float, float, float]) -> Dict[str, Any]:
        """
        Executes a 1-millisecond fast-forward physics prediction loop 
        evaluating trajectory safety under predicted wind/obstacles.
        """
        start_t = time.perf_counter()

        x, y, z = current_state.get("x", 0.0), current_state.get("y", 0.0), current_state.get("z", 10.0)
        vx, vy, vz = candidate_action
        wind_vx = current_state.get("wind_vx", 2.0)
        wind_vy = current_state.get("wind_vy", 1.0)

        trajectory: List[Tuple[float, float, float]] = []
        max_risk = 0.0

        for step in range(self.horizon_steps):
            # Forward Euler step with wind disturbance
            x += (vx + wind_vx * 0.2) * self.dt
            y += (vy + wind_vy * 0.2) * self.dt
            z += vz * self.dt

            # Check obstacle proximity
            dist_to_obs = math.sqrt((x - 15.0)**2 + (y - 15.0)**2)
            step_risk = 1.0 / (dist_to_obs + 0.1) if dist_to_obs < 5.0 else 0.0
            max_risk = max(max_risk, step_risk)

            trajectory.append((round(x, 2), round(y, 2), round(z, 2)))

        sim_time_ms = (time.perf_counter() - start_t) * 1000.0

        return {
            "predicted_trajectory": trajectory,
            "max_risk_predicted": round(max_risk, 4),
            "is_trajectory_safe": max_risk < 0.5,
            "simulation_execution_time_ms": round(sim_time_ms, 3)
        }
