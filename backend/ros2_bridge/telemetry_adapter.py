"""
ROS2 Telemetry Adapter
Subscribes to ArduPilot/Gazebo sensor topics and normalizes them into Altaria Cognitive State.
"""

import logging
from typing import Any, Dict

from backend.ros2_bridge.node import AltariaROS2Node
from backend.events.bus import get_event_bus
from backend.events.schemas import DomainEvent, EventType
from backend.events.topics import Topic

logger = logging.getLogger("ros2_telemetry")


class ROS2TelemetryAdapter:
    def __init__(self, node: AltariaROS2Node):
        self.node = node
        self.uav_id = node.uav_id
        self._bus = get_event_bus()

        # Subscribe to standard ROS2 / PX4-ROS2 topics
        self.node.create_subscription(f"/{self.uav_id}/fmu/out/vehicle_gps_position", None, self._on_gps)
        self.node.create_subscription(f"/{self.uav_id}/fmu/out/sensor_combined", None, self._on_imu)
        self.node.create_subscription(f"/{self.uav_id}/fmu/out/battery_status", None, self._on_battery)
        
        self._state_cache = {
            "vehicle_id": self.uav_id,
            "position": {"lat": 0.0, "lon": 0.0, "alt": 0.0},
            "velocity": {"n": 0.0, "e": 0.0, "d": 0.0},
            "battery": 1.0,
            "health": "NOMINAL",
            "confidence": 1.0,
            "mission_state": "ACTIVE",
            "survivability_score": 1.0
        }

    async def _on_gps(self, msg: Any):
        # Translate ROS2 GPS msg to Altaria state
        self._state_cache["position"] = {"lat": msg.lat, "lon": msg.lon, "alt": msg.alt}
        await self._publish_normalized()

    async def _on_imu(self, msg: Any):
        # Update velocities and health
        pass

    async def _on_battery(self, msg: Any):
        self._state_cache["battery"] = msg.remaining

    async def _publish_normalized(self):
        event = DomainEvent.create(
            EventType.TELEMETRY_NORMALIZED,
            self.uav_id,
            self._state_cache
        )
        await self._bus.publish(event, Topic.TELEMETRY_NORMALIZED)
