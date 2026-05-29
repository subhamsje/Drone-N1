"""Real flight-hour intelligence — operational telemetry harvesting and cognition archives."""

import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np

logger = logging.getLogger("flight_hour_intel")


@dataclass
class FlightHourRecord:
    uav_id: str
    flight_hours: float
    cycles: int
    mean_survivability: float
    anomaly_count: int
    recovery_count: int

    def to_dict(self) -> Dict:
        return {k: round(v, 4) if isinstance(v, float) else v for k, v in self.__dict__.items()}


class FlightHourIntelligenceEngine:
    """
    Harvests operational telemetry into durable cognition archives.
    Anomaly, actuator aging, environment, recovery replay, failure distributions.
    """

    def __init__(self, uav_id: str):
        self.uav_id = uav_id
        self._cycle_count = 0
        self._flight_hours = 0.0
        self._cycle_dt_h = 0.2 / 3600.0  # 200ms loop
        self._anomaly_archive: deque = deque(maxlen=10_000)
        self._actuator_aging: Dict[str, List[float]] = {"m0": [], "m1": [], "m2": [], "m3": []}
        self._environment_archive: deque = deque(maxlen=5_000)
        self._recovery_replay: deque = deque(maxlen=2_000)
        self._failure_events: List[Dict] = []
        self._surv_samples: List[float] = []

    def harvest_cycle(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        self._cycle_count += 1
        self._flight_hours += self._cycle_dt_h

        surv = float(snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0))
        self._surv_samples.append(surv)
        if len(self._surv_samples) > 5000:
            self._surv_samples = self._surv_samples[-2500:]

        anomaly_score = float(snapshot.get("anomaly", {}).get("score", 0))
        if anomaly_score > 0.55:
            self._anomaly_archive.append({
                "ts": time.time(),
                "score": anomaly_score,
                "risk": float(snapshot.get("risk", {}).get("value", 0)),
            })

        motors = snapshot.get("physics", {}).get("motor_thrusts", [5.42] * 4)
        if isinstance(motors, list):
            for i, t in enumerate(motors[:4]):
                key = f"m{i}"
                self._actuator_aging[key].append(float(t))
                if len(self._actuator_aging[key]) > 500:
                    self._actuator_aging[key] = self._actuator_aging[key][-250:]

        env_sig = snapshot.get("embodied_cognition", {}).get("weather_signature_id", "wx_0")
        region = snapshot.get("embodied_cognition", {}).get("regional_profile", "default")
        self._environment_archive.append({
            "ts": time.time(),
            "signature": env_sig,
            "region": region,
            "turbulence": float(snapshot.get("twin_physics", {}).get("turbulence_estimate", 0)),
        })

        if snapshot.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"):
            self._recovery_replay.append({
                "ts": time.time(),
                "strategy": snapshot.get("survival", {}).get("strategy"),
                "surv": surv,
                "audit_id": snapshot.get("safety_audit_id"),
                "lineage": snapshot.get("operational_trust", {}).get("recovery_lineage", []),
            })

        crash_p = float(snapshot.get("inference", {}).get("crash_probability", 0))
        if crash_p > 0.75 or surv < 0.35:
            self._failure_events.append({
                "ts": time.time(),
                "crash_p": crash_p,
                "surv": surv,
                "phase": snapshot.get("flight_operations", {}).get("mission_phase", "?"),
            })
            if len(self._failure_events) > 500:
                self._failure_events = self._failure_events[-250:]

        return self.get_intelligence_export()

    def get_intelligence_export(self) -> Dict[str, Any]:
        actuator_wear = {}
        for k, vals in self._actuator_aging.items():
            if vals:
                mean_t = np.mean(vals)
                std_t = np.std(vals)
                actuator_wear[k] = {"mean_thrust": round(mean_t, 4), "wear_index": round(std_t / max(mean_t, 0.1), 4)}

        failure_dist = {}
        if self._failure_events:
            failure_dist = {
                "count": len(self._failure_events),
                "mean_crash_p": round(np.mean([f["crash_p"] for f in self._failure_events[-50:]]), 4),
                "mean_surv_at_failure": round(np.mean([f["surv"] for f in self._failure_events[-50:]]), 4),
            }

        return {
            "uav_id": self.uav_id,
            "flight_hours": round(self._flight_hours, 4),
            "operational_cycles": self._cycle_count,
            "mean_survivability": round(np.mean(self._surv_samples), 4) if self._surv_samples else 0,
            "anomaly_archive_size": len(self._anomaly_archive),
            "recent_anomalies": list(self._anomaly_archive)[-5:],
            "actuator_aging_dataset": actuator_wear,
            "environment_archive_size": len(self._environment_archive),
            "recovery_replay_dataset_size": len(self._recovery_replay),
            "recent_recoveries": list(self._recovery_replay)[-3:],
            "mission_failure_distribution": failure_dist,
        }
