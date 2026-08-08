import pytest
from backend.intelligence.autonomy_gradient import AutonomyAuthorityManager, AutonomyLevel

def test_manual_mode_blocks_ai_commands():
    mgr = AutonomyAuthorityManager(AutonomyLevel.MANUAL)
    res = mgr.validate_command_authority("TAKEOFF", "AI_COGNITIVE_KERNEL")
    assert res["authorized"] is False

def test_supervised_mode_requests_human_ack():
    mgr = AutonomyAuthorityManager(AutonomyLevel.SUPERVISED)
    res = mgr.validate_command_authority("ARM", "AI_COGNITIVE_KERNEL")
    assert res["authorized"] is True
    assert res.get("requires_human_ack") is True

def test_safety_override_always_authorized():
    mgr = AutonomyAuthorityManager(AutonomyLevel.MANUAL)
    res = mgr.validate_command_authority("EMERGENCY_FLARE", "SAFETY_OVERRIDE_SYSTEM")
    assert res["authorized"] is True
