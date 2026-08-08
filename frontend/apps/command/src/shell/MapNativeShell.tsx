import React, { useState } from 'react';
import { DroneConnectionCenter } from '../hardware/DroneConnectionCenter';
import { useOperatingFabric } from '../hooks/useOperatingFabric';
import { AltariaCommandCenter } from '../command_center/AltariaCommandCenter';
import { useTacticalAudio } from '../hooks/useTacticalAudio';
import { useCognitionStore } from '../stores/cognitionStore';
import { PlanetaryCognitionGlobe } from '../world_model/PlanetaryCognitionGlobe';
import { CognitiveTwin } from '../cognition/CognitiveTwin';
import { ReplayTimeline } from '../mission_replay/CognitionReplayCinematic';
import { RenderErrorBoundary } from '../runtime/RenderErrorBoundary';
import { OperationalBoot } from './OperationalBoot';
import { CommandHUD } from './CommandHUD';
import { MissionCommandRibbon } from '../mission/MissionCommandRibbon';
import { TelemetryLakeOverlay } from '../analytics/TelemetryLakeOverlay';
import { SystemStatusHud } from './SystemStatusHud';
import { SystemDetailDrawer } from './SystemDetailDrawer';

// Next-Level Enterprise Additions
import { WorkspaceNavigationRail } from './WorkspaceNavigationRail';
import { OperationsCenterHome } from '../ops_center/OperationsCenterHome';
import { NodeMissionGraph } from '../mission_studio/NodeMissionGraph';
import { TacticalArHud } from '../hud/TacticalArHud';
import { FpvVisionHud } from '../fpv/FpvVisionHud';
import { CommandPaletteModal } from './CommandPaletteModal';
import { IncidentManagerModal } from '../incidents/IncidentManagerModal';
import { AiDebriefCard } from '../mission_replay/AiDebriefCard';
import { FaultInjectionDrawer } from '../adversarial/FaultInjectionDrawer';
import { CounterfactualTwinWorkbench } from '../twin_workbench/CounterfactualTwinWorkbench';

import { OpticShaderToolbar } from '../hud/OpticShaderToolbar';
import { MissionReplayScrubber } from '../mission_replay/MissionReplayScrubber';
import { SwarmTopologyModal } from '../swarm/SwarmTopologyModal';

import { PrimaryFlightDisplay } from '../hud/PrimaryFlightDisplay';

export function MapNativeShell() {
  useOperatingFabric();
  useTacticalAudio();
  const [cmdOpen, setCmdOpen] = useState(true);
  const [swarmModalOpen, setSwarmModalOpen] = useState(false);
  const viewMode = useCognitionStore((s) => s.viewMode);
  const workspaceMode = useCognitionStore((s) => s.workspaceMode);
  const focusedUavId = useCognitionStore((s) => s.focusedUavId);

  const showPlanet = viewMode === 'planet' || viewMode === 'dual';
  const showTwin = viewMode === 'twin' || viewMode === 'dual';

  return (
    <div className="flex h-full w-full flex-col overflow-hidden bg-[#080c14]">
      <OperationalBoot />
      <WorkspaceNavigationRail />
      <SystemStatusHud />
      <CommandHUD />

      <main className="relative flex-1 overflow-hidden">
        {/* Operations Center Homepage View */}
        {workspaceMode === 'ops_center' && <OperationsCenterHome />}

        {/* Node-Based Mission Studio View */}
        {workspaceMode === 'mission_studio' && <NodeMissionGraph />}

        {/* 3D Counterfactual Digital Twin Workbench View */}
        {workspaceMode === 'twin_workbench' && <CounterfactualTwinWorkbench />}

        {/* 3D Command Globe Viewport */}
        {workspaceMode === 'command_globe' && (
          <>
            <AltariaCommandCenter collapsed={!cmdOpen} onToggle={() => setCmdOpen((o) => !o)} />

            <div className={`absolute inset-0 transition-all duration-300 ${cmdOpen ? 'left-[300px]' : 'left-0'}`}>
              <div className="relative h-full w-full flex overflow-hidden">
                {showPlanet && (
                  <div className={`${showTwin ? 'w-1/2 border-r border-slate-800/60' : 'w-full'} relative h-full overflow-hidden`}>
                    <RenderErrorBoundary domain="Planetary Cognition">
                      <PlanetaryCognitionGlobe focusId={focusedUavId} />
                    </RenderErrorBoundary>
                    <PrimaryFlightDisplay />
                    <TacticalArHud />
                    <OpticShaderToolbar />
                    {!showTwin && <MissionCommandRibbon />}
                    <DroneConnectionCenter />
                  </div>
                )}

                {showTwin && (
                  <div className={`${showPlanet ? 'w-1/2' : 'w-full'} relative h-full overflow-hidden`}>
                    <RenderErrorBoundary domain="Cognition Battlefield">
                      <CognitiveTwin focusId={focusedUavId} />
                    </RenderErrorBoundary>
                    {!showPlanet && <DroneConnectionCenter />}
                  </div>
                )}
              </div>
            </div>

            <FpvVisionHud />
            <MissionReplayScrubber />
            <FaultInjectionDrawer />
          </>
        )}

        <SystemDetailDrawer />
      </main>

      <footer className="relative z-30 shrink-0 border-t border-slate-800/80 bg-[#010409]/95 p-2">
        <ReplayTimeline />
      </footer>
      
      <TelemetryLakeOverlay />

      {/* Global Modals */}
      <CommandPaletteModal />
      <IncidentManagerModal />
      <AiDebriefCard />
      <SwarmTopologyModal isOpen={swarmModalOpen} onClose={() => setSwarmModalOpen(false)} />
    </div>
  );
}
