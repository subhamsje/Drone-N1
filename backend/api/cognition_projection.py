"""Project OS snapshots into cognition-native streams for the command environment."""

import time
from typing import Any, Dict


def project_cognition_envelope(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Operational consciousness layer — not raw telemetry."""
    physics = snapshot.get("physics", {})
    nav = snapshot.get("navigation", {}) or {}
    pos = nav.get("position_ned") or [0, 0, float(physics.get("altitude", 10))]

    return {
        "ts": time.time(),
        "uav_id": snapshot.get("uav_id"),
        "os_version": snapshot.get("os_version"),
        "cycle": snapshot.get("cycle"),
        "pose": {
            "position": pos,
            "altitude_m": float(physics.get("altitude", 10)),
            "heading_deg": float(nav.get("heading", 0)),
        },
        "cognition": {
            "action": snapshot.get("decision", {}).get("action"),
            "preempt": snapshot.get("decision", {}).get("world_model_preempt"),
            "crash_probability": float(snapshot.get("inference", {}).get("crash_probability", 0)),
            "composite_survivability": float(
                snapshot.get("probabilistic_safety", {}).get("composite_survivability", 0)
            ),
            "global_uncertainty": float(snapshot.get("confidence", {}).get("global_uncertainty", 0)),
            "gps_trust": float(snapshot.get("sensor_trust", {}).get("gps_confidence", 1)),
            "vision_trust": float(snapshot.get("sensor_trust", {}).get("vision_confidence", 1)),
            "reasoning_chain": snapshot.get("explanation", {}).get("reasoning_chain", []),
            "ai_trust_score": float(snapshot.get("explanation", {}).get("ai_trust_score", 0)),
        },
        "world_model": {
            "forecast": snapshot.get("world_model"),
            "foundation": snapshot.get("foundation_world_model"),
            "uncertainty": snapshot.get("world_cognition", {}).get("uncertainty"),
            "future_graph": snapshot.get("world_cognition", {}).get("future_graph"),
        },
        "survival": {
            "urgency": snapshot.get("survival", {}).get("urgency"),
            "strategy": snapshot.get("survival", {}).get("strategy"),
            "landing_zone": snapshot.get("landing_zone"),
            "probabilistic_escalation": snapshot.get("probabilistic_escalation"),
        },
        "embodied": {
            "cognition": snapshot.get("embodied_cognition"),
            "learning": snapshot.get("embodied_learning"),
            "evolution": snapshot.get("embodied_evolution"),
        },
        "hardware": snapshot.get("hardware_cognition"),
        "swarm": snapshot.get("collective_swarm") or snapshot.get("collective_intelligence"),
        "adversarial": {
            "operations": snapshot.get("adversarial_operations"),
            "adaptive": snapshot.get("adaptive_adversarial"),
            "perception": snapshot.get("adversarial_perception"),
            "cyber": snapshot.get("cyber_warfare"),
        },
        "trust": snapshot.get("operational_trust"),
        "airspace": {
            "state": snapshot.get("airspace"),
            "traffic": snapshot.get("airspace_traffic"),
            "planetary": snapshot.get("planetary_airspace"),
        },
        "route_governance": snapshot.get("route_governance"),
        "certification": {
            "operational": snapshot.get("operational_certification"),
            "evidence_dag": snapshot.get("mission_evidence_dag"),
            "formal": snapshot.get("formal_certification"),
        },
        "fleet_ops": snapshot.get("autonomous_operations"),
        "economics": snapshot.get("operational_economics"),
        "replay": snapshot.get("mission_replay"),
        "rt": {
            "critical_path_ms": snapshot.get("rt_execution", {}).get("critical_path_ms"),
            "mixed_criticality": snapshot.get("mixed_criticality"),
        },
    }


def project_channel_payloads(snapshot: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    env = project_cognition_envelope(snapshot)
    return {
        "cognition": env,
        "survival": {"ts": env["ts"], "uav_id": env["uav_id"], **env["survival"], "cognition": env["cognition"]},
        "world_model": {"ts": env["ts"], "uav_id": env["uav_id"], **env["world_model"]},
        "swarm": {"ts": env["ts"], "uav_id": env["uav_id"], "swarm": env["swarm"]},
        "trust": {"ts": env["ts"], "uav_id": env["uav_id"], **env["trust"]} if env.get("trust") else {},
        "hardware": {"ts": env["ts"], "uav_id": env["uav_id"], **env["hardware"]} if env.get("hardware") else {},
        "adversarial": {"ts": env["ts"], "uav_id": env["uav_id"], **env["adversarial"]},
        "airspace": {"ts": env["ts"], "uav_id": env["uav_id"], **env["airspace"]},
        "certification": {"ts": env["ts"], "uav_id": env["uav_id"], **env["certification"]},
    }
