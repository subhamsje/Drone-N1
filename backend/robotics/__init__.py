"""Robotics Bounded Context Package."""

from backend.robotics.schemas import DomainVehicleType, MultiDomainTelemetryEnvelope
from backend.robotics.uav_adapter import UavProtocolAdapter
from backend.robotics.vtol_adapter import VtolProtocolAdapter
from backend.robotics.ugv_adapter import UgvProtocolAdapter
from backend.robotics.usv_adapter import UsvProtocolAdapter
from backend.robotics.adapter_factory import RoboticsAdapterFactory

__all__ = [
    "DomainVehicleType",
    "MultiDomainTelemetryEnvelope",
    "UavProtocolAdapter",
    "VtolProtocolAdapter",
    "UgvProtocolAdapter",
    "UsvProtocolAdapter",
    "RoboticsAdapterFactory"
]
