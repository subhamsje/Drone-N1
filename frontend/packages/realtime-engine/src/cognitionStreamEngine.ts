import type { CognitionEnvelope, OperatingState } from '@altaria/cognition-sdk';
import { Subject, Subscription, timer, Observable, throwError } from 'rxjs';
import { catchError, delayWhen, retryWhen, sampleTime, tap } from 'rxjs/operators';

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error' | 'reconnecting';

/** Survivability-first priority (lower = higher) */
export const StreamPriority = {
  SURVIVABILITY: 0,
  POSE: 1,
  RECOVERY: 2,
  TRUST: 3,
  WORLD: 4,
  SWARM: 5,
  ANALYTICS: 6,
} as const;

const CHANNEL_PRIORITY: Record<string, number> = {
  operating_state: StreamPriority.SURVIVABILITY,
  cognition: StreamPriority.SURVIVABILITY,
  all: StreamPriority.SURVIVABILITY,
  survival: StreamPriority.RECOVERY,
  trust: StreamPriority.TRUST,
  world_model: StreamPriority.WORLD,
  swarm: StreamPriority.SWARM,
  hardware: StreamPriority.ANALYTICS,
  adversarial: StreamPriority.ANALYTICS,
  airspace: StreamPriority.WORLD,
  certification: StreamPriority.ANALYTICS,
};

export interface FutureBranch {
  points: [number, number, number][];
  probability: number;
  survivability: number;
  label: string;
}

export interface TwinRenderState {
  survivability: number;
  thrustScale: number;
  turbulence: number;
  altitudeM: number;
  headingDeg: number;
  trajectory: [number, number, number][];
  branches: FutureBranch[];
  /** Worst-case predicted path */
  crashPath: [number, number, number][];
  landingPoint: [number, number, number];
  /** Survivability at prediction horizons */
  futureSurvivability: [number, number, number];
  branchWeights: [number, number, number];
  uncertainty: number;
  gpsUncertainty: number;
  visionUncertainty: number;
  crashRisk: number;
  recoveryProb: number;
  threatLevel: number;
  rfDenied: number;
  thermalLoad: number;
  motorStress: [number, number, number, number];
  swarmCoupling: number;
  action: string;
  uavId: string;
  osVersion: string;
}

export interface GlobeRenderState {
  lon: number;
  lat: number;
  altM: number;
  conflictRisk: number;
  congestion: number;
  threatLevel: number;
  rfDenied: number;
  uavId: string;
}

export interface CognitionRenderState {
  twin: TwinRenderState;
  globe: GlobeRenderState;
  revision: number;
}

const DEFAULT_TWIN: TwinRenderState = {
  survivability: 0.75,
  thrustScale: 1,
  turbulence: 0.15,
  altitudeM: 10,
  headingDeg: 0,
  trajectory: [[0, 0, 0], [0.5, 0.33, 0.5], [1, 0.5, 1], [1.5, 0.67, 1.8]],
  branches: [],
  crashPath: [[0, 0, 0], [0.8, 0.2, 0.6], [1.6, 0.1, 1.2]],
  landingPoint: [2, 0.05, 2],
  futureSurvivability: [0.75, 0.7, 0.65],
  branchWeights: [0.55, 0.3, 0.15],
  uncertainty: 0.3,
  gpsUncertainty: 0.1,
  visionUncertainty: 0.1,
  crashRisk: 0.1,
  recoveryProb: 0.8,
  threatLevel: 0,
  rfDenied: 0,
  thermalLoad: 0.2,
  motorStress: [0.1, 0.1, 0.1, 0.1],
  swarmCoupling: 0,
  action: 'NONE',
  uavId: '—',
  osVersion: '—',
};

const DEFAULT_GLOBE: GlobeRenderState = {
  lon: 77.5,
  lat: 12.9,
  altM: 30,
  conflictRisk: 0,
  congestion: 0,
  threatLevel: 0,
  rfDenied: 0,
  uavId: 'ALTARIA',
};

export interface StreamEngineStats {
  packetsReceived: number;
  packetsDropped: number;
  uiFlushHz: number;
  connection: ConnectionState;
  latencyMs: number;
}

export type UiFlushCallback = (
  envelope: CognitionEnvelope,
  stats: StreamEngineStats,
  operating?: OperatingState | null,
) => void;

