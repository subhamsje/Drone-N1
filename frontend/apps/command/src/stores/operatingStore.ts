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
  activeTenant: string;
  analyticsOverlayOpen: boolean;
  applyOperating: (op: OperatingState, stats: StreamEngineStats) => void;
  applyEnvelopeFlush: (env: CognitionEnvelope, stats: StreamEngineStats, op?: OperatingState | null) => void;
  setPlatform: (p: Partial<PlatformPollStatus>) => void;
  setActiveMissionId: (id: string | null) => void;
  setCommandTab: (tab: string) => void;
  setActiveTenant: (tenant: string) => void;
  setAnalyticsOverlayOpen: (open: boolean) => void;
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
  activeTenant: 'default-fleet',
  analyticsOverlayOpen: false,

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

  setPlatform: (p) => {
    const prev = get().platform;
    const next = { ...prev };
    if (p.execution) next.execution = { ...(prev.execution || {}), ...p.execution };
    if (p.intelligence) next.intelligence = { ...(prev.intelligence || {}), ...p.intelligence };
    if (p.edge) next.edge = { ...(prev.edge || {}), ...p.edge };
    if (p.mlops) next.mlops = { ...(prev.mlops || {}), ...p.mlops };
    set({ platform: next });
  },
  setActiveMissionId: (activeMissionId) => set({ activeMissionId }),
  setCommandTab: (commandTab) => set({ commandTab }),
  setActiveTenant: (activeTenant) => set({ activeTenant }),
  setAnalyticsOverlayOpen: (analyticsOverlayOpen) => set({ analyticsOverlayOpen }),
}));
