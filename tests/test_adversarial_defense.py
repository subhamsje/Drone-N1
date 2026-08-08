import pytest
import hmac
import hashlib
from backend.security.adversarial_defense import AdversarialDefenseEngine

def test_gps_spoofing_detection():
    defense = AdversarialDefenseEngine()
    # Large divergence between GPS reported acceleration and IMU body accelerometer
    res = defense.detect_gps_spoofing(gps_accel_ms2=5.4, imu_accel_ms2=1.2, clock_drift_ns=150.0)
    assert res["is_spoofed"] is True
    assert res["recommended_action"] == "FORCE_VIO_OPTICAL_FLOW_HANDOVER"

def test_command_signature_and_replay_rejection():
    secret = "ALTARIA_ZERO_TRUST_ECDSA_ROOT".encode("utf-8")
    defense = AdversarialDefenseEngine("ALTARIA_ZERO_TRUST_ECDSA_ROOT")
    
    nonce = "nonce_104829"
    cmd = "ARM_VEHICLE_ALTARIA"
    msg = f"{nonce}:{cmd}".encode("utf-8")
    sig = hmac.new(secret, msg, hashlib.sha256).hexdigest()

    # First attempt -> Valid
    assert defense.verify_command_signature(cmd, nonce, sig) is True
    # Replay attempt with same nonce -> Rejected
    assert defense.verify_command_signature(cmd, nonce, sig) is False
