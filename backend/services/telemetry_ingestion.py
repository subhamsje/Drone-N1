"""High-throughput telemetry ingestion with prioritization."""

import logging
from typing import Any, Dict

from backend.events.bus import get_event_bus
from backend.events.schemas import DomainEvent, EventType
from backend.events.topics import Topic
from backend.mavlink.gateway import MAVLinkGateway
from backend.mavlink.normalizer import NormalizedTelemetry
from backend.storage.repositories import get_state_repository

logger = logging.getLogger("telemetry_ingestion")


class TelemetryIngestionService:
    """Ingests raw/sim telemetry, normalizes, persists, publishes events."""

    def __init__(self, uav_id: str):
        self.uav_id = uav_id
        self.gateway = MAVLinkGateway(uav_id)
        self._bus = get_event_bus()
        self._repo = get_state_repository()
        self._ingest_count = 0
        self._priority_count = 0

    async def ingest_raw(self, raw_msg: Dict[str, Any]) -> NormalizedTelemetry:
        self._ingest_count += 1
        normalized = await self.gateway.ingest_packet(raw_msg)
        await self._maybe_priority_publish(normalized)
        return normalized

    async def ingest_snapshot(self, snapshot: Dict[str, Any]):
        self._ingest_count += 1
        self._repo.upsert_snapshot(self.uav_id, snapshot)
        normalized = await self.gateway.ingest_simulation_snapshot(snapshot)

        await self._bus.publish(
            DomainEvent.create(
                EventType.TWIN_SNAPSHOT,
                self.uav_id,
                {"cycle": snapshot.get("cycle"), "system_state": snapshot.get("system_state")},
            ),
            Topic.TWIN_SNAPSHOT,
        )

        if snapshot.get("anomaly", {}).get("is_anomaly"):
            await self._bus.publish(
                DomainEvent.create(
                    EventType.ANOMALY_DETECTED,
                    self.uav_id,
                    snapshot.get("anomaly", {}),
                ),
                Topic.ANOMALY_DETECTED,
            )

        risk = snapshot.get("risk", {})
        await self._bus.publish(
            DomainEvent.create(EventType.RISK_UPDATED, self.uav_id, risk),
            Topic.RISK_SCORE,
        )

        pred = snapshot.get("prediction", {})
        if float(risk.get("value", 0)) > 0.5:
            await self._bus.publish(
                DomainEvent.create(
                    EventType.PREDICTION_FAILURE,
                    self.uav_id,
                    {**pred, "crash_probability": min(1.0, float(risk.get("value", 0)) * 1.2)},
                ),
                Topic.PREDICTION_FAILURE,
            )

        await self._maybe_priority_publish(normalized)
        return normalized

    async def _maybe_priority_publish(self, tel: NormalizedTelemetry):
        if tel.battery_pct < 20 or (tel.vibration and tel.vibration > 0.8):
            self._priority_count += 1
            await self._bus.publish(
                DomainEvent.create(
                    EventType.TELEMETRY_NORMALIZED,
                    self.uav_id,
                    {**tel.to_dict(), "priority": True},
                ),
                Topic.TELEMETRY_PRIORITY,
            )

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "uav_id": self.uav_id,
            "ingested": self._ingest_count,
            "priority": self._priority_count,
            "gateway": self.gateway.stats,
        }
