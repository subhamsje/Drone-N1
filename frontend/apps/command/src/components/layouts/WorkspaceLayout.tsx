import React from 'react';
import { useUiStore } from '../../global/uiState';
import { TopCommandBar } from './TopCommandBar';
import { DockableWorkspace } from '../../layout';
import { PlanetaryCognitionGlobe } from '../../world_model/PlanetaryCognitionGlobe';
import { PrimaryFlightDisplay } from '../../hud/PrimaryFlightDisplay';
import { FpvFeed } from '../../features/fpv/FpvFeed';
import { CounterfactualTwinWorkbench } from '../../twin_workbench/CounterfactualTwinWorkbench';
import { NodeGraph } from '../../features/mission-studio/NodeGraph';
import { OpsDashboard } from '../../features/ops-center/OpsDashboard';
import { LogConsole } from '../composites/LogConsole';
import { EventTimelineView } from '../../features/timeline/EventTimelineView';
import { CommandPaletteModal } from '../../shell/CommandPaletteModal';

export const WorkspaceLayout: React.FC = () => {
  const { commandPaletteOpen } = useUiStore();

  const renderTabContent = (tabId: string) => {
    switch (tabId) {
      case 'globe':
        return (
          <div className="relative h-full w-full overflow-hidden">
            <PlanetaryCognitionGlobe focusId="Altaria-Alpha" />
            <PrimaryFlightDisplay />
          </div>
        );
      case 'fpv':
        return <FpvFeed />;
      case 'twin':
        return <CounterfactualTwinWorkbench />;
      case 'studio':
        return <NodeGraph />;
      case 'ops':
        return <OpsDashboard />;
      case 'pfd':
        return (
          <div className="h-full w-full bg-[#050811] p-4 flex items-center justify-center relative">
            <PrimaryFlightDisplay />
          </div>
        );
      case 'telemetry':
        return <LogConsole />;
      case 'timeline':
        return <EventTimelineView />;
      default:
        return (
          <div className="h-full w-full flex items-center justify-center font-mono text-xs text-slate-500">
            Viewport: {tabId}
          </div>
        );
    }
  };

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-[#080c14] text-slate-200 font-sans select-none">
      {/* 1. Global Unified Command Bar */}
      <TopCommandBar />

      {/* 2. Main Dockable Workspace System */}
      <main className="relative flex-1 overflow-hidden">
        <DockableWorkspace renderTabContent={renderTabContent} />
      </main>

      {/* 3. Global Command Palette Modal (⌘K) */}
      <CommandPaletteModal />
    </div>
  );
};
