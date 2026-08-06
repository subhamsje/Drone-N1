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
  workspaceMode: 'ops_center' | 'command_globe' | 'mission_studio' | 'twin_workbench';
  opticMode: 'satellite' | 'tactical' | 'thermal' | 'nightvision' | 'wireframe';
  ctrlKOpen: boolean;
  fpvExpanded: boolean;
  activeIncidentModal: boolean;
  debriefModal: boolean;
  focusedUavId: string | null;
  sensorTrust: { gps: number; vio: number; baro: number; imu: number };
  confidence: { nav: number; vision: number; weather: number; battery: number; loc: number };
  replayFrames: Array<{ 
    ts: number; 
    surv: number; 
    action: string; 
    pose?: { geo?: { lat: number; lon: number }; altitude_m: number; heading_deg: number } 
  }>;
  applyUiFlush: (envelope: CognitionEnvelope, stats: StreamEngineStats) => void;
  setConnection: (s: string) => void;
  setDegraded: (d: boolean) => void;
  setViewMode: (m: 'planet' | 'twin' | 'dual') => void;
  setWorkspaceMode: (w: 'ops_center' | 'command_globe' | 'mission_studio' | 'twin_workbench') => void;
  setOpticMode: (o: 'satellite' | 'tactical' | 'thermal' | 'nightvision' | 'wireframe') => void;
  setCtrlKOpen: (open: boolean) => void;
  setFpvExpanded: (exp: boolean) => void;
  setActiveIncidentModal: (open: boolean) => void;
  setDebriefModal: (open: boolean) => void;
  setFocusedUavId: (id: string | null) => void;
}

export const useCognitionStore = create<CognitionState>((set, get) => ({
  envelope: null,
  uiVersion: 0,
  connection: 'disconnected',
  latencyMs: 0,
  packetsDropped: 0,
  degraded: false,
  viewMode: 'planet',
  workspaceMode: 'ops_center',
  opticMode: 'satellite',
  ctrlKOpen: false,
  fpvExpanded: false,
  activeIncidentModal: false,
  debriefModal: false,
  focusedUavId: null,
  sensorTrust: { gps: 98.4, vio: 94.2, baro: 96.8, imu: 99.1 },
  confidence: { nav: 98, vision: 93, weather: 86, battery: 95, loc: 91 },
  replayFrames: [],

  applyUiFlush: (envelope, stats) => {
    const prev = get().replayFrames;
    let replayFrames = prev;
    if (envelope.replay?.frames) {
      replayFrames = (
        envelope.replay.frames as Array<{ timestamp: number; survivability: number; action: string, pose: any }>
      ).map((f) => ({ 
        ts: f.timestamp, 
        surv: f.survivability, 
        action: f.action, 
        pose: f.pose 
      }));
    } else {
      replayFrames = [
        ...prev,
        {
          ts: envelope.ts,
          surv: envelope.cognition.composite_survivability,
          action: envelope.cognition.action ?? 'NONE',
          pose: { 
            geo: envelope.pose.geo, 
            altitude_m: envelope.pose.altitude_m, 
            heading_deg: envelope.pose.heading_deg 
          },
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
  setWorkspaceMode: (workspaceMode) => set({ workspaceMode }),
  setOpticMode: (opticMode) => set({ opticMode }),
  setCtrlKOpen: (ctrlKOpen) => set({ ctrlKOpen }),
  setFpvExpanded: (fpvExpanded) => set({ fpvExpanded }),
  setActiveIncidentModal: (activeIncidentModal) => set({ activeIncidentModal }),
  setDebriefModal: (debriefModal) => set({ debriefModal }),
  setFocusedUavId: (focusedUavId) => set({ focusedUavId }),
}));
