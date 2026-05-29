"""Edge AI runtime — Jetson/RPi offline autonomy, buffering, local failover."""

import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List

logger = logging.getLogger("edge.runtime")


@dataclass
class EdgeDeviceProfile:
    device: str  # jetson_orin | rpi | coral
    has_cuda: bool
    has_tensorrt: bool
    max_batch: int = 1
    fp16: bool = True


DEVICE_PROFILES = {
    "jetson_orin": EdgeDeviceProfile("jetson_orin", True, True, 4, True),
    "rpi": EdgeDeviceProfile("rpi", False, False, 1, False),
    "coral": EdgeDeviceProfile("coral", False, False, 1, True),
}


class EdgeRuntime:
    """
    Edge-native intelligence runtime.
    Operates offline with local inference and recovery authority.
    """

    def __init__(self, uav_id: str, device: str = "jetson_orin"):
        self.uav_id = uav_id
        self.profile = DEVICE_PROFILES.get(device, DEVICE_PROFILES["jetson_orin"])
        self._offline_buffer: Deque[Dict] = deque(maxlen=50_000)
        self._cloud_connected = True
        self._local_recovery_authority = True
        self._last_edge_decision_ts = 0.0

    def set_cloud_connected(self, connected: bool):
        self._cloud_connected = connected

    def buffer_telemetry(self, snapshot: Dict[str, Any]):
        self._offline_buffer.append({
            "ts": time.time(),
            "snapshot": snapshot,
        })

    def drain_buffer(self) -> List[Dict]:
        drained = list(self._offline_buffer)
        self._offline_buffer.clear()
        return drained

    def should_use_edge_inference(self) -> bool:
        return not self._cloud_connected or self.profile.has_cuda

    def edge_recovery_authority(self, urgency: str) -> bool:
        if not self._local_recovery_authority:
            return False
        return urgency in ("IMMEDIATE", "HIGH")

    def get_status(self) -> Dict[str, Any]:
        return {
            "uav_id": self.uav_id,
            "device": self.profile.device,
            "cuda": self.profile.has_cuda,
            "tensorrt": self.profile.has_tensorrt,
            "cloud_connected": self._cloud_connected,
            "offline_buffered": len(self._offline_buffer),
            "edge_inference": self.should_use_edge_inference(),
        }
