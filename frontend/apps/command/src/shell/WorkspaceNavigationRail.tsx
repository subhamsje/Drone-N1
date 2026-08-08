import React from 'react';
import { useCognitionStore } from '../stores/cognitionStore';
import { MultiDomainVehicleSelector } from '../robotics/MultiDomainVehicleSelector';
import { EnterpriseModeSelector } from '../enterprise/EnterpriseModeSelector';
import { LayoutDashboard, Globe2, GitMerge, Box, Search, Shield, Activity } from 'lucide-react';

export function WorkspaceNavigationRail() {
  const workspaceMode = useCognitionStore((s) => s.workspaceMode);
  const setWorkspaceMode = useCognitionStore((s) => s.setWorkspaceMode);
  const setCtrlKOpen = useCognitionStore((s) => s.setCtrlKOpen);

  const navs = [
    { id: 'ops_center', label: 'Operations', icon: LayoutDashboard },
    { id: 'command_globe', label: 'Planetary 3D', icon: Globe2 },
    { id: 'mission_studio', label: 'Mission Studio', icon: GitMerge },
    { id: 'twin_workbench', label: 'Digital Twin', icon: Box },
  ] as const;

  return (
    <header className="h-13 w-full bg-[#0a0e17]/95 border-b border-slate-800/60 px-5 flex items-center justify-between z-30 shrink-0 select-none font-sans backdrop-blur-xl">
      {/* Brand Identity & Workspaces */}
      <div className="flex items-center space-x-7">
        <div className="flex items-center space-x-2.5">
          <div className="h-7 w-7 rounded-lg bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-mono font-bold text-white text-xs shadow-md shadow-sky-500/10">
            N1
          </div>
          <span className="font-semibold tracking-tight text-sm text-slate-100 font-mono">
            ALTARIA<span className="text-sky-400 font-normal ml-0.5">OS</span>
          </span>
        </div>

        {/* Linear-Style Pill Navigation */}
        <nav className="flex items-center space-x-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800/60">
          {navs.map((n) => {
            const Icon = n.icon;
            const active = workspaceMode === n.id;
            return (
              <button
                key={n.id}
                onClick={() => setWorkspaceMode(n.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  active
                    ? 'bg-slate-800 text-white font-semibold shadow-sm border border-slate-700/60'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${active ? 'text-sky-400' : 'text-slate-500'}`} />
                <span>{n.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Right Tools: Enterprise Tier Selector, 5G Network Pill, Multi-Domain Switcher & Command Search */}
      <div className="flex items-center space-x-3">
        <EnterpriseModeSelector />
        
        {/* Network Pill */}
        <div className="hidden xl:flex items-center space-x-2 bg-slate-900/60 border border-slate-800/80 px-2.5 py-1 rounded-lg text-xs font-mono text-slate-300">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-medium text-[11px] text-slate-300">5G PRIVATE</span>
          <span className="text-[10px] text-slate-500">12ms</span>
        </div>

        <MultiDomainVehicleSelector />

        {/* Command Search Button */}
        <button
          onClick={() => setCtrlKOpen(true)}
          className="flex items-center space-x-2.5 bg-slate-900/60 hover:bg-slate-800/80 text-slate-400 hover:text-slate-200 px-3 py-1.5 rounded-lg border border-slate-800/80 text-xs font-mono transition-all group"
        >
          <Search className="w-3.5 h-3.5 text-slate-500 group-hover:text-sky-400 transition-colors" />
          <span className="hidden sm:inline">Search...</span>
          <kbd className="bg-slate-950/80 px-1.5 py-0.5 rounded border border-slate-800 text-[10px] text-slate-400 font-mono">
            ⌘K
          </kbd>
        </button>
      </div>
    </header>
  );
}
