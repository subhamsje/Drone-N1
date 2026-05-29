import { create } from 'zustand';
import type { CognitionEnvelope } from '@altaria/cognition-sdk';
import type { StreamEngineStats } from '@altaria/realtime-engine';

interface CognitionState {
  envelope: CognitionEnvelope | null;
  uiVersion: number;
  connection: string;
  latencyMs: number;
  packetsDropped: number;
  degraded: boolean;
  viewMode: 'planet' | 'twin' | 'dual';
  replayFrames: Array<{ ts: number; surv: number; action: string }>;
  applyUiFlush: (envelope: CognitionEnvelope, stats: StreamEngineStats) => void;
  setConnection: (s: string) => void;
  setDegraded: (d: boolean) => void;
  setViewMode: (m: 'planet' | 'twin' | 'dual') => void;
}

export const useCognitionStore = create<CognitionState>((set, get) => ({
  envelope: null,
  uiVersion: 0,
  connection: 'disconnected',
  latencyMs: 0,
  packetsDropped: 0,
  degraded: false,
  viewMode: 'planet',
  replayFrames: [],

  applyUiFlush: (envelope, stats) => {
    const prev = get().replayFrames;
    let replayFrames = prev;
    if (envelope.replay?.frames) {
      replayFrames = (
        envelope.replay.frames as Array<{ timestamp: number; survivability: number; action: string }>
      ).map((f) => ({ ts: f.timestamp, surv: f.survivability, action: f.action }));
    } else {
      replayFrames = [
        ...prev,
        {
          ts: envelope.ts,
          surv: envelope.cognition.composite_survivability,
          action: envelope.cognition.action ?? 'NONE',
        },
      ].slice(-120);
    }
    set({
      envelope,
      uiVersion: get().uiVersion + 1,
      connection: stats.connection,
      latencyMs: stats.latencyMs,
      packetsDropped: stats.packetsDropped,
      replayFrames,
    });
  },

  setConnection: (connection) => set({ connection }),
  setDegraded: (degraded) => set({ degraded }),
  setViewMode: (viewMode) => set({ viewMode }),
}));
