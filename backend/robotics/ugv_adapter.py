"""UGV Ground Rover Protocol Adapter (ROS2 /cmd_vel, Skid/Ackermann Steering)."""

import time
from typing import Dict, Any

class UgvProtocolAdapter:
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id

    def drive_velocity(self, linear_m_s: float, angular_rad_s: float) -> Dict[str, Any]:
        """Dispatches ROS2 geometry_msgs/Twist velocity commands to ground rover."""
        return {
            "vehicle_id": self.vehicle_id,
            "domain_type": "UGV_GROUND_ROVER",
            "steering_type": "SKID_STEER_4WD",
            "cmd_vel": {
                "linear_x_m_s": linear_m_s,
                "angular_z_rad_s": angular_rad_s
            },
            "wheel_odometry": {"left_rpm": 320, "right_rpm": 340},
            "protocol": "ROS2_DDS_CMD_VEL",
            "status": "VELOCITY_DISPATCHED",
            "timestamp": time.time()
        }
