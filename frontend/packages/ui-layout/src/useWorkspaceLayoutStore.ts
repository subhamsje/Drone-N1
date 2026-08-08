import { create } from 'zustand';
import {
  LayoutNode,
  FloatingPanelState,
  DraggingTabState,
  DockDropPosition,
  updateSplitRatio,
  dockTabIntoTree,
  removeTabFromTree,
  switchActiveTabInTree,
} from './layoutTree';

const DEFAULT_TACTICAL_LAYOUT: LayoutNode = {
  id: 'split_root',
  type: 'split',
  direction: 'horizontal',
  ratio: 0.65,
  first: {
    id: 'split_left',
    type: 'split',
    direction: 'vertical',
    ratio: 0.6,
    first: {
      id: 'leaf_main_viewport',
      type: 'leaf',
      tabs: ['globe', 'fpv', 'twin', 'studio'],
      activeTabId: 'globe',
    },
    second: {
      id: 'leaf_bottom_console',
      type: 'leaf',
      tabs: ['telemetry', 'timeline'],
      activeTabId: 'telemetry',
    },
  },
  second: {
    id: 'leaf_right_panel',
    type: 'leaf',
    tabs: ['ops', 'pfd'],
    activeTabId: 'ops',
  },
};

const PRESET_FPV_FOCUSED: LayoutNode = {
  id: 'split_fpv_root',
  type: 'split',
  direction: 'horizontal',
  ratio: 0.72,
  first: {
    id: 'leaf_fpv_primary',
    type: 'leaf',
    tabs: ['fpv', 'globe'],
    activeTabId: 'fpv',
  },
  second: {
    id: 'split_fpv_telemetry',
    type: 'split',
    direction: 'vertical',
    ratio: 0.5,
    first: {
      id: 'leaf_pfd_side',
      type: 'leaf',
      tabs: ['pfd', 'ops'],
      activeTabId: 'pfd',
    },
    second: {
      id: 'leaf_logs_side',
      type: 'leaf',
      tabs: ['telemetry', 'timeline'],
      activeTabId: 'telemetry',
    },
  },
};

const PRESET_STUDIO_IDE: LayoutNode = {
  id: 'leaf_studio_solo',
  type: 'leaf',
  tabs: ['studio', 'twin', 'ops'],
  activeTabId: 'studio',
};

export interface WorkspaceLayoutState {
  layoutTree: LayoutNode;
  floatingPanels: FloatingPanelState[];
  draggingTab: DraggingTabState | null;
  activePreset: string;
  nextZIndex: number;

  // Actions
  updateSplitRatio: (splitId: string, ratio: number) => void;
  setDraggingTab: (tab: DraggingTabState | null) => void;
  dockTab: (tabId: string, targetLeafId: string, position: DockDropPosition) => void;
  switchTab: (leafId: string, tabId: string) => void;
  closeTab: (tabId: string) => void;
  floatTab: (tabId: string, title: string) => void;
  updateFloatingPosition: (id: string, x: number, y: number) => void;
  bringToFront: (id: string) => void;
  closeFloatingPanel: (id: string) => void;
  redockFloatingPanel: (floatingId: string, targetLeafId: string, position: DockDropPosition) => void;
  loadPreset: (presetName: 'tactical' | 'fpv' | 'studio') => void;
  resetLayout: () => void;
}

const STORAGE_KEY = 'altaria_workspace_layout_v2';

function loadInitialTree(): LayoutNode {
  if (typeof window === 'undefined') return DEFAULT_TACTICAL_LAYOUT;
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed && parsed.type) return parsed;
    }
  } catch (e) {}
  return DEFAULT_TACTICAL_LAYOUT;
}

function persistTree(tree: LayoutNode) {
  if (typeof window !== 'undefined') {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(tree));
    } catch (e) {}
  }
}

export const useWorkspaceLayoutStore = create<WorkspaceLayoutState>((set, get) => ({
  layoutTree: loadInitialTree(),
  floatingPanels: [],
  draggingTab: null,
  activePreset: 'tactical',
  nextZIndex: 100,

  updateSplitRatio: (splitId, ratio) => {
    const { layoutTree } = get();
    const updated = updateSplitRatio(layoutTree, splitId, ratio);
    set({ layoutTree: updated });
    persistTree(updated);
  },

  setDraggingTab: (tab) => set({ draggingTab: tab }),

  dockTab: (tabId, targetLeafId, position) => {
    const { layoutTree } = get();
    const updated = dockTabIntoTree(layoutTree, tabId, targetLeafId, position);
    set({ layoutTree: updated, draggingTab: null });
    persistTree(updated);
  },

  switchTab: (leafId, tabId) => {
    const { layoutTree } = get();
    const updated = switchActiveTabInTree(layoutTree, leafId, tabId);
    set({ layoutTree: updated });
    persistTree(updated);
  },

  closeTab: (tabId) => {
    const { layoutTree } = get();
    const updated = removeTabFromTree(layoutTree, tabId);
    if (updated) {
      set({ layoutTree: updated });
      persistTree(updated);
    }
  },

  floatTab: (tabId, title) => {
    const { layoutTree, floatingPanels, nextZIndex } = get();
    const cleanTree = removeTabFromTree(layoutTree, tabId);

    const newPanel: FloatingPanelState = {
      id: `float_${Date.now()}`,
      tabId,
      title,
      x: 120 + floatingPanels.length * 30,
      y: 100 + floatingPanels.length * 30,
      width: 540,
      height: 380,
      zIndex: nextZIndex + 1,
    };

    set({
      layoutTree: cleanTree || DEFAULT_TACTICAL_LAYOUT,
      floatingPanels: [...floatingPanels, newPanel],
      nextZIndex: nextZIndex + 1,
    });
    if (cleanTree) persistTree(cleanTree);
  },

  updateFloatingPosition: (id, x, y) => {
    set((state) => ({
      floatingPanels: state.floatingPanels.map((p) =>
        p.id === id ? { ...p, x: Math.max(0, x), y: Math.max(0, y) } : p
      ),
    }));
  },

  bringToFront: (id) => {
    const { nextZIndex } = get();
    set((state) => ({
      floatingPanels: state.floatingPanels.map((p) =>
        p.id === id ? { ...p, zIndex: nextZIndex + 1 } : p
      ),
      nextZIndex: nextZIndex + 1,
    }));
  },

  closeFloatingPanel: (id) => {
    set((state) => ({
      floatingPanels: state.floatingPanels.filter((p) => p.id !== id),
    }));
  },

  redockFloatingPanel: (floatingId, targetLeafId, position) => {
    const { floatingPanels, layoutTree } = get();
    const panel = floatingPanels.find((p) => p.id === floatingId);
    if (!panel) return;

    const updatedTree = dockTabIntoTree(layoutTree, panel.tabId, targetLeafId, position);
    set({
      layoutTree: updatedTree,
      floatingPanels: floatingPanels.filter((p) => p.id !== floatingId),
    });
    persistTree(updatedTree);
  },

  loadPreset: (presetName) => {
    let tree: LayoutNode = DEFAULT_TACTICAL_LAYOUT;
    if (presetName === 'fpv') tree = PRESET_FPV_FOCUSED;
    if (presetName === 'studio') tree = PRESET_STUDIO_IDE;

    set({ layoutTree: tree, activePreset: presetName, floatingPanels: [] });
    persistTree(tree);
  },

  resetLayout: () => {
    set({ layoutTree: DEFAULT_TACTICAL_LAYOUT, floatingPanels: [] });
    persistTree(DEFAULT_TACTICAL_LAYOUT);
  },
}));
