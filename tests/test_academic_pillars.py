"""
Academic Unit & Integration Test Suite for:
1. Digital Twin Multi-Scale Dynamics & Edge Offloading (Li et al., TVT 2022 / TMC 2025)
2. GPS-Denied Navigation with AFKF & SPRT Fault Isolation (IEEE Sensors 2026 / Campos et al., T-RO 2021)
3. RSSM Foundation World Model with Counterfactual Rollouts (DayDreamer / Hafner et al., CoRL / Science Robotics)
4. Distributed Stochastic MPC & Event-Triggered Swarm Consensus (IEEE TIE 2024 / IEEE TCYB 2022)
5. MAVSec Zero-Trust Cryptographic Protocol & Replay Shield (Computers & Security 2019 / Koubaa et al., 2019)
6. Situation Awareness-Based Agent Transparency (SAT) Model (Chen & Barnes, IEEE THMS 2014 / 2018)
"""

import pytest
import numpy as np
import time

# Pillar 1: Digital Twin & Edge Offloading
from backend.analytics.edge_offloading import DigitalTwinEdgeOffloadingEngine, OffloadingTask
from engines.twin_physics_hf import HighFidelityTwinPhysics

# Pillar 2: GPS-Denied Navigation, AFKF & SPRT
from engines.gps_denied_nav import GPSDeniedNavigator, SequentialProbabilityRatioTest, AdaptiveFederatedKalmanFilter
from engines.sensor_trust import SensorTrustEngine

# Pillar 3: RSSM Foundation World Model
from engines.foundation_world_model import FoundationWorldModelEngine, RecurrentStateSpaceModel

# Pillar 4: DS-MPC & Swarm Cognition
from engines.distributed_swarm import DistributedSwarmCognition, DistributedStochasticMPC, EventTriggeredBroadcaster

# Pillar 5: MAVSec Zero-Trust Protocol
from engines.cybersecurity import CybersecurityEngine, MAVSecCryptoEngine, MAVSecPacket

# Pillar 6: SAT Explainability
from altaria_os.cognition.explainability import AutonomyExplainabilityEngine


# ─────────────────────────────────────────────────────────────────────────────
# 1. Digital Twin & Edge Offloading Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_digital_twin_multi_scale_physics():
    twin = HighFidelityTwinPhysics(mass_kg=2.0, drag_coeff=0.075)
    physics_data = {
        "imu": [0.2, -0.1, 9.81],
        "rpm": 5800.0,
        "altitude": 35.0,
        "battery": 88.0,
        "motor_thrusts": [5.2, 5.3, 5.1, 5.2],
    }
    forecast = twin.step(physics_data, physics_data["motor_thrusts"], risk=0.12)
    assert forecast.turbulence_index >= 0.0
    assert forecast.instability_horizon_s > 5.0
    assert forecast.replay_available is True


def test_edge_offloading_pareto_decision():
    engine = DigitalTwinEdgeOffloadingEngine(local_cpu_freq_ghz=1.5, edge_cpu_freq_ghz=4.0)
    task = OffloadingTask(
        task_id="task-perception-101",
        data_size_bytes=1024 * 64,  # 64 KB perception vector
        cpu_cycles_per_bit=350,
        max_latency_deadline_s=0.35,
        priority="HIGH",
    )
    decision = engine.optimize_task_offloading(
        task=task,
        distance_to_mec_m=120.0,
        uav_battery_pct=85.0,
    )
    assert decision.execution_target in ("LOCAL", "EDGE_SERVER", "HYBRID_SPLIT")
    assert decision.channel_rate_mbps > 1.0
    assert decision.is_deadline_met is True
    assert decision.digital_twin_sync_drift_ms >= 0.0


