import React, { useState, useRef } from 'react';
import { LeafNode, DockDropPosition } from './layoutTree';
import { useWorkspaceLayoutStore } from './useWorkspaceLayoutStore';
import { TAB_REGISTRY } from './PanelRegistry';
import { ExternalLink, X, Move, Layers } from 'lucide-react';

export interface LeafNodeViewProps {
  node: LeafNode;
  renderTabContent: (tabId: string) => React.ReactNode;
}

export const LeafNodeView: React.FC<LeafNodeViewProps> = ({ node, renderTabContent }) => {
  const { switchTab, closeTab, floatTab, dockTab, setDraggingTab, draggingTab } = useWorkspaceLayoutStore();
  const [dropHover, setDropHover] = useState<DockDropPosition | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const activeTabMeta = TAB_REGISTRY[node.activeTabId] || { title: node.activeTabId, icon: Layers };

  // Drag over target calculation
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!containerRef.current || !draggingTab) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const w = rect.width;
    const h = rect.height;

    // Detect drop zones
    if (x < w * 0.25) {
      setDropHover('left');
    } else if (x > w * 0.75) {
      setDropHover('right');
    } else if (y < h * 0.25) {
      setDropHover('top');
    } else if (y > h * 0.75) {
      setDropHover('bottom');
    } else {
      setDropHover('center');
    }
  };

  const handleDragLeave = () => {
    setDropHover(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (draggingTab && dropHover) {
      dockTab(draggingTab.tabId, node.id, dropHover);
    }
    setDropHover(null);
  };

  const handleTabDragStart = (e: React.DragEvent, tabId: string, title: string) => {
    setDraggingTab({ tabId, sourceLeafId: node.id, tabTitle: title });
    e.dataTransfer.setData('text/plain', tabId);
  };

  return (
    <div
      ref={containerRef}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className="h-full w-full flex flex-col bg-[#080c14] border border-slate-800/80 rounded-xl overflow-hidden relative select-none font-sans"
    >
      {/* 1. Header Tab Strip */}
      <div className="h-9 bg-[#0d131f] border-b border-slate-800/80 px-2 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-1 overflow-x-auto">
          {node.tabs.map((tabId) => {
            const meta = TAB_REGISTRY[tabId] || { title: tabId, icon: Layers };
            const Icon = meta.icon;
            const active = node.activeTabId === tabId;
            return (
              <div
                key={tabId}
                draggable
                onDragStart={(e) => handleTabDragStart(e, tabId, meta.title)}
                onClick={() => switchTab(node.id, tabId)}
                className={`group flex items-center space-x-1.5 px-3 py-1 rounded-md text-xs font-mono cursor-grab active:cursor-grabbing transition-all ${
                  active
                    ? 'bg-slate-800 text-white font-semibold shadow-sm border border-slate-700/60'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${active ? 'text-sky-400' : 'text-slate-500'}`} />
                <span className="text-[11px] truncate max-w-[140px]">{meta.title}</span>

                {/* Tab Close Button */}
                {node.tabs.length > 1 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      closeTab(tabId);
                    }}
                    className="opacity-0 group-hover:opacity-100 hover:text-rose-400 p-0.5 rounded transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>
            );
          })}
        </div>

        {/* Panel Action Icons */}
        <div className="flex items-center space-x-1 text-slate-400">
          <button
            onClick={() => floatTab(node.activeTabId, activeTabMeta.title)}
            title="Detach into Floating Window"
            className="p-1 rounded hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. Active Tab Content Area */}
      <div className="flex-1 overflow-hidden relative">{renderTabContent(node.activeTabId)}</div>

      {/* 3. Ghost Docking Preview Overlay */}
      {dropHover && (
        <div
          className={`absolute pointer-events-none bg-sky-500/20 border-2 border-sky-400/80 rounded-lg backdrop-blur-xs transition-all z-40 ${
            dropHover === 'left'
              ? 'inset-y-0 left-0 w-1/2'
              : dropHover === 'right'
              ? 'inset-y-0 right-0 w-1/2'
              : dropHover === 'top'
              ? 'inset-x-0 top-0 h-1/2'
              : dropHover === 'bottom'
              ? 'inset-x-0 bottom-0 h-1/2'
              : 'inset-0'
          }`}
        >
          <div className="absolute inset-0 flex items-center justify-center font-mono text-xs font-bold text-sky-200">
            DOCK {dropHover.toUpperCase()}
          </div>
        </div>
      )}
    </div>
  );
};