export type OperatingStateCallback = (state: OperatingState, stats: StreamEngineStats) => void;

interface StreamMessage {
  channel: string;
  data: unknown;
  priority: number;
}

/**
 * Realtime cognition stream engine using RxJS — backpressure, batching, survivability-first.
 */
export class CognitionStreamEngine {
  readonly renderState: CognitionRenderState = {
    twin: { ...DEFAULT_TWIN },
    globe: { ...DEFAULT_GLOBE },
    revision: 0,
  };

  private url: string;
  private ws: WebSocket | null = null;
  private envelope: CognitionEnvelope | null = null;
  operatingState: OperatingState | null = null;

  private messageSubject = new Subject<StreamMessage>();
  private envelopeSubject = new Subject<CognitionEnvelope>();
  private operatingSubject = new Subject<OperatingState>();
  private subscription = new Subscription();

  private uiFlushMs: number;
  private onUiFlush: UiFlushCallback | null = null;
  private onOperating: OperatingStateCallback | null = null;
  private destroyed = false;

  stats: StreamEngineStats = {
    packetsReceived: 0,
    packetsDropped: 0,
    uiFlushHz: 12,
    connection: 'disconnected',
    latencyMs: 0,
  };

  constructor(url: string, uiFlushHz = 12) {
    this.url = url;
    this.uiFlushMs = 1000 / uiFlushHz;
    this.stats.uiFlushHz = uiFlushHz;

    // RxJS Pipeline for message processing
    this.subscription.add(
      this.messageSubject.pipe(
        tap((msg) => {
          this.stats.packetsReceived++;
          if (msg.channel === 'operating_state') {
            const op = msg.data as OperatingState;
            if (op?.cognition) {
              this.operatingState = op;
              this.envelope = op.cognition;
              this.applyRenderState(op.cognition, op.aircraft);
              this.operatingSubject.next(op);
            }
          } else if (msg.channel === 'cognition' || msg.channel === 'all') {
            const data = msg.data as CognitionEnvelope;
            if (data?.cognition) {
              this.envelope = data;
              this.applyRenderState(data);
            }
          } else if (this.envelope && msg.data && typeof msg.data === 'object') {
            this.patchEnvelope(msg.channel, msg.data as Record<string, unknown>);
            this.applyRenderState(this.envelope);
          }
          if (this.envelope) {
            this.envelopeSubject.next(this.envelope);
          }
        })
      ).subscribe()
    );

    // RxJS Pipeline for UI Flushes (sampleTime for backpressure)
    this.subscription.add(
      this.envelopeSubject.pipe(
        sampleTime(this.uiFlushMs)
      ).subscribe((env) => {
        if (this.onUiFlush && !this.destroyed) {
          this.onUiFlush(env, { ...this.stats }, this.operatingState);
        }
      })
    );

    this.subscription.add(
      this.operatingSubject.pipe(sampleTime(this.uiFlushMs)).subscribe((op) => {
        if (this.onOperating && !this.destroyed) {
          this.onOperating(op, { ...this.stats });
        }
      }),
    );
  }

  setUiFlushCallback(cb: UiFlushCallback | null): void {
    this.onUiFlush = cb;
  }

  setOperatingCallback(cb: OperatingStateCallback | null): void {
    this.onOperating = cb;
  }

  connect(): void {
    if (this.destroyed) return;
    if (this.ws?.readyState === WebSocket.OPEN || this.ws?.readyState === WebSocket.CONNECTING) return;
    this.openSocketWithRetry();
  }

  destroy(): void {
    this.destroyed = true;
    this.subscription.unsubscribe();
    this.ws?.close();
    this.ws = null;
  }

