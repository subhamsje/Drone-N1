"""Telemetry lakehouse — failures, crashes, spoofing, recovery events for fleet learning."""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("telemetry_lake")


@dataclass
class LakeRecord:
    record_type: str  # telemetry | failure | crash | spoof | recovery | mission
    uav_id: str
    fleet_id: str
    timestamp: float
    payload: Dict[str, Any]
    labels: List[str] = field(default_factory=list)


class TelemetryLakehouse:
    """
    In-process lake for dev; production → ClickHouse + S3 parquet.
    Feeds online learning and replay infrastructure.
    """

    def __init__(self, fleet_id: str, max_records: int = 100_000):
        self.fleet_id = fleet_id
        self._records: deque = deque(maxlen=max_records)
        self._failure_archive: List[Dict] = []
        self._recovery_archive: List[Dict] = []

    def ingest_cycle(self, snapshot: Dict[str, Any], uav_id: str):
        labels = []
        risk = float(snapshot.get("risk", {}).get("value", 0))
        if snapshot.get("anomaly", {}).get("is_anomaly"):
            labels.append("anomaly")
        if snapshot.get("cybersecurity", {}).get("is_spoofed"):
            labels.append("gps_spoof")
        if risk > 0.7:
            labels.append("high_risk")
        if snapshot.get("decision", {}).get("os_override"):
            labels.append("survival_override")

        rec = LakeRecord("telemetry", uav_id, self.fleet_id, time.time(), snapshot, labels)
        self._records.append(rec)

        if snapshot.get("survival", {}).get("urgency") in ("IMMEDIATE", "HIGH"):
            self._recovery_archive.append({
                "ts": time.time(), "uav_id": uav_id, "plan": snapshot.get("survival"),
            })

        if float(snapshot.get("inference", {}).get("crash_probability", 0)) > 0.8:
            self._failure_archive.append({
                "ts": time.time(), "uav_id": uav_id,
                "crash_prob": snapshot["inference"]["crash_probability"],
            })

    def query_training_batch(self, label: Optional[str] = None, limit: int = 1000) -> List[Dict]:
        out = []
        for rec in reversed(self._records):
            if label and label not in rec.labels:
                continue
            out.append(rec.payload)
            if len(out) >= limit:
                break
        return out

    def get_stats(self) -> Dict[str, Any]:
        return {
            "fleet_id": self.fleet_id,
            "total_records": len(self._records),
            "failures": len(self._failure_archive),
            "recoveries": len(self._recovery_archive),
        }
