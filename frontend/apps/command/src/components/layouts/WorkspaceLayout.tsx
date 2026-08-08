import React from 'react';
import { useUiStore } from '../../global/uiState';
import { TopCommandBar } from './TopCommandBar';
import { OperationsCenterHome } from '../../ops_center/OperationsCenterHome';
import { NodeMissionGraph } from '../../mission_studio/NodeMissionGraph';
import { CounterfactualTwinWorkbench } from '../../twin_workbench/CounterfactualTwinWorkbench';
import { AltariaCommandCenter } from '../../command_center/AltariaCommandCenter';
import { PlanetaryCognitionGlobe } from '../../world_model/PlanetaryCognitionGlobe';
import { PrimaryFlightDisplay } from '../../hud/PrimaryFlightDisplay';
import { TacticalArHud } from '../../hud/TacticalArHud';
import { OpticShaderToolbar } from '../../hud/OpticShaderToolbar';
import { DroneConnectionCenter } from '../../hardware/DroneConnectionCenter';
import { CommandPaletteModal } from '../../shell/CommandPaletteModal';

export const WorkspaceLayout: React.FC = () => {
  const { workspaceMode, commandPaletteOpen, setCommandPaletteOpen } = useUiStore();
  const [cmdOpen, setCmdOpen] = React.useState(true);

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-[#080c14] text-slate-200 font-sans select-none">
      {/* 1. Global Unified Command Bar */}
      <TopCommandBar />

      {/* 2. Main Workspace Viewport Engine */}
      <main className="relative flex-1 overflow-hidden">
        {/* Workspace: Operations Center */}
        {workspaceMode === 'ops_center' && <OperationsCenterHome />}

        {/* Workspace: Node Mission Studio */}
        {workspaceMode === 'mission_studio' && <NodeMissionGraph />}

        {/* Workspace: 3D Counterfactual Digital Twin */}
        {workspaceMode === 'twin_workbench' && <CounterfactualTwinWorkbench />}

        {/* Workspace: Planetary 3D Command Globe */}
        {workspaceMode === 'command_globe' && (
          <div className="relative h-full w-full overflow-hidden">
            <AltariaCommandCenter collapsed={!cmdOpen} onToggle={() => setCmdOpen((o) => !o)} />

            <div className={`absolute inset-0 transition-all duration-300 ${cmdOpen ? 'left-[300px]' : 'left-0'}`}>
              <div className="relative h-full w-full overflow-hidden">
                <PlanetaryCognitionGlobe focusId="Altaria-Alpha" />
                <PrimaryFlightDisplay />
                <TacticalArHud />
                <OpticShaderToolbar />
                <DroneConnectionCenter />
              </div>
            </div>
          </div>
        )}
      </main>

      {/* 3. Global Command Search Modal (⌘K) */}
      <CommandPaletteModal />
    </div>
  );
};
