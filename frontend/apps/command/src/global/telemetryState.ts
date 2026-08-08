import { create } from 'zustand';
import { wsManager } from '../services/websocket/wsManager';

export interface TelemetryState {
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
  connected: boolean;
  updateTelemetry: (partial: Partial<TelemetryState>) => void;
  initStream: () => () => void;
}

export const useTelemetryStore = create<TelemetryState>((set, get) => ({
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
  connected: true,

  updateTelemetry: (partial) => set((state) => ({ ...state, ...partial })),

  initStream: () => {
    const unsub = wsManager.subscribe('telemetry', (data: any) => {
      set((state) => ({
        ...state,
        altitudeM: typeof data.altitude_m === 'number' ? data.altitude_m : state.altitudeM,
        airspeedMs: typeof data.airspeed_ms === 'number' ? data.airspeed_ms : state.airspeedMs,
        headingDeg: typeof data.heading_deg === 'number' ? data.heading_deg : state.headingDeg,
        pitchDeg: typeof data.pitch_deg === 'number' ? data.pitch_deg : state.pitchDeg,
        rollDeg: typeof data.roll_deg === 'number' ? data.roll_deg : state.rollDeg,
        batteryPct: typeof data.battery_pct === 'number' ? data.battery_pct : state.batteryPct,
        batteryVolts: typeof data.battery_volts === 'number' ? data.battery_volts : state.batteryVolts,
        gpsSats: typeof data.gps_sats === 'number' ? data.gps_sats : state.gpsSats,
        rssiDbm: typeof data.rssi_dbm === 'number' ? data.rssi_dbm : state.rssiDbm,
        latencyMs: typeof data.latency_ms === 'number' ? data.latency_ms : state.latencyMs,
        motors: data.motors ? { ...state.motors, ...data.motors } : state.motors,
        connected: true,
      }));
    });
    return unsub;
  },
}));