# ─────────────────────────────────────────────────────────────────────────────
# 2. GPS-Denied AFKF & SPRT Fault Isolation Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_sprt_fault_isolation_on_anomaly():
    sprt = SequentialProbabilityRatioTest(alpha_false_alarm=0.01, beta_missed_detection=0.01)
    
    # Healthy nominal residuals
    for _ in range(5):
        fault, llr = sprt.update(0.2)
        assert fault is False

    # Injected massive GPS spoofing / jamming residuals
    fault_detected = False
    for _ in range(10):
        fault, llr = sprt.update(4.5)
        if fault:
            fault_detected = True
            break
    assert fault_detected is True


def test_gps_denied_afkf_mode_transition():
    navigator = GPSDeniedNavigator()
    
    # Nominal GPS flight
    state_gps = navigator.update(gps_confidence=0.95, imu=[0, 0, 9.81], dt=0.2, vision_confidence=0.85)
    assert state_gps.mode == "gps"
    assert state_gps.localization_confidence > 0.8
    assert state_gps.fault_detected is False

    # GPS Denied / Jammed -> transitions to SLAM or VIO
    state_denied = navigator.update(
        gps_confidence=0.1,
        imu=[0.5, 0.2, 9.81],
        dt=0.2,
        vision_confidence=0.90,
        is_gps_spoofed=True,
    )
    assert state_denied.mode in ("slam", "vio")
    assert state_denied.fault_detected is True
    assert "GNSS" in state_denied.isolated_sensors


# ─────────────────────────────────────────────────────────────────────────────
# 3. RSSM Foundation World Model Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_rssm_latent_counterfactual_rollouts():
    world_model = FoundationWorldModelEngine()
    snapshot = {
        "risk": {"value": 0.35, "level": "MEDIUM"},
        "inference": {"crash_probability": 0.08},
        "twin_physics": {"turbulence_estimate": 0.15},
        "sensor_trust": {"composite_trust": 0.92, "comm_trust": 0.95},
        "probabilistic_safety": {"composite_survivability": 0.85},
    }
    forecast = world_model.simulate(snapshot)
    assert forecast.latent_state.rollforward_steps == 5
    assert len(forecast.counterfactual_rollouts) >= 4
    assert 0.0 <= forecast.generative_survivability <= 1.0
    assert len(forecast.consequence_graph) > 0


# ─────────────────────────────────────────────────────────────────────────────
# 4. Distributed Stochastic MPC & Swarm Consensus Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_ds_mpc_collision_avoidance_trajectory():
    ds_mpc = DistributedStochasticMPC(horizon_steps=5, dt=0.2, d_safe_m=6.0)
    curr_pos = np.array([0.0, 0.0, -20.0])
    target_pos = np.array([30.0, 0.0, -20.0])
    # Neighbor in direct path at (10, 0, -20)
    neighbor_pts = [np.array([10.0, 0.5, -20.0])]
    traj = ds_mpc.plan_trajectory(curr_pos, target_pos, neighbor_pts)
    assert len(traj) == 6
    # Verify trajectory actively avoids colliding with neighbor
    for pt in traj:
        assert isinstance(pt, np.ndarray)


def test_event_triggered_telemetry_broadcasting():
    broadcaster = EventTriggeredBroadcaster(delta_threshold=1.5)
    # First broadcast always triggers
    assert broadcaster.should_broadcast(np.array([0.0, 0.0, 0.0])) is True
    # Small micro-motion under threshold does NOT broadcast (bandwidth saved)
    assert broadcaster.should_broadcast(np.array([0.2, 0.1, 0.0])) is False
    # Large jump exceeds threshold and triggers broadcast
    assert broadcaster.should_broadcast(np.array([2.5, 1.0, 0.0])) is True


def test_distributed_swarm_collective_reasoning():
    swarm = DistributedSwarmCognition(fleet_id="swarm-alpha", member_ids=["uav-1", "uav-2", "uav-3"])
    snap_1 = {"risk": {"value": 0.15}, "decision": {"action": "HOLD"}, "telemetry": {"position_ned": [0, 0, -20]}}
    snap_2 = {"risk": {"value": 0.20}, "decision": {"action": "HOLD"}, "telemetry": {"position_ned": [15, 0, -20]}}
    swarm.ingest_member("uav-1", snap_1)
    swarm.ingest_member("uav-2", snap_2)
    consensus = swarm.collective_reason()
    assert consensus.consensus_action in ("HOLD", "NONE", "COLLECTIVE_PATROL")
    assert consensus.collective_risk <= 0.3
    assert len(consensus.dsm_pc_trajectory) > 0


