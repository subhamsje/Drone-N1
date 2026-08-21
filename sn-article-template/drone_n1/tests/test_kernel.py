"""
Unit test suite for Drone-N1 (Altaria OS Kernel)
"""

import unittest
import time
from drone_n1.altaria_kernel import AltariaKernel
from drone_n1.risk_engine import RiskEngine
from drone_n1.afkf_estimator import AFKFEstimator
from drone_n1.ai_safety_shield import AISafetyShield
from drone_n1.digital_twin_sim import DigitalTwinSandbox
from drone_n1.security import CommandSecurityEngine
from drone_n1.scheduler import MixedCriticalityScheduler, ExecutionDomain

class TestDroneN1Kernel(unittest.TestCase):

    def setUp(self):
        self.kernel = AltariaKernel()
        self.risk_engine = RiskEngine()
        self.afkf = AFKFEstimator()
        self.shield = AISafetyShield()
        self.twin = DigitalTwinSandbox()
        self.security = CommandSecurityEngine()
        self.scheduler = MixedCriticalityScheduler()

    def test_risk_engine_calculation(self):
        telemetry = {
            "wind_speed": 5.0,
            "visibility_km": 10.0,
            "battery_soc": 0.9,
            "motor_vibration_g": 0.2,
            "temp_c": 30.0,
            "sprt_residual": 0.1,
            "num_satellites": 14,
            "hdop": 0.8,
            "distance_to_geofence_m": 100.0,
            "execution_delay_s": 0.0
        }
        res = self.risk_engine.compute_aggregate_risk(telemetry)
        self.assertIn("total_risk", res)
        self.assertLess(res["total_risk"], 0.40)
        self.assertEqual(res["threat_level"], "GREEN")

    def test_afkf_gnss_spoofing_detection(self):
        gnss = (10.0, 0.0, 10.0)
        vio = (0.0, 0.0, 10.0)  # 10m residual gap simulating spoofing
        imu = (0.0, 0.0, 9.81)

        # Run multiple updates to build up SPRT log likelihood ratio
        res = None
        for _ in range(5):
            res = self.afkf.process_sensor_fusion(gnss, vio, imu)

        self.assertGreater(res["sprt_residual"], 5.0)
        self.assertEqual(res["active_mode"], "VIO_TAKEOVER")

    def test_safety_shield_enforcement(self):
        # Overspeed command (25 m/s > max 15 m/s limit)
        is_safe, clamped = self.shield.validate_command(20.0, 15.0, 0.0, 10.0, 100.0)
        self.assertFalse(is_safe)
        self.assertIn("violations", clamped)
        self.assertLessEqual(clamped["clamped_cmd"][0], 15.0)

    def test_ecdsa_command_verification(self):
        cmd = self.security.sign_mavlink_command(101, (5.0, 0.0, 0.0, 10.0))
        is_valid = self.security.verify_mavlink_command_signature(
            cmd["command_id"],
            cmd["target_setpoints"],
            cmd["timestamp"],
            cmd["signature_hex"]
        )
        self.assertTrue(is_valid)

    def test_mixed_criticality_scheduler(self):
        counter = {"d0": 0, "d5": 0}
        self.scheduler.add_task("task_d5", ExecutionDomain.D5_FLIGHT_ANALYTICS, lambda: counter.update(d5=1))
        self.scheduler.add_task("task_d0", ExecutionDomain.D0_FLIGHT_STABILIZATION, lambda: counter.update(d0=1))

        res = self.scheduler.execute_pending_tasks()
        self.assertEqual(res["executed_count"], 2)
        self.assertEqual(counter["d0"], 1)
        self.assertEqual(counter["d5"], 1)

if __name__ == "__main__":
    unittest.main()