  private openSocketWithRetry(): void {
    let reconnectAttempts = 0;
    
    const connectObservable = new Observable<WebSocket>((observer) => {
      this.stats.connection = reconnectAttempts > 0 ? 'reconnecting' : 'connecting';
      const ws = new WebSocket(this.url);
      
      ws.onopen = () => {
        reconnectAttempts = 0;
        this.stats.connection = 'connected';
        ws.send(
          JSON.stringify({
            subscribe: [
              'operating_state',
              'cognition',
              'all',
              'survival',
              'world_model',
              'swarm',
              'trust',
              'hardware',
              'adversarial',
              'airspace',
              'certification',
            ],
          }),
        );
        observer.next(ws);
      };

      ws.onmessage = (ev) => {
        const t0 = performance.now();
        try {
          const msg = JSON.parse(ev.data as string) as { channel: string; data: unknown };
          const priority = CHANNEL_PRIORITY[msg.channel] ?? StreamPriority.ANALYTICS;
          this.messageSubject.next({ channel: msg.channel, data: msg.data, priority });
        } catch {
          this.stats.packetsDropped++;
        }
        this.stats.latencyMs = performance.now() - t0;
      };

      ws.onclose = () => {
        this.stats.connection = 'disconnected';
        observer.error(new Error('WebSocket closed'));
      };

      ws.onerror = (err) => {
        this.stats.connection = 'error';
        observer.error(err);
      };

      this.ws = ws;

      return () => ws.close();
    });

    this.subscription.add(
      connectObservable.pipe(
        retryWhen(errors =>
          errors.pipe(
            tap(() => reconnectAttempts++),
            delayWhen(() => timer(Math.min(30000, 1000 * Math.pow(2, reconnectAttempts))))
          )
        )
      ).subscribe()
    );
  }

  private patchEnvelope(channel: string, data: Record<string, unknown>): void {
    if (!this.envelope) return;
    const e = this.envelope as unknown as Record<string, unknown>;
    if (channel === 'survival') Object.assign(e, { survival: data });
    else if (channel === 'world_model') e.world_model = { ...(e.world_model as object), ...data };
    else if (channel === 'swarm') e.swarm = data;
    else if (channel === 'trust') e.trust = data;
    else if (channel === 'hardware') e.hardware = data;
    else if (channel === 'adversarial') e.adversarial = data;
    else if (channel === 'airspace') e.airspace = data;
    else if (channel === 'certification') e.certification = data;
  }

  applyLiveAircraft(geo: { lat: number; lon: number }, altM: number, headingDeg?: number): void {
    const g = this.renderState.globe;
    g.lon = geo.lon;
    g.lat = geo.lat;
    g.altM = altM;
    if (headingDeg !== undefined) {
      this.renderState.twin.headingDeg = headingDeg;
    }
    this.renderState.revision += 1;
  }

