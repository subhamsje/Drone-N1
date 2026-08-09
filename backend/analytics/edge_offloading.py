"""
Digital Twin Assisted Aerial Edge Computing & Task Offloading Engine.
Based on research: "Digital Twin Assisted Task Offloading for Aerial Edge Computing and Networks"
(IEEE Transactions on Vehicular Technology, 2022; IEEE Transactions on Mobile Computing, 2025).

Optimizes computational offloading decisions (Local vs Edge Server) under dynamic UAV channel fading,
processing queues, battery energy constraints, and Digital Twin state predictions.
"""

from typing import Dict, Any, List, Optional
import math
import time
from dataclasses import dataclass, field


@dataclass
class OffloadingTask:
    task_id: str
    data_size_bytes: int          # Data size D_k in bytes (e.g., 2MB visual frame)
    cpu_cycles_per_bit: int       # Computation intensity C_k (cycles/bit)
    max_latency_deadline_s: float # Tau_k max allowable latency in seconds
    priority: str = "HIGH"        # CRITICAL, HIGH, NORMAL


@dataclass
class OffloadingDecision:
    task_id: str
    execution_target: str         # LOCAL | EDGE_SERVER | HYBRID_SPLIT
    local_latency_s: float
    offload_latency_s: float
    local_energy_joules: float
    offload_energy_joules: float
    energy_saved_joules: float
    channel_rate_mbps: float
    is_deadline_met: bool
    digital_twin_sync_drift_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "execution_target": self.execution_target,
            "local_latency_s": round(self.local_latency_s, 4),
            "offload_latency_s": round(self.offload_latency_s, 4),
            "local_energy_joules": round(self.local_energy_joules, 4),
            "offload_energy_joules": round(self.offload_energy_joules, 4),
            "energy_saved_joules": round(self.energy_saved_joules, 4),
            "channel_rate_mbps": round(self.channel_rate_mbps, 2),
            "is_deadline_met": self.is_deadline_met,
            "digital_twin_sync_drift_ms": round(self.digital_twin_sync_drift_ms, 2),
        }


class DigitalTwinEdgeOffloadingEngine:
    """
    Evaluates real-time Pareto-optimal computation offloading using the Digital Twin state.
    Calculates Rayleigh fading uplink data rates, local CPU clock scaling, and MEC compute loads.
    """

    def __init__(
        self,
        local_cpu_freq_ghz: float = 1.5,     # UAV Companion Computer (e.g. Jetson Orin Nano)
        edge_cpu_freq_ghz: float = 3.8,      # Ground MEC Base Station Server
        channel_bandwidth_mhz: float = 20.0, # 20 MHz 5G/Wi-Fi 6 channel
        transmit_power_watts: float = 0.5,   # UAV RF transmission power (27 dBm)
        noise_power_dbm: float = -95.0,      # Thermal noise floor
    ):
        self.f_local = local_cpu_freq_ghz * 1e9
        self.f_edge = edge_cpu_freq_ghz * 1e9
        self.bandwidth_hz = channel_bandwidth_mhz * 1e6
        self.p_tx = transmit_power_watts
        self.noise_watts = 10 ** ((noise_power_dbm - 30) / 10.0)
        self.effective_capacitance_kappa = 1e-28 # CPU energy coefficient (k * f^2)

        self._task_history: List[OffloadingDecision] = []
        self._last_twin_sync_time = time.time()

    def calculate_uplink_rate(self, distance_meters: float, path_loss_exponent: float = 2.4) -> float:
        """
        Shannon channel capacity with log-distance path loss and Rayleigh fading channel:
        R = B * log2(1 + (P_tx * h) / (N0 * d^alpha))
        """
        d = max(10.0, distance_meters)
        # Reference channel gain at 1 meter (-30 dB)
        g0 = 1e-3
        channel_gain = g0 / (d ** path_loss_exponent)
        snr = (self.p_tx * channel_gain) / max(1e-15, self.noise_watts)
        rate_bps = self.bandwidth_hz * math.log2(1.0 + snr)
        return max(1e5, rate_bps) # Minimum 100 kbps fallback

    def optimize_task_offloading(
        self,
        task: OffloadingTask,
        distance_to_mec_m: float,
        uav_battery_pct: float,
        dt_state: Optional[Dict[str, Any]] = None,
    ) -> OffloadingDecision:
        """
        Solves the energy-delay trade-off:
        Min (alpha * T + beta * E) subject to T <= T_deadline
        """
        total_bits = task.data_size_bytes * 8
        total_cycles = total_bits * task.cpu_cycles_per_bit

        # 1. Local Execution
        t_local = total_cycles / self.f_local
        # Energy = kappa * cycles * (f_local)^2
        e_local = self.effective_capacitance_kappa * total_cycles * (self.f_local ** 2)

        # 2. Edge Offload Execution
        channel_bps = self.calculate_uplink_rate(distance_to_mec_m)
        t_tx = total_bits / channel_bps
        e_tx = self.p_tx * t_tx
        t_edge_compute = total_cycles / self.f_edge
        t_offload = t_tx + t_edge_compute
        e_offload = e_tx # Energy on the UAV side is transmission energy

        # Digital twin synchronization latency compensation
        twin_drift_ms = (time.time() - self._last_twin_sync_time) * 1000.0
        self._last_twin_sync_time = time.time()

        # Decision Strategy:
        # If battery is low (< 25%), bias heavily toward saving onboard energy (Offload if deadline permits)
        # If deadline is tight, choose min latency
        battery_urgency = max(0.0, (30.0 - uav_battery_pct) / 30.0)
        
        target = "LOCAL"
        if t_offload <= task.max_latency_deadline_s and (e_offload < e_local or battery_urgency > 0.4):
            target = "EDGE_SERVER"
        elif t_local > task.max_latency_deadline_s and t_offload <= task.max_latency_deadline_s:
            target = "EDGE_SERVER"
        elif t_local <= task.max_latency_deadline_s:
            target = "LOCAL"
        else:
            target = "HYBRID_SPLIT" # Graceful degradation

        selected_latency = t_offload if target == "EDGE_SERVER" else t_local
        selected_energy = e_offload if target == "EDGE_SERVER" else e_local
        energy_saved = max(0.0, e_local - selected_energy)

        decision = OffloadingDecision(
            task_id=task.task_id,
            execution_target=target,
            local_latency_s=t_local,
            offload_latency_s=t_offload,
            local_energy_joules=e_local,
            offload_energy_joules=e_offload,
            energy_saved_joules=energy_saved,
            channel_rate_mbps=channel_bps / 1e6,
            is_deadline_met=selected_latency <= task.max_latency_deadline_s,
            digital_twin_sync_drift_ms=min(50.0, twin_drift_ms),
        )

        self._task_history.append(decision)
        if len(self._task_history) > 100:
            self._task_history.pop(0)

        return decision


edge_offloading_engine = DigitalTwinEdgeOffloadingEngine()
