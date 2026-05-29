/** Unified Altaria operating state — single frontend contract. */

import type { CognitionEnvelope } from './types';

export interface GeoPosition {
  lat: number;
  lon: number;
  source?: string;
}

export interface AircraftSnapshot {
  uav_id?: string;
  connected?: boolean;
  mode?: string;
  geo: GeoPosition;
  altitude_m: number;
  heading_deg: number;
  velocity_mps: number;
  battery_pct: number;
  gps_trust: number;
  comm_trust: number;
  armed?: boolean;
}

export interface SurvivabilitySnapshot {
  crash_probability: number;
  composite_survivability: number;
  mission_continuity: number;
  landing_success_probability: number;
  recovery_success_probability: number;
  urgency?: string;
  strategy?: string;
  landing_zone?: unknown;
  recommended_actions?: unknown[];
}

export interface MissionSnapshot {
  active_mission?: {
    mission_id: string;
    phase: string;
    intent: string;
    plan?: Record<string, unknown>;
    validation?: { passed?: boolean };
  } | null;
  missions: Array<Record<string, unknown>>;
  intent?: string;
  route_governance?: Record<string, unknown>;
  flight_ops?: Record<string, unknown>;
  replay?: Record<string, unknown>;
}

export interface FleetSnapshot {
  fleet_id?: string;
  swarm?: Record<string, unknown>;
  distributed_swarm?: Record<string, unknown>;
  fleet_learning?: Record<string, unknown>;
  autonomous_operations?: Record<string, unknown>;
  intelligence?: Record<string, unknown>;
}

export interface WorldSnapshot {
  forecast?: Record<string, unknown>;
  foundation?: Record<string, unknown>;
  world_cognition?: Record<string, unknown>;
  twin_physics?: Record<string, unknown>;
}

export interface OperatingState {
  ts: number;
  uav_id: string;
  os_version?: string;
  cycle?: number;
  cognition: CognitionEnvelope;
  aircraft: AircraftSnapshot;
  survivability: SurvivabilitySnapshot;
  world: WorldSnapshot;
  mission: MissionSnapshot;
  fleet: FleetSnapshot;
  geospatial?: Record<string, unknown>;
  analytics?: Record<string, unknown>;
  edge?: Record<string, unknown>;
  flight_stack?: Record<string, unknown>;
  recovery?: Record<string, unknown>;
  execution?: Record<string, unknown>;
  mlops?: Record<string, unknown>;
}

export interface PlatformPollStatus {
  execution?: Record<string, unknown>;
  intelligence?: Record<string, unknown>;
  edge?: Record<string, unknown>;
  mlops?: Record<string, unknown>;
}