  private applyRenderState(env: CognitionEnvelope, aircraft?: { geo?: { lat: number; lon: number }; altitude_m?: number; heading_deg?: number }): void {
    const t = this.renderState.twin;
    const g = this.renderState.globe;
    t.survivability = env.cognition.composite_survivability;
    t.crashRisk = env.cognition.crash_probability;
    t.action = env.cognition.action ?? 'NONE';
    t.uncertainty = Number(
      (env.world_model?.uncertainty as { composite_uncertainty?: number })?.composite_uncertainty ?? 0.3,
    );
    const learning = env.embodied?.learning as { thrust_scale?: number } | undefined;
    t.thrustScale = Number(learning?.thrust_scale ?? 1);
    const nodes = (env.world_model?.forecast as { nodes?: Array<{ state_key: string; probability: number }> })
      ?.nodes;
    t.turbulence = Number(nodes?.find((n) => n.state_key === 'turbulence_propagation')?.probability ?? 0.15);
    t.altitudeM = env.pose?.altitude_m ?? 10;
    t.headingDeg = env.pose?.heading_deg ?? 0;
    t.gpsUncertainty = 1 - (env.cognition.gps_trust ?? 0.9);
    t.visionUncertainty = 1 - (env.cognition.vision_trust ?? 0.9);
    t.uavId = env.uav_id ?? '—';
    t.osVersion = env.os_version ?? '—';
    const survival = env.survival as Record<string, unknown> | undefined;
    t.recoveryProb = Number(survival?.recovery_success_probability ?? 1 - t.crashRisk);
    t.thermalLoad = Number((env.hardware as Record<string, number>)?.thermal_fatigue_index ?? 0.2);
    const adv = env.adversarial as Record<string, number> | undefined;
    t.threatLevel = Number(adv?.attack_confidence ?? adv?.gps_spoofing_index ?? 0);
    t.rfDenied = Number(adv?.rf_jamming_index ?? adv?.telemetry_poisoning_index ?? 0);
    const hw = env.hardware as Record<string, number> | undefined;
    const baseWear = Number(hw?.motor_degradation_index ?? 0.15);
    t.motorStress = [
      Number(hw?.motor_0_wear ?? baseWear),
      Number(hw?.motor_1_wear ?? baseWear * 1.05),
      Number(hw?.motor_2_wear ?? baseWear * 0.95),
      Number(hw?.motor_3_wear ?? baseWear * 1.1),
    ];
    const graph = env.swarm?.cognition_graph as { edges?: Array<{ risk_coupling: number }> } | undefined;
    const couplings = graph?.edges?.map((e) => e.risk_coupling) ?? [];
    t.swarmCoupling = couplings.length
      ? couplings.reduce((a, b) => a + b, 0) / couplings.length
      : 0;
    const alt = t.altitudeM;
    t.trajectory = [
      [0, 0, 0],
      [0.5, alt / 30, 0.5],
      [1, alt / 20, 1],
      [1.5, alt / 15, 1.8],
    ];
    const spread = 0.35 + t.uncertainty * 0.8;
    const foundation = env.world_model?.foundation as { generative_survivability?: number } | undefined;
    const genSurv = Number(foundation?.generative_survivability ?? t.survivability);
    const b0 = t.trajectory;
    const b1 = t.trajectory.map(
      ([x, y, z]) => [x + spread, y * (1 + t.turbulence * 0.3), z + spread * 0.5] as [number, number, number],
    );
    const b2 = t.trajectory.map(
      ([x, y, z]) => [x - spread * 0.7, y * (0.5 + t.crashRisk), z - spread * 0.4] as [number, number, number],
    );
    const w0 = Math.max(0.1, t.survivability);
    const w1 = Math.max(0.08, 0.35 * (1 - t.uncertainty));
    const w2 = Math.max(0.05, t.crashRisk + t.uncertainty * 0.25);
    const wSum = w0 + w1 + w2;
    t.branchWeights = [w0 / wSum, w1 / wSum, w2 / wSum];
    t.futureSurvivability = [
      t.survivability,
      lerpScalar(t.survivability, genSurv, 0.5),
      lerpScalar(t.survivability, genSurv * (1 - t.crashRisk * 0.5), 0.35),
    ];
    t.branches = [
      { points: b0, probability: t.branchWeights[0], survivability: t.futureSurvivability[0], label: 'OPTIMAL' },
      { points: b1, probability: t.branchWeights[1], survivability: t.futureSurvivability[1], label: 'TURBULENT' },
      { points: b2, probability: t.branchWeights[2], survivability: t.futureSurvivability[2], label: 'ADVERSARIAL' },
    ];
    t.crashPath = b2;
    const last = b0[b0.length - 1] ?? [2, 0, 2];
    t.landingPoint = [last[0] + 0.5, 0.05, last[2] + 0.5];

    g.altM = alt;
    g.uavId = env.uav_id ?? 'ALTARIA';
    if (aircraft?.geo?.lat != null && aircraft?.geo?.lon != null) {
      g.lat = aircraft.geo.lat;
      g.lon = aircraft.geo.lon;
      if (aircraft.altitude_m != null) g.altM = aircraft.altitude_m;
    } else {
      const geoPose = (env.pose as { geo?: { lat: number; lon: number } })?.geo;
      if (geoPose?.lat != null && geoPose?.lon != null) {
        g.lat = geoPose.lat;
        g.lon = geoPose.lon;
      }
    }
    g.conflictRisk = Number((env.airspace?.state as { conflict_risk?: number })?.conflict_risk ?? 0);
    g.congestion = Number(
      (env.airspace?.planetary as { global_congestion?: number })?.global_congestion ?? 0,
    );
    g.threatLevel = t.threatLevel;
    g.rfDenied = t.rfDenied;
    this.renderState.revision += 1;
  }
}

function lerpScalar(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

let sharedEngine: CognitionStreamEngine | null = null;

export function getCognitionStreamEngine(url: string): CognitionStreamEngine {
  if (!sharedEngine) sharedEngine = new CognitionStreamEngine(url);
  return sharedEngine;
}

export function resetCognitionStreamEngine(): void {
  sharedEngine?.destroy();
  sharedEngine = null;
}
