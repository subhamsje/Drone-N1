"""MAVLink AI firewall — command validation, rate limiting, replay detection."""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Optional, Set


@dataclass
class FirewallVerdict:
    allowed: bool
    reason: str
    threat_score: float = 0.0
    blocked_count: int = 0


@dataclass
class CommandContext:
    command: str
    uav_id: str
    timestamp: float
    sequence: int = 0
    signature: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)


class MAVLinkFirewall:
    """
    Aerospace-grade command inspection layer above raw MAVLink.
    Integrates with engines.cybersecurity.MAVLinkFirewall concepts.
    """

    BLOCKED_COMMANDS = frozenset({"MAV_CMD_COMPONENT_ARM_DISARM", "MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN"})
    MAX_ALTITUDE_M = 120.0
    MAX_HORIZONTAL_SPEED_MS = 25.0

    def __init__(self, max_cmd_rate_hz: float = 10.0, signed_commands: bool = False):
        self.max_cmd_rate_hz = max_cmd_rate_hz
        self.signed_commands = signed_commands
        self._cmd_times: Deque[float] = deque(maxlen=100)
        self._sequences: Dict[str, int] = {}
        self._blocked_total = 0
        self._trusted_operators: Set[str] = {"system", "recovery-orchestrator", "mission-governance"}

    def inspect(self, ctx: CommandContext) -> FirewallVerdict:
        now = time.time()

        # Rate limiting
        self._cmd_times.append(now)
        recent = [t for t in self._cmd_times if now - t < 1.0]
        if len(recent) > self.max_cmd_rate_hz:
            self._blocked_total += 1
            return FirewallVerdict(False, "rate_limit_exceeded", threat_score=0.6, blocked_count=self._blocked_total)

        # Sequence monotonicity (replay detection)
        last_seq = self._sequences.get(ctx.uav_id, -1)
        if ctx.sequence > 0 and ctx.sequence <= last_seq:
            self._blocked_total += 1
            return FirewallVerdict(False, "replay_detected", threat_score=0.9, blocked_count=self._blocked_total)
        if ctx.sequence > 0:
            self._sequences[ctx.uav_id] = ctx.sequence

        # Signed commands
        if self.signed_commands and not ctx.signature:
            self._blocked_total += 1
            return FirewallVerdict(False, "missing_signature", threat_score=0.7, blocked_count=self._blocked_total)

        # Semantic bounds
        alt = ctx.params.get("altitude_m")
        if alt is not None and float(alt) > self.MAX_ALTITUDE_M:
            self._blocked_total += 1
            return FirewallVerdict(False, "altitude_cap_exceeded", threat_score=0.5, blocked_count=self._blocked_total)

        speed = ctx.params.get("speed_ms")
        if speed is not None and float(speed) > self.MAX_HORIZONTAL_SPEED_MS:
            self._blocked_total += 1
            return FirewallVerdict(False, "speed_cap_exceeded", threat_score=0.5, blocked_count=self._blocked_total)

        # Dangerous command gate (non-trusted sources)
        if ctx.command in self.BLOCKED_COMMANDS and ctx.params.get("source") not in self._trusted_operators:
            self._blocked_total += 1
            return FirewallVerdict(False, "command_not_authorized", threat_score=0.8, blocked_count=self._blocked_total)

        return FirewallVerdict(True, "ok", threat_score=0.0, blocked_count=self._blocked_total)
