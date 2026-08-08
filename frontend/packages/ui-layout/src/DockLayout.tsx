import React, { useState } from 'react';

export interface DockPanelConfig {
  id: string;
  title: string;
  component: React.ReactNode;
}

export interface DockLayoutProps {
  panels: DockPanelConfig[];
  defaultActiveId?: string;
  className?: string;
}

export const DockLayout: React.FC<DockLayoutProps> = ({
  panels,
  defaultActiveId,
  className = '',
}) => {
  const [activeId, setActiveId] = useState(defaultActiveId || panels[0]?.id);

  const activePanel = panels.find((p) => p.id === activeId) || panels[0];

  return (
    <div className={`h-full w-full flex flex-col bg-[#080c14] overflow-hidden ${className}`}>
      {/* Dock Tab Selector Header */}
      <div className="h-10 bg-[#0d131f] border-b border-slate-800/80 px-4 flex items-center space-x-2 shrink-0 select-none">
        {panels.map((panel) => {
          const active = activeId === panel.id;
          return (
            <button
              key={panel.id}
              onClick={() => setActiveId(panel.id)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                active
                  ? 'bg-slate-800 text-white font-semibold shadow-sm border border-slate-700/60'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              {panel.title}
            </button>
          );
        })}
      </div>

      {/* Active Dock Viewport */}
      <div className="flex-1 overflow-hidden">{activePanel?.component}</div>
    </div>
  );
};
