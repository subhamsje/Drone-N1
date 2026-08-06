"""Master Robotics Protocol Adapter Factory."""

from typing import Dict, Any
from backend.robotics.schemas import DomainVehicleType
from backend.robotics.uav_adapter import UavProtocolAdapter
from backend.robotics.vtol_adapter import VtolProtocolAdapter
from backend.robotics.ugv_adapter import UgvProtocolAdapter
from backend.robotics.usv_adapter import UsvProtocolAdapter

class RoboticsAdapterFactory:
    @staticmethod
    def get_adapter(vehicle_id: str, vehicle_type: DomainVehicleType):
        """Instantiates appropriate domain protocol adapter based on vehicle_type."""
        if vehicle_type == DomainVehicleType.UGV:
            return UgvProtocolAdapter(vehicle_id)
        elif vehicle_type == DomainVehicleType.USV:
            return UsvProtocolAdapter(vehicle_id)
        elif vehicle_type == DomainVehicleType.VTOL:
            return VtolProtocolAdapter(vehicle_id)
        else:
            return UavProtocolAdapter(vehicle_id)
