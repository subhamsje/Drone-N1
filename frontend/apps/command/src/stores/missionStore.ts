import { create } from 'zustand';

export interface GeoWaypoint {
  id: string;
  lon: number;
  lat: number;
  altM: number;
  label?: string;
}

export interface GeoFence {
  id: string;
  lon: number;
  lat: number;
  radiusM: number;
  kind: 'no-fly' | 'corridor' | 'recovery';
}

export interface SemanticConstraints {
  avoid_populated?: boolean;
  minimize_battery?: boolean;
  max_risk?: number;
  [key: string]: unknown;
}

export type PlanTool = 'navigate' | 'waypoint' | 'geofence' | 'corridor';

interface MissionState {
  tool: PlanTool;
  waypoints: GeoWaypoint[];
  geofences: GeoFence[];
  semanticIntent: string;
  constraints: SemanticConstraints | null;
  governanceActive: boolean;
  aiRouteSummary: string | null;
  planning: boolean;
  setTool: (t: PlanTool) => void;
  addWaypoint: (wp: Omit<GeoWaypoint, 'id'>) => void;
  removeWaypoint: (id: string) => void;
  addGeofence: (gf: Omit<GeoFence, 'id'>) => void;
  setSemanticIntent: (s: string) => void;
  setConstraints: (c: SemanticConstraints | null) => void;
  setGovernanceActive: (v: boolean) => void;
  setAiRouteSummary: (s: string | null) => void;
  setPlanning: (p: boolean) => void;
  clearMission: () => void;
}

let wpCounter = 0;
let gfCounter = 0;

export const useMissionStore = create<MissionState>((set, get) => ({
  tool: 'navigate',
  waypoints: [],
  geofences: [],
  semanticIntent: '',
  constraints: null,
  governanceActive: true,
  aiRouteSummary: null,
  planning: false,

  setTool: (tool) => set({ tool }),
  addWaypoint: (wp) => {
    wpCounter += 1;
    set({
      waypoints: [
        ...get().waypoints,
        { ...wp, id: `wp-${wpCounter}`, label: `WP${get().waypoints.length + 1}` },
      ],
    });
  },
  removeWaypoint: (id) => set({ waypoints: get().waypoints.filter((w) => w.id !== id) }),
  addGeofence: (gf) => {
    gfCounter += 1;
    set({ geofences: [...get().geofences, { ...gf, id: `gf-${gfCounter}` }] });
  },
  setSemanticIntent: (semanticIntent) => set({ semanticIntent }),
  setConstraints: (constraints) => set({ constraints }),
  setGovernanceActive: (governanceActive) => set({ governanceActive }),
  setAiRouteSummary: (aiRouteSummary) => set({ aiRouteSummary }),
  setPlanning: (planning) => set({ planning }),
  clearMission: () => set({ waypoints: [], geofences: [], aiRouteSummary: null, constraints: null }),
}));
