"""MAVLink telemetry normalization to cognitive platform schema."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time


@dataclass
class NormalizedTelemetry:
    uav_id: str
    timestamp: float
    altitude_m: float
    battery_pct: float
    rpm: float
    imu: List[float]
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    gps_fix: int = 0
    velocity_ned: Optional[List[float]] = None
    motor_outputs: Optional[List[float]] = None
    vibration: Optional[float] = None
    link_quality: float = 1.0
    raw_msg_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uav_id": self.uav_id,
            "timestamp": self.timestamp,
            "altitude_m": self.altitude_m,
            "battery_pct": self.battery_pct,
            "rpm": self.rpm,
            "imu": self.imu,
            "gps": {"lat": self.gps_lat, "lon": self.gps_lon, "fix": self.gps_fix},
            "velocity_ned": self.velocity_ned,
            "motor_outputs": self.motor_outputs,
            "vibration": self.vibration,
            "link_quality": self.link_quality,
        }


class TelemetryNormalizer:
    """Maps MAVLink message dicts or simulation frames to NormalizedTelemetry."""

    def from_mavlink_dict(self, uav_id: str, msg: Dict[str, Any]) -> NormalizedTelemetry:
        msg_type = msg.get("type", "")
        ts = msg.get("time_usec", time.time() * 1e6) / 1e6 if "time_usec" in msg else time.time()

        if msg_type in ("HEARTBEAT", "heartbeat"):
            return NormalizedTelemetry(
                uav_id=uav_id, timestamp=ts,
                altitude_m=msg.get("alt", 0), battery_pct=100,
                rpm=0, imu=[0, 0, 0], link_quality=1.0,
            )

        if msg_type in ("SYS_STATUS", "sys_status"):
            return NormalizedTelemetry(
                uav_id=uav_id, timestamp=ts,
                altitude_m=0,
                battery_pct=float(msg.get("battery_remaining", 100)),
                rpm=0, imu=[0, 0, 0],
                link_quality=min(1.0, msg.get("drop_rate_comm", 0) / 100.0) if msg.get("drop_rate_comm") else 1.0,
            )

        if msg_type in ("ATTITUDE", "attitude"):
            return NormalizedTelemetry(
                uav_id=uav_id, timestamp=ts,
                altitude_m=0, battery_pct=100, rpm=0,
                imu=[
                    float(msg.get("rollspeed", 0)),
                    float(msg.get("pitchspeed", 0)),
                    float(msg.get("yawspeed", 0)),
                ],
            )

        # Generic fallback
        return NormalizedTelemetry(
            uav_id=uav_id, timestamp=ts,
            altitude_m=float(msg.get("alt", msg.get("relative_alt", 0)) or 0) / 1000.0
            if msg.get("relative_alt") else float(msg.get("altitude", 0)),
            battery_pct=float(msg.get("battery", msg.get("battery_remaining", 100))),
            rpm=float(msg.get("rpm", 0)),
            imu=list(msg.get("imu", [0, 0, 0])),
            gps_lat=msg.get("lat"),
            gps_lon=msg.get("lon"),
            motor_outputs=msg.get("motor_outputs"),
            vibration=msg.get("vibration"),
        )

    def from_simulation_snapshot(self, uav_id: str, snap_dict: Dict[str, Any]) -> NormalizedTelemetry:
        phys = snap_dict.get("physics", {})
        return NormalizedTelemetry(
            uav_id=uav_id,
            timestamp=snap_dict.get("timestamp", time.time()),
            altitude_m=float(phys.get("altitude", 0)),
            battery_pct=float(phys.get("battery", 100)),
            rpm=float(phys.get("rpm", 0)),
            imu=list(phys.get("imu", [0, 0, 0])),
            motor_outputs=list(phys.get("motor_thrusts", [])),
        )
