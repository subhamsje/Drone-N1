"""
Deterministic Temporal Replay & Time-Travel Debugging Engine.
Enables frame-by-frame seeking, blackbox flight analysis, and FAA/EASA incident recreation.
"""

from typing import Dict, Any, List, Optional
import time

class TelemetrySnapshot:
    def __init__(self, timestamp: float, altitude_m: float, airspeed_ms: float, pitch_deg: float, roll_deg: float, battery_pct: float, decision_log: str):
        self.timestamp = timestamp
        self.altitude_m = altitude_m
        self.airspeed_ms = airspeed_ms
        self.pitch_deg = pitch_deg
        self.roll_deg = roll_deg
        self.battery_pct = battery_pct
        self.decision_log = decision_log

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "altitude_m": self.altitude_m,
            "airspeed_ms": self.airspeed_ms,
            "pitch_deg": self.pitch_deg,
            "roll_deg": self.roll_deg,
            "battery_pct": self.battery_pct,
            "decision_log": self.decision_log,
        }

class TemporalReplayEngine:
    def __init__(self):
        self.timeline: List[TelemetrySnapshot] = []
        self.current_cursor_idx: int = 0
        self.playback_speed: float = 1.0
        self.is_playing: bool = False

    def record_frame(self, altitude_m: float, airspeed_ms: float, pitch_deg: float, roll_deg: float, battery_pct: float, decision_log: str = "NOMINAL_CRUISE") -> None:
        snap = TelemetrySnapshot(
            timestamp=time.time(),
            altitude_m=altitude_m,
            airspeed_ms=airspeed_ms,
            pitch_deg=pitch_deg,
            roll_deg=roll_deg,
            battery_pct=battery_pct,
            decision_log=decision_log,
        )
        self.timeline.append(snap)
        if len(self.timeline) > 5000:
            self.timeline.pop(0)

    def seek(self, timestamp: float) -> Optional[Dict[str, Any]]:
        """Finds closest telemetry frame to given timestamp."""
        if not self.timeline:
            return None
        closest = min(self.timeline, key=lambda s: abs(s.timestamp - timestamp))
        self.current_cursor_idx = self.timeline.index(closest)
        return closest.to_dict()

    def step_forward(self) -> Optional[Dict[str, Any]]:
        if not self.timeline:
            return None
        self.current_cursor_idx = min(len(self.timeline) - 1, self.current_cursor_idx + 1)
        return self.timeline[self.current_cursor_idx].to_dict()

    def step_backward(self) -> Optional[Dict[str, Any]]:
        if not self.timeline:
            return None
        self.current_cursor_idx = max(0, self.current_cursor_idx - 1)
        return self.timeline[self.current_cursor_idx].to_dict()

    def get_full_timeline_summary(self) -> Dict[str, Any]:
        return {
            "total_frames": len(self.timeline),
            "cursor_idx": self.current_cursor_idx,
            "playback_speed": self.playback_speed,
            "duration_sec": round(self.timeline[-1].timestamp - self.timeline[0].timestamp, 2) if len(self.timeline) > 1 else 0.0,
        }

temporal_replay_engine = TemporalReplayEngine()