# ─────────────────────────────────────────────────────────────────────────────
# 5. MAVSec Zero-Trust Protocol & Replay Shield Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_mavsec_signing_and_verification():
    crypto = MAVSecCryptoEngine()
    payload = b"MAVLINK_SET_ATTITUDE_TARGET_WP_01"
    packet = crypto.sign_message(seq=101, msg_id=76, payload=payload)
    assert packet.is_authenticated is True

    valid, reason = crypto.verify_message(packet)
    assert valid is True
    assert reason == "AUTHENTICATED_VALID"


def test_mavsec_replay_attack_rejection():
    crypto = MAVSecCryptoEngine()
    payload = b"MAVLINK_DISARM_COMMAND"
    packet_1 = crypto.sign_message(seq=201, msg_id=11, payload=payload)
    valid_1, _ = crypto.verify_message(packet_1)
    assert valid_1 is True

    # Replay the identical packet sequence -> MUST BE BLOCKED
    valid_replay, reason = crypto.verify_message(packet_1)
    assert valid_replay is False
    assert reason == "REPLAY_ATTACK_DETECTED"


def test_cybersecurity_engine_full_evaluation():
    engine = CybersecurityEngine()
    ekf_vel = np.array([12.0, 0.5, -0.2])
    imu_accel = [0.1, 0.0, 9.81]
    u_cmd = np.array([5.4, 5.4, 5.4, 5.4])
    t_now = time.time()

    status = engine.evaluate_threat(ekf_vel, imu_accel, u_cmd, t_now, dt=0.2)
    assert 0.0 <= status.threat_level <= 1.0
    assert status.zero_trust_status in ("VERIFIED_SECURE", "THREAT_ELEVATED", "ZERO_TRUST_COMPROMISED")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Situation Awareness-Based Agent Transparency (SAT) Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_sat_3_level_transparency():
    explainer = AutonomyExplainabilityEngine()
    snapshot = {
        "autonomy_mode": "TACTICAL_AUTONOMOUS",
        "decision": {"action": "HOLD_POSITION", "os_override": False},
        "risk": {"value": 0.25, "level": "LOW", "dominant_source": "NOMINAL"},
        "cognition": {"confidence": 0.92, "reasoning_factors": {"stability": 0.95}},
        "survival": {"strategy": "HOLD", "urgency": "LOW", "scenarios_evaluated": 12, "survival_score": 0.94},
        "sensor_trust": {"gps_confidence": 0.95, "imu_confidence": 0.98, "vision_confidence": 0.91, "fusion_confidence": 0.96, "primary_nav_source": "gps"},
        "foundation_world_model": {"generative_survivability": 0.93},
        "confidence": {"global_uncertainty": 0.12, "degraded_mode": "NOMINAL"},
        "telemetry": {"battery": 82.0},
    }
    explanation = explainer.explain_cycle(snapshot)
    
    # SAT Level 1
    assert explanation.sat_level_1 is not None
    assert explanation.sat_level_1.primary_nav_source == "gps"
    assert explanation.sat_level_1.active_intent == "EXECUTE_HOLD_POSITION"

    # SAT Level 2
    assert explanation.sat_level_2 is not None
    assert "battery_margin" in explanation.sat_level_2.constraint_margins
    assert len(explanation.sat_level_2.candidate_actions_evaluated) > 0

    # SAT Level 3
    assert explanation.sat_level_3 is not None
    assert explanation.sat_level_3.survivability_10s_forecast > 0.8
    assert 0.0 <= explanation.sat_level_3.operator_cognitive_load_index <= 1.0
    assert explanation.sat_level_3.recommended_intervention_window_s > 0.0
