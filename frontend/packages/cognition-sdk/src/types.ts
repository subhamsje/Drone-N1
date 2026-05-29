/** Cognition-native stream types — operational consciousness, not telemetry tables. */

export interface CognitionPose {
  position: number[];
  altitude_m: number;
  heading_deg: number;
  geo?: { lat: number; lon: number; source?: string };
  velocity_ned?: number[];
}

export interface CognitionMetrics {
  action?: string;
  preempt?: string;
  crash_probability: number;
  composite_survivability: number;
  global_uncertainty: number;
  gps_trust: number;
  vision_trust: number;
  reasoning_chain: string[];
  ai_trust_score: number;
}

export interface CognitionEnvelope {
  ts: number;
  uav_id: string;
  os_version?: string;
  cycle?: number;
  pose: CognitionPose;
  cognition: CognitionMetrics;
  world_model: Record<string, unknown>;
  survival: Record<string, unknown>;
  embodied: Record<string, unknown>;
  hardware?: Record<string, unknown>;
  swarm?: Record<string, unknown>;
  adversarial: Record<string, unknown>;
  trust?: Record<string, unknown>;
  airspace: Record<string, unknown>;
  certification: Record<string, unknown>;
  fleet_ops?: Record<string, unknown>;
  economics?: Record<string, unknown>;
  replay?: Record<string, unknown>;
  route_governance?: Record<string, unknown>;
  rt: Record<string, unknown>;
}

export interface StreamMessage {
  channel: string;
  data: CognitionEnvelope | Record<string, unknown>;
}
