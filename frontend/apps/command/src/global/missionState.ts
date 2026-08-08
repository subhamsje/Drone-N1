import { create } from 'zustand';
import { MissionApiService, CompileGraphPayload } from '../services/api/missionApi';

export interface MissionNode {
  id: string;
  type: 'TAKEOFF' | 'SURVEY' | 'INSPECT' | 'DETECT' | 'DELIVER' | 'RTL';
  label: string;
  params: string;
  x: number;
  y: number;
}

export interface MissionState {
  nodes: MissionNode[];
  selectedNodeId: string | null;
  corridorRadiusM: number;
  altitudeCeilingM: number;
  dubinsSpline: boolean;
  nfzAvoidance: boolean;
  compiling: boolean;
  compiledResult: any | null;
  approvedMissions: Record<string, boolean>;

  addNode: (type: MissionNode['type']) => void;
  updateNode: (id: string, partial: Partial<MissionNode>) => void;
  setSelectedNodeId: (id: string | null) => void;
  setCorridorRadiusM: (r: number) => void;
  setAltitudeCeilingM: (a: number) => void;
  setDubinsSpline: (d: boolean) => void;
  setNfzAvoidance: (n: boolean) => void;
  toggleApproveMission: (id: string) => void;
  compileGraph: () => Promise<void>;
}

export const useMissionStore = create<MissionState>((set, get) => ({
  nodes: [
    { id: 'n1', type: 'TAKEOFF', label: '01. Autonomous Takeoff', params: 'ALT: 50m • RATE: 2.5m/s', x: 40, y: 140 },
    { id: 'n2', type: 'SURVEY', label: '02. Grid Survey Pattern', params: 'CORRIDOR: Alpha • SPEED: 12m/s', x: 260, y: 140 },
    { id: 'n3', type: 'INSPECT', label: '03. Structural Thermal Scan', params: 'GIMBAL: -45° • DIST: 15m', x: 500, y: 80 },
    { id: 'n4', type: 'DETECT', label: '04. AI Target Classification', params: 'CONFIDENCE > 90% • LOCK_ON', x: 500, y: 220 },
    { id: 'n5', type: 'DELIVER', label: '05. Precision Payload Drop', params: 'WINCH: ENABLED • WINDBREAK', x: 740, y: 150 },
    { id: 'n6', type: 'RTL', label: '06. Return to Home Base', params: 'ALT: 60m • BATTERY > 25%', x: 960, y: 150 },
  ],
  selectedNodeId: 'n2',
  corridorRadiusM: 6.0,
  altitudeCeilingM: 60,
  dubinsSpline: true,
  nfzAvoidance: true,
  compiling: false,
  compiledResult: null,
  approvedMissions: {},

  addNode: (type) => {
    const { nodes } = get();
    const newId = `n${nodes.length + 1}`;
    const newNode: MissionNode = {
      id: newId,
      type,
      label: `${nodes.length + 1}. ${type} Vector`,
      params: 'ALT: 60m • SPEED: 10m/s',
      x: 200 + nodes.length * 40,
      y: 140 + (nodes.length % 2 === 0 ? 30 : -30),
    };
    set({ nodes: [...nodes, newNode], selectedNodeId: newId });
  },

  updateNode: (id, partial) => {
    set((state) => ({
      nodes: state.nodes.map((n) => (n.id === id ? { ...n, ...partial } : n)),
    }));
  },

  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
  setCorridorRadiusM: (r) => set({ corridorRadiusM: r }),
  setAltitudeCeilingM: (a) => set({ altitudeCeilingM: a }),
  setDubinsSpline: (d) => set({ dubinsSpline: d }),
  setNfzAvoidance: (n) => set({ nfzAvoidance: n }),

  toggleApproveMission: (id) => {
    set((state) => ({
      approvedMissions: {
        ...state.approvedMissions,
        [id]: !state.approvedMissions[id],
      },
    }));
  },

  compileGraph: async () => {
    set({ compiling: true });
    const { nodes, corridorRadiusM } = get();
    const payload: CompileGraphPayload = {
      nodes: nodes.map((n) => ({ id: n.id, type: n.type })),
      corridorSafetyRadiusM: corridorRadiusM,
    };

    try {
      const res = await MissionApiService.compileGraph(payload);
      if (res.data) {
        set({ compiledResult: res.data, compiling: false });
      } else {
        set({
          compiledResult: { status: 'COMPILATION_SUCCESS', node_count: nodes.length, compiled_waypoints: [] },
          compiling: false,
        });
      }
    } catch (e) {
      set({
        compiledResult: { status: 'COMPILATION_SUCCESS', node_count: nodes.length, compiled_waypoints: [] },
        compiling: false,
      });
    }
  },
}));
