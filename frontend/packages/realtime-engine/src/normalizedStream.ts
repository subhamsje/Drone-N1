/**
 * Backpressure-Safe Normalized Telemetry & Event Stream.
 * Features 3-tier channel prioritization, 16ms (60fps) batching, and event deduplication.
 */

export type ChannelPriority = 'CRITICAL' | 'HIGH' | 'LOW';

export interface TelemetryFrame {
  timestamp: number;
  altitudeM: number;
  airspeedMs: number;
  headingDeg: number;
  pitchDeg: number;
  rollDeg: number;
  batteryPct: number;
  batteryVolts: number;
  gpsSats: number;
  rssiDbm: number;
  latencyMs: number;
  motors: {
    m1: number;
    m2: number;
    m3: number;
    m4: number;
  };
}

export type FrameListener = (frame: TelemetryFrame) => void;

class NormalizedStreamEngine {
  private listeners: Set<FrameListener> = new Set();
  private pendingCriticalFrame: Partial<TelemetryFrame> | null = null;
  private pendingHighEvents: any[] = [];
  private pendingLowLogs: any[] = [];
  private rafHandle: number | null = null;
  private lastFrameTimestamp = 0;
  private frameIntervalMs = 16.67; // 60 FPS Sync

  // Current consolidated state snapshot
  private currentFrame: TelemetryFrame = {
    timestamp: Date.now(),
    altitudeM: 48.5,
    airspeedMs: 14.8,
    headingDeg: 42,
    pitchDeg: -3.2,
    rollDeg: 4.5,
    batteryPct: 94,
    batteryVolts: 15.8,
    gpsSats: 19,
    rssiDbm: -44,
    latencyMs: 12.4,
    motors: { m1: 5820, m2: 5815, m3: 5840, m4: 5810 },
  };

  constructor() {
    this.startBatchingLoop();
  }

  /** Ingest raw data packet into prioritized backpressure buffer */
  public push(priority: ChannelPriority, payload: any) {
    if (priority === 'CRITICAL') {
      // Critical (attitude/telemetry): overwrite latest values (deduplication)
      this.pendingCriticalFrame = {
        ...this.pendingCriticalFrame,
        altitudeM: typeof payload.altitude_m === 'number' ? payload.altitude_m : payload.altitudeM,
        airspeedMs: typeof payload.airspeed_ms === 'number' ? payload.airspeed_ms : payload.airspeedMs,
        headingDeg: typeof payload.heading_deg === 'number' ? payload.heading_deg : payload.headingDeg,
        pitchDeg: typeof payload.pitch_deg === 'number' ? payload.pitch_deg : payload.pitchDeg,
        rollDeg: typeof payload.roll_deg === 'number' ? payload.roll_deg : payload.rollDeg,
        batteryPct: typeof payload.battery_pct === 'number' ? payload.battery_pct : payload.batteryPct,
        batteryVolts: typeof payload.battery_volts === 'number' ? payload.battery_volts : payload.batteryVolts,
        gpsSats: typeof payload.gps_sats === 'number' ? payload.gps_sats : payload.gpsSats,
        rssiDbm: typeof payload.rssi_dbm === 'number' ? payload.rssi_dbm : payload.rssiDbm,
        latencyMs: typeof payload.latency_ms === 'number' ? payload.latency_ms : payload.latencyMs,
        motors: payload.motors ? { ...payload.motors } : undefined,
      };
    } else if (priority === 'HIGH') {
      // High (AI survivability / alerts): buffer up to 10 max
      this.pendingHighEvents.push(payload);
      if (this.pendingHighEvents.length > 10) this.pendingHighEvents.shift();
    } else {
      // Low (Informational logs): buffer up to 20 max
      this.pendingLowLogs.push(payload);
      if (this.pendingLowLogs.length > 20) this.pendingLowLogs.shift();
    }
  }

  private startBatchingLoop() {
    const tick = (now: number) => {
      if (now - this.lastFrameTimestamp >= this.frameIntervalMs) {
        this.flushBatch();
        this.lastFrameTimestamp = now;
      }
      this.rafHandle = requestAnimationFrame(tick);
    };
    this.rafHandle = requestAnimationFrame(tick);
  }

  private flushBatch() {
    if (!this.pendingCriticalFrame) return;

    // Apply pending critical updates onto current state snapshot
    this.currentFrame = {
      ...this.currentFrame,
      ...this.pendingCriticalFrame,
      motors: this.pendingCriticalFrame.motors
        ? { ...this.currentFrame.motors, ...this.pendingCriticalFrame.motors }
        : this.currentFrame.motors,
      timestamp: Date.now(),
    };
    this.pendingCriticalFrame = null;

    // Dispatch single synchronized frame to all UI subscribers
    this.listeners.forEach((listener) => {
      try {
        listener(this.currentFrame);
      } catch (err) {
        console.error('[NormalizedStreamEngine] Subscriber dispatch error:', err);
      }
    });
  }

  public subscribe(listener: FrameListener): () => void {
    this.listeners.add(listener);
    // Send immediate initial frame
    listener(this.currentFrame);

    return () => {
      this.listeners.delete(listener);
    };
  }

  public getCurrentSnapshot(): TelemetryFrame {
    return { ...this.currentFrame };
  }
}

export const normalizedStream = new NormalizedStreamEngine();
