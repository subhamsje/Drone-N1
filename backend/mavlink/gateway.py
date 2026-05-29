"""MAVLink gateway — ingest, firewall, normalize, route to event bus."""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from backend.events.bus import get_event_bus
from backend.events.schemas import DomainEvent, EventType
from backend.events.topics import Topic
from backend.mavlink.firewall import CommandContext, MAVLinkFirewall, FirewallVerdict
from backend.mavlink.normalizer import NormalizedTelemetry, TelemetryNormalizer

logger = logging.getLogger("mavlink_gateway")


class MAVLinkGateway:
    """
    Backend abstraction above MAVLink / PX4 / ArduPilot.
    Supports simulation injection and live UDP (when pymavlink available).
    """

    def __init__(self, uav_id: str, connection: str = "udp:127.0.0.1:14550"):
        self.uav_id = uav_id
        self.connection = connection
        self.normalizer = TelemetryNormalizer()
        self.firewall = MAVLinkFirewall()
        self._bus = get_event_bus()
        self._running = False
        self._mavlink = None
        self._packet_count = 0
        self._anomaly_count = 0

    async def ingest_packet(self, raw_msg: Dict[str, Any]) -> Optional[NormalizedTelemetry]:
        """Process a single parsed MAVLink message dict."""
        self._packet_count += 1
        normalized = self.normalizer.from_mavlink_dict(self.uav_id, raw_msg)

        event = DomainEvent.create(
            EventType.TELEMETRY_NORMALIZED,
            self.uav_id,
            normalized.to_dict(),
        )
        await self._bus.publish(event, Topic.TELEMETRY_NORMALIZED)
        await self._bus.publish(
            DomainEvent.create(EventType.TELEMETRY_INGESTED, self.uav_id, {"raw_type": raw_msg.get("type")}),
            Topic.TELEMETRY_RAW,
        )
        return normalized

    async def ingest_simulation_snapshot(self, snap_dict: Dict[str, Any]) -> NormalizedTelemetry:
        normalized = self.normalizer.from_simulation_snapshot(self.uav_id, snap_dict)
        await self._bus.publish(
            DomainEvent.create(EventType.TELEMETRY_NORMALIZED, self.uav_id, normalized.to_dict()),
            Topic.TELEMETRY_NORMALIZED,
        )
        return normalized

    async def submit_command(
        self,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        source: str = "api-gateway",
        sequence: int = 0,
    ) -> FirewallVerdict:
        ctx = CommandContext(
            command=command,
            uav_id=self.uav_id,
            timestamp=time.time(),
            sequence=sequence,
            params={**(params or {}), "source": source},
        )
        verdict = self.firewall.inspect(ctx)

        if verdict.allowed:
            await self._bus.publish(
                DomainEvent.create(
                    EventType.COMMAND_AUTHORIZED,
                    self.uav_id,
                    {"command": command, "params": params, "source": source},
                ),
                Topic.COMMAND_MAVLINK,
            )
            await self._execute_command(command, params)
        else:
            await self._bus.publish(
                DomainEvent.create(
                    EventType.COMMAND_REJECTED,
                    self.uav_id,
                    {"command": command, "reason": verdict.reason, "threat_score": verdict.threat_score},
                ),
                Topic.CYBER_BLOCKED,
            )
            self._anomaly_count += 1

        return verdict

    async def _execute_command(self, command: str, params: Optional[Dict[str, Any]]):
        """Dispatch to pymavlink when available; log in simulation."""
        try:
            from pymavlink import mavutil
            if self._mavlink is None:
                self._mavlink = mavutil.mavlink_connection(self.connection)
            # Map semantic commands to MAVLink — production expands per vehicle type
            logger.info("[%s] MAVLink command: %s %s", self.uav_id, command, params)
        except ImportError:
            logger.debug("[%s] Sim command: %s", self.uav_id, command)

    async def start_live_ingest(self, poll_interval_s: float = 0.02):
        """Background loop for live MAVLink connection."""
        try:
            from pymavlink import mavutil
        except ImportError:
            logger.warning("pymavlink not installed — live ingest disabled")
            return

        self._running = True
        self._mavlink = mavutil.mavlink_connection(self.connection)
        logger.info("MAVLink gateway connected: %s", self.connection)

        while self._running:
            msg = self._mavlink.recv_match(blocking=False)
            if msg is not None:
                await self.ingest_packet(msg.to_dict())
            await asyncio.sleep(poll_interval_s)

    def stop(self):
        self._running = False

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "uav_id": self.uav_id,
            "packets": self._packet_count,
            "blocked": self.firewall._blocked_total,
            "anomalies": self._anomaly_count,
        }
