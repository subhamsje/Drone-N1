import { create } from 'zustand';
import type {
  OperatingState,
  PlatformPollStatus,
  CognitionEnvelope,
} from '@altaria/cognition-sdk';
import type { StreamEngineStats } from '@altaria/realtime-engine';

interface OperatingStoreState {
  operating: OperatingState | null;
  envelope: CognitionEnvelope | null;
  platform: PlatformPollStatus;
  uiVersion: number;
  stream: StreamEngineStats;
  activeMissionId: string | null;
  commandTab: string;
  applyOperating: (op: OperatingState, stats: StreamEngineStats) => void;
  applyEnvelopeFlush: (env: CognitionEnvelope, stats: StreamEngineStats, op?: OperatingState | null) => void;
  setPlatform: (p: Partial<PlatformPollStatus>) => void;
  setActiveMissionId: (id: string | null) => void;
  setCommandTab: (tab: string) => void;
}

const defaultStream: StreamEngineStats = {
  packetsReceived: 0,
  packetsDropped: 0,
  uiFlushHz: 12,
  connection: 'disconnected',
  latencyMs: 0,
};

export const useOperatingStore = create<OperatingStoreState>((set, get) => ({
  operating: null,
  envelope: null,
  platform: {},
  uiVersion: 0,
  stream: defaultStream,
  activeMissionId: null,
  commandTab: 'mission',

  applyOperating: (op, stats) => {
    const mid = op.mission?.active_mission?.mission_id ?? get().activeMissionId;
    set({
      operating: op,
      envelope: op.cognition,
      stream: stats,
      activeMissionId: mid,
      uiVersion: get().uiVersion + 1,
    });
  },

  applyEnvelopeFlush: (env, stats, op) => {
    set({
      envelope: env,
      operating: op ?? get().operating,
      stream: stats,
      uiVersion: get().uiVersion + 1,
    });
  },

  setPlatform: (p) => set({ platform: { ...get().platform, ...p } }),
  setActiveMissionId: (activeMissionId) => set({ activeMissionId }),
  setCommandTab: (commandTab) => set({ commandTab }),
}));
