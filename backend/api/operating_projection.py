"""Unified operating state — single frontend contract for Altaria OS."""

import os
import time
from typing import Any, Dict, List, Optional

from backend.api.cognition_projection import project_cognition_envelope

# Operational home (configurable via env for field ops)
HOME_LAT = float(os.getenv("ALTARIA_HOME_LAT", "12.9716"))
HOME_LON = float(os.getenv("ALTARIA_HOME_LON", "77.5946"))


def _ned_to_geo(position_ned: List[float]) -> Dict[str, float]:
    """Approximate NED meters → WGS84 offset from home."""
    if not position_ned or len(position_ned) < 2:
        return {"lat": HOME_LAT, "lon": HOME_LON}
    north_m, east_m = float(position_ned[0]), float(position_ned[1])
    lat = HOME_LAT + north_m / 111_320.0
    lon = HOME_LON + east_m / (111_320.0 * max(0.2, abs(__import__("math").cos(__import__("math").radians(HOME_LAT)))))
    return {"lat": round(lat, 7), "lon": round(lon, 7)}


def project_aircraft_snapshot(snapshot: Dict[str, Any], live_telemetry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    physics = snapshot.get("physics", {})
    nav = snapshot.get("navigation", {}) or {}
    trust = snapshot.get("sensor_trust", {}) or {}
    live = live_telemetry or {}

    if live.get("lat") is not None and live.get("lon") is not None:
        geo = {"lat": float(live["lat"]), "lon": float(live["lon"]), "source": "mavsdk"}
        alt_m = float(live.get("alt_m", physics.get("altitude", 10)))
        battery = float(live.get("battery_pct", physics.get("battery", 100)) / 100.0 if live.get("battery_pct", 0) > 1 else live.get("battery_pct", physics.get("battery", 0.85)))
    else:
        pos = nav.get("position_ned") or [0.0, 0.0, float(physics.get("altitude", 10))]
        geo = {**_ned_to_geo(pos), "source": "ned_home"}
        alt_m = float(physics.get("altitude", pos[2] if len(pos) > 2 else 10))
        battery = float(physics.get("battery", 85)) / 100.0 if float(physics.get("battery", 85)) > 1 else float(physics.get("battery", 0.85))

    return {
        "uav_id": snapshot.get("uav_id"),
        "connected": live.get("connected", live.get("mode") != "simulation"),
        "mode": live.get("mode", "cognitive"),
        "geo": geo,
        "altitude_m": alt_m,
        "heading_deg": float(nav.get("heading", 0)),
        "velocity_mps": float(nav.get("ground_speed", physics.get("speed", 0))),
        "battery_pct": battery,
        "gps_trust": float(trust.get("gps_confidence", 1)),
        "comm_trust": float(trust.get("comm_trust", 0.9)),
        "armed": live.get("armed", False),
    }


def project_survivability_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    inf = snapshot.get("inference", {}) or {}
    surv = snapshot.get("survival", {}) or {}
    ps = snapshot.get("probabilistic_safety", {}) or {}
    return {
        "crash_probability": float(inf.get("crash_probability", 0)),
        "composite_survivability": float(ps.get("composite_survivability", 0.5)),
        "mission_continuity": float(ps.get("mission_continuity", 0.7)),
        "landing_success_probability": float(surv.get("landing_success_probability", 0.8)),
        "recovery_success_probability": float(surv.get("recovery_success_probability", 1 - inf.get("crash_probability", 0))),
        "urgency": surv.get("urgency"),
        "strategy": surv.get("strategy"),
        "landing_zone": snapshot.get("landing_zone"),
        "recommended_actions": surv.get("recommended_actions", []),
    }


def project_world_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "forecast": snapshot.get("world_model"),
        "foundation": snapshot.get("foundation_world_model"),
        "world_cognition": snapshot.get("world_cognition"),
        "twin_physics": snapshot.get("twin_physics"),
    }


def project_mission_snapshot(
    snapshot: Dict[str, Any],
    intelligence_missions: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    fo = snapshot.get("flight_operations", {}) or snapshot.get("operational_intelligence", {})
    active = None
    if intelligence_missions:
        for m in intelligence_missions:
            if m.get("phase") not in ("learn", "replay"):
                active = m
                break
    return {
        "active_mission": active,
        "missions": intelligence_missions or [],
        "intent": snapshot.get("mission_intent"),
        "route_governance": snapshot.get("route_governance"),
        "flight_ops": fo,
        "replay": snapshot.get("mission_replay"),
    }


def project_fleet_snapshot(snapshot: Dict[str, Any], fleet_intel: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "fleet_id": snapshot.get("fleet_id"),
        "swarm": snapshot.get("collective_swarm") or snapshot.get("collective_intelligence") or snapshot.get("swarm"),
        "distributed_swarm": snapshot.get("distributed_swarm"),
        "fleet_learning": snapshot.get("fleet_learning"),
        "autonomous_operations": snapshot.get("autonomous_operations"),
        "intelligence": fleet_intel,
    }


def project_operating_state(
    snapshot: Dict[str, Any],
    *,
    intelligence_missions: Optional[List[Dict[str, Any]]] = None,
    fleet_intel: Optional[Dict[str, Any]] = None,
    live_telemetry: Optional[Dict[str, Any]] = None,
    geospatial: Optional[Dict[str, Any]] = None,
    analytics: Optional[Dict[str, Any]] = None,
    edge_status: Optional[Dict[str, Any]] = None,
    flight_stack: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Single source of truth for the command environment."""
    cognition = project_cognition_envelope(snapshot)
    aircraft = project_aircraft_snapshot(snapshot, live_telemetry)
    cognition["pose"]["geo"] = aircraft["geo"]
    cognition["pose"]["altitude_m"] = aircraft["altitude_m"]
    cognition["pose"]["heading_deg"] = aircraft["heading_deg"]

    return {
        "ts": time.time(),
        "uav_id": snapshot.get("uav_id"),
        "os_version": snapshot.get("os_version"),
        "cycle": snapshot.get("cycle"),
        "cognition": cognition,
        "aircraft": aircraft,
        "survivability": project_survivability_snapshot(snapshot),
        "world": project_world_snapshot(snapshot),
        "mission": project_mission_snapshot(snapshot, intelligence_missions),
        "fleet": project_fleet_snapshot(snapshot, fleet_intel),
        "geospatial": geospatial,
        "analytics": analytics,
        "edge": edge_status,
        "flight_stack": flight_stack,
        "recovery": {
            "active": snapshot.get("recovery_workflow"),
            "survival": snapshot.get("survival"),
        },
        "execution": snapshot.get("rt_execution"),
        "mlops": snapshot.get("inference"),
    }
