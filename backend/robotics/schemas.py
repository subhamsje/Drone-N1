"""Universal Multi-Domain Robotics Schemas (UAV, UGV, USV, VTOL, Fixed-Wing, Robot Arm)."""

from enum import Enum
from typing import Dict, Any, Optional

class DomainVehicleType(str, Enum):
    UAV = "UAV_MULTI_ROTOR"
    VTOL = "VTOL_HYBRID"
    FIXED_WING = "FIXED_WING_AIRPLANE"
    UGV = "UGV_GROUND_ROVER"
    USV = "USV_SURFACE_BOAT"
    ROBOT_ARM = "ROBOT_ARM_MANIPULATOR"

class MultiDomainTelemetryEnvelope:
    def __init__(self, vehicle_id: str, vehicle_type: DomainVehicleType):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type

    def project_schema(self, pose_3d: Dict[str, float]) -> Dict[str, Any]:
        return {
            "vehicle_id": self.vehicle_id,
            "domain_type": self.vehicle_type.value,
            "pose": pose_3d,
            "multi_domain_ready": True
        }
