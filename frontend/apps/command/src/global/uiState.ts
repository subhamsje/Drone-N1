import { create } from 'zustand';

export type WorkspaceMode = 'ops_center' | 'command_globe' | 'mission_studio' | 'twin_workbench';
export type OpticMode = 'satellite' | 'tactical_ar' | 'flir' | 'nvg' | 'sar';
export type EnterpriseTier = 'COMMERCIAL_ENTERPRISE' | 'DEFENSE_TACTICAL' | 'BVLOS_REGULATORY';

export interface UiState {
  workspaceMode: WorkspaceMode;
  opticMode: OpticMode;
  enterpriseTier: EnterpriseTier;
  commandPaletteOpen: boolean;
  intelModalOpen: boolean;
  complianceModalOpen: boolean;
  incidentModalOpen: boolean;
  debriefModalOpen: boolean;
  activeDockLayout: 'standard' | 'expanded_map' | 'dual_viewport' | 'telemetry_focused';

  setWorkspaceMode: (mode: WorkspaceMode) => void;
  setOpticMode: (mode: OpticMode) => void;
  setEnterpriseTier: (tier: EnterpriseTier) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  setIntelModalOpen: (open: boolean) => void;
  setComplianceModalOpen: (open: boolean) => void;
  setIncidentModalOpen: (open: boolean) => void;
  setDebriefModalOpen: (open: boolean) => void;
  setActiveDockLayout: (layout: UiState['activeDockLayout']) => void;
}

export const useUiStore = create<UiState>((set) => ({
  workspaceMode: 'ops_center',
  opticMode: 'satellite',
  enterpriseTier: 'DEFENSE_TACTICAL',
  commandPaletteOpen: false,
  intelModalOpen: false,
  complianceModalOpen: false,
  incidentModalOpen: false,
  debriefModalOpen: false,
  activeDockLayout: 'standard',

  setWorkspaceMode: (mode) => set({ workspaceMode: mode }),
  setOpticMode: (mode) => set({ opticMode: mode }),
  setEnterpriseTier: (tier) => set({ enterpriseTier: tier }),
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
  setIntelModalOpen: (open) => set({ intelModalOpen: open }),
  setComplianceModalOpen: (open) => set({ complianceModalOpen: open }),
  setIncidentModalOpen: (open) => set({ incidentModalOpen: open }),
  setDebriefModalOpen: (open) => set({ debriefModalOpen: open }),
  setActiveDockLayout: (layout) => set({ activeDockLayout: layout }),
}));
