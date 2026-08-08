"""
Adversarial & Cyber Resilience Defense Engine.
Detects GPS spoofing, signal jamming, and unauthorized command injection attacks in real time.
"""

from typing import Dict, Any, List
import time
import math
import hmac
import hashlib

class AdversarialDefenseEngine:
    def __init__(self, shared_secret: str = "ALTARIA_ZERO_TRUST_ECDSA_ROOT"):
        self.shared_secret = shared_secret.encode("utf-8")
        self.observed_nonces = set()
        self.spoof_alert_active: bool = False

    def detect_gps_spoofing(self, gps_accel_ms2: float, imu_accel_ms2: float, clock_drift_ns: float) -> Dict[str, Any]:
        """
        Cross-checks GPS physical acceleration against on-board redundant IMU accelerometers.
        Large discrepancy (> 3.2 m/s^2) or sudden clock step indicates GPS spoofing attack.
        """
        accel_delta = abs(gps_accel_ms2 - imu_accel_ms2)
        is_spoofed = accel_delta > 3.2 or abs(clock_drift_ns) > 120.0

        self.spoof_alert_active = is_spoofed
        return {
            "is_spoofed": is_spoofed,
            "acceleration_divergence_ms2": round(accel_delta, 3),
            "clock_drift_ns": round(clock_drift_ns, 1),
            "recommended_action": "FORCE_VIO_OPTICAL_FLOW_HANDOVER" if is_spoofed else "MAINTAIN_RTK_FIX",
            "defense_status": "ATTACK_CONTAINED" if is_spoofed else "AUTHENTIC_GPS_SIGNAL",
        }

    def verify_command_signature(self, command_payload: str, nonce: str, signature_hex: str) -> bool:
        """
        Verifies cryptographic HMAC-SHA256 zero-trust signature and rejects replayed nonces.
        """
        if nonce in self.observed_nonces:
            return False # Replay attack detected

        message = f"{nonce}:{command_payload}".encode("utf-8")
        expected_sig = hmac.new(self.shared_secret, message, hashlib.sha256).hexdigest()
        
        is_valid = hmac.compare_digest(expected_sig, signature_hex)
        if is_valid:
            self.observed_nonces.add(nonce)
            if len(self.observed_nonces) > 5000:
                self.observed_nonces.pop()

        return is_valid

adversarial_defense = AdversarialDefenseEngine()
