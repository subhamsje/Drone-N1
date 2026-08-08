/**
 * Tree-Based Dockable Layout Model & Pure Tree Transformation Functions.
 * Modeled after VS Code, Figma, and Unreal Engine 5 editor architecture.
 */

export type DockDropPosition = 'left' | 'right' | 'top' | 'bottom' | 'center';

export interface LeafNode {
  id: string;
  type: 'leaf';
  tabs: string[];
  activeTabId: string;
}

export interface SplitNode {
  id: string;
  type: 'split';
  direction: 'horizontal' | 'vertical';
  ratio: number; // 0.1 to 0.9
  first: LayoutNode;
  second: LayoutNode;
}

export type LayoutNode = LeafNode | SplitNode;

export interface FloatingPanelState {
  id: string;
  tabId: string;
  title: string;
  x: number;
  y: number;
  width: number;
  height: number;
  zIndex: number;
}

export interface DraggingTabState {
  tabId: string;
  sourceLeafId: string;
  tabTitle: string;
}

/** Pure Function: Recursively updates the split ratio of a target split node */
export function updateSplitRatio(node: LayoutNode, splitId: string, ratio: number): LayoutNode {
  if (node.type === 'leaf') return node;
  if (node.id === splitId) {
    const clampedRatio = Math.max(0.1, Math.min(0.9, ratio));
    return { ...node, ratio: clampedRatio };
  }
  return {
    ...node,
    first: updateSplitRatio(node.first, splitId, ratio),
    second: updateSplitRatio(node.second, splitId, ratio),
  };
}

/** Pure Function: Removes a tab from the tree, prunes empty leaf nodes, and collapses redundant splits */
export function removeTabFromTree(node: LayoutNode, tabId: string): LayoutNode | null {
  if (node.type === 'leaf') {
    const newTabs = node.tabs.filter((t) => t !== tabId);
    if (newTabs.length === 0) return null; // Prune empty leaf

    const newActiveId = node.activeTabId === tabId ? newTabs[0] : node.activeTabId;
    return { ...node, tabs: newTabs, activeTabId: newActiveId };
  }

  const newFirst = removeTabFromTree(node.first, tabId);
  const newSecond = removeTabFromTree(node.second, tabId);

  // If one child collapsed, promote the other child
  if (!newFirst && !newSecond) return null;
  if (!newFirst) return newSecond;
  if (!newSecond) return newFirst;

  return { ...node, first: newFirst, second: newSecond };
}

/** Pure Function: Docks a tab into a target leaf node */
export function dockTabIntoTree(
  root: LayoutNode,
  tabId: string,
  targetLeafId: string,
  position: DockDropPosition
): LayoutNode {
  // 1. Remove tab from existing position first (prevent duplication)
  const cleanTree = removeTabFromTree(root, tabId) || createDefaultLeaf(tabId);

  // 2. Insert tab into target position
  return insertTabAtTarget(cleanTree, tabId, targetLeafId, position);
}

function insertTabAtTarget(
  node: LayoutNode,
  tabId: string,
  targetLeafId: string,
  position: DockDropPosition
): LayoutNode {
  if (node.type === 'leaf') {
    if (node.id !== targetLeafId) return node;

    // Center drop: Merge tab into leaf tab array
    if (position === 'center') {
      const tabs = node.tabs.includes(tabId) ? node.tabs : [...node.tabs, tabId];
      return { ...node, tabs, activeTabId: tabId };
    }

    // Side drop: Split current leaf into a new SplitNode
    const newLeaf: LeafNode = {
      id: `leaf_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      type: 'leaf',
      tabs: [tabId],
      activeTabId: tabId,
    };

    const isHorizontal = position === 'left' || position === 'right';
    const isNewFirst = position === 'left' || position === 'top';

    return {
      id: `split_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
      type: 'split',
      direction: isHorizontal ? 'horizontal' : 'vertical',
      ratio: 0.5,
      first: isNewFirst ? newLeaf : node,
      second: isNewFirst ? node : newLeaf,
    };
  }

  return {
    ...node,
    first: insertTabAtTarget(node.first, tabId, targetLeafId, position),
    second: insertTabAtTarget(node.second, tabId, targetLeafId, position),
  };
}

export function createDefaultLeaf(tabId: string = 'ops'): LeafNode {
  return {
    id: `leaf_default_${Date.now()}`,
    type: 'leaf',
    tabs: [tabId],
    activeTabId: tabId,
  };
}

export function switchActiveTabInTree(node: LayoutNode, leafId: string, tabId: string): LayoutNode {
  if (node.type === 'leaf') {
    if (node.id === leafId && node.tabs.includes(tabId)) {
      return { ...node, activeTabId: tabId };
    }
    return node;
  }
  return {
    ...node,
    first: switchActiveTabInTree(node.first, leafId, tabId),
    second: switchActiveTabInTree(node.second, leafId, tabId),
  };
}
