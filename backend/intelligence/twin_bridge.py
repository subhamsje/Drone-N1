"""
Digital twin bridge — Gazebo + PX4/ArduPilot SITL/HITL.

Altaria does not replace Gazebo. It injects scenarios and reads outcomes for training/validation.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("twin_bridge")


@dataclass
class SimulationScenario:
    name: str
    wind_mps: float = 0.0
    turbulence: float = 0.0
    gps_spoof: bool = False
    sensor_failure: Optional[str] = None
    actuator_failure: Optional[str] = None
    duration_s: float = 60.0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


class DigitalTwinBridge:
    """
    Hooks for:
    - Gazebo wind plugins
    - PX4 SITL (udp://:14540)
    - ArduPilot SITL via MAVProxy
    - HITL benches

    Set ALTARIA_PX4_SITL=1 and run validation scripts in altaria_os/validation/.
    """

    PRESETS = {
        "calm": SimulationScenario("calm", wind_mps=2, turbulence=0.05),
        "gusty": SimulationScenario("gusty", wind_mps=12, turbulence=0.45),
        "spoof": SimulationScenario("spoof", gps_spoof=True, tags=["cyber"]),
        "imu_fail": SimulationScenario("imu_fail", sensor_failure="imu", tags=["hardware"]),
        "motor_degraded": SimulationScenario("motor_degraded", actuator_failure="motor_3"),
    }

    def __init__(self):
        self._active: Optional[SimulationScenario] = None

    def load_scenario(self, name: str) -> SimulationScenario:
        self._active = self.PRESETS.get(name, SimulationScenario(name))
        logger.info("Twin scenario loaded: %s", self._active.name)
        return self._active

    def apply_to_snapshot(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Inject scenario into cognitive snapshot path (SITL/HITL validation)."""
        if not self._active:
            return snapshot
        s = self._active
        snapshot.setdefault("twin_physics", {})["turbulence_estimate"] = s.turbulence
        snapshot.setdefault("twin_physics", {})["wind_mps"] = s.wind_mps
        if s.gps_spoof:
            snapshot.setdefault("cybersecurity", {})["is_spoofed"] = True
        if s.sensor_failure:
            snapshot.setdefault("sensor_trust", {})[f"{s.sensor_failure}_trust"] = 0.2
        snapshot["simulation_scenario"] = s.to_dict()
        return snapshot

    def gazebo_launch_hint(self) -> Dict[str, str]:
        return {
            "px4_sitl": "make px4_sitl gazebo",
            "ardupilot_sitl": "sim_vehicle.py -v ArduCopter --map --console",
            "mavproxy": "mavproxy.py --master=udp:127.0.0.1:14550",
            "altaria_connect": "POST /api/v1/execution/command CONNECT udp://:14540",
        }
