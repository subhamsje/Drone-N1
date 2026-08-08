import React from 'react';
import { useCognitionStore } from '../stores/cognitionStore';
import { MultiDomainVehicleSelector } from '../robotics/MultiDomainVehicleSelector';
import { AudioVisualizerWidget } from '../audio/AudioVisualizerWidget';

export function WorkspaceNavigationRail() {
  const workspaceMode = useCognitionStore((s) => s.workspaceMode);
  const setWorkspaceMode = useCognitionStore((s) => s.setWorkspaceMode);
  const setCtrlKOpen = useCognitionStore((s) => s.setCtrlKOpen);

  const navs = [
    { id: 'ops_center', label: 'Operations Center', icon: '🏛️' },
    { id: 'command_globe', label: '3D Command Globe', icon: '🌐' },
    { id: 'mission_studio', label: 'Mission Studio Graph', icon: '🧩' },
    { id: 'twin_workbench', label: 'Digital Twin Workbench', icon: '🌀' },
  ] as const;

  return (
    <header className="h-12 w-full bg-[#010409]/95 border-b border-slate-800/80 px-4 flex items-center justify-between z-30 shrink-0 select-none font-sans">
      {/* Brand Logo & Workspaces */}
      <div className="flex items-center space-x-6">
        <div className="flex items-center space-x-2">
          <div className="h-6 w-6 rounded bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center font-mono font-bold text-white text-xs shadow-md shadow-cyan-500/20">
            N1
          </div>
          <span className="font-bold tracking-wider text-sm text-white font-mono">
            ALTARIA<span className="text-cyan-400">OS</span>
          </span>
        </div>

        {/* Workspace Switcher Tabs */}
        <nav className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-lg border border-slate-800">
          {navs.map((n) => {
            const active = workspaceMode === n.id;
            return (
              <button
                key={n.id}
                onClick={() => setWorkspaceMode(n.id)}
                className={`flex items-center space-x-2 px-3 py-1 rounded-md text-xs font-mono transition-all ${
                  active
                    ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40 shadow'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <span>{n.icon}</span>
                <span>{n.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Right Tools: Audio Visualizer, Network Failover, Multi-Domain Selector & Ctrl+K Palette */}
      <div className="flex items-center space-x-3">
        <AudioVisualizerWidget />
        <div className="hidden lg:flex items-center space-x-1.5 bg-slate-900/90 border border-emerald-500/30 px-2.5 py-1 rounded-xl text-xs font-mono text-emerald-400">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-semibold text-[11px]">5G PRIVATE</span>
          <span className="text-[10px] text-slate-500 font-mono">12ms</span>
        </div>
        <MultiDomainVehicleSelector />
        <button
          onClick={() => setCtrlKOpen(true)}
          className="flex items-center space-x-2 bg-slate-900/80 hover:bg-slate-800 text-slate-400 hover:text-white px-3 py-1 rounded-lg border border-slate-800 text-xs font-mono transition-all"
        >
          <svg className="w-3.5 h-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span>Search Commands...</span>
          <kbd className="bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800 text-[10px] text-cyan-400 font-mono">
            Ctrl+K
          </kbd>
        </button>
      </div>
    </header>
  );
}
