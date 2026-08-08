import React from 'react';
import { useWorkspaceLayoutStore } from './useWorkspaceLayoutStore';
import { SplitNodeView } from './SplitNodeView';
import { FloatingPanelContainer } from './FloatingPanelContainer';
import { LayoutDashboard, Video, GitMerge, RotateCcw, Box } from 'lucide-react';

export interface DockableWorkspaceProps {
  renderTabContent: (tabId: string) => React.ReactNode;
  className?: string;
}

export const DockableWorkspace: React.FC<DockableWorkspaceProps> = ({
  renderTabContent,
  className = '',
}) => {
  const { layoutTree, activePreset, loadPreset, resetLayout } = useWorkspaceLayoutStore();

  const presets = [
    { id: 'tactical', label: 'Tactical Cockpit', icon: LayoutDashboard },
    { id: 'fpv', label: 'FPV & Photogrammetry', icon: Video },
    { id: 'studio', label: 'Mission Studio IDE', icon: GitMerge },
  ] as const;

  return (
    <div className={`h-full w-full flex flex-col bg-[#080c14] overflow-hidden select-none font-sans ${className}`}>
      {/* Top Workspace Presets Sub-Header */}
      <div className="h-10 bg-[#0d131f] border-b border-slate-800/80 px-4 flex items-center justify-between shrink-0 font-mono text-xs">
        <div className="flex items-center space-x-2">
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">WORKSPACE PRESETS:</span>
          <div className="flex items-center space-x-1 bg-slate-900/80 p-0.5 rounded-lg border border-slate-800">
            {presets.map((p) => {
              const Icon = p.icon;
              const active = activePreset === p.id;
              return (
                <button
                  key={p.id}
                  onClick={() => loadPreset(p.id as any)}
                  className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-[11px] transition-all ${
                    active
                      ? 'bg-slate-800 text-sky-400 font-bold border border-slate-700/60 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Icon className="w-3 h-3" />
                  <span>{p.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        <button
          onClick={resetLayout}
          className="flex items-center space-x-1 text-slate-400 hover:text-slate-200 text-[11px] p-1 rounded hover:bg-slate-800/60 transition-colors"
          title="Reset Layout to Factory Default"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset Layout</span>
        </button>
      </div>

      {/* Main Recursive Tree Split Area */}
      <div className="flex-1 p-2 overflow-hidden relative">
        <SplitNodeView node={layoutTree} renderTabContent={renderTabContent} />
      </div>

      {/* Floating Detached Panels */}
      <FloatingPanelContainer renderTabContent={renderTabContent} />
    </div>
  );
};
