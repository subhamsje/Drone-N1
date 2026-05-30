import { DroneConnectionCenter } from '../hardware/DroneConnectionCenter';
import { useState } from 'react';
import { useOperatingFabric } from '../hooks/useOperatingFabric';
import { AltariaCommandCenter } from '../command_center/AltariaCommandCenter';
import { useTacticalAudio } from '../hooks/useTacticalAudio';
import { useOperatingStore } from '../stores/operatingStore';
import { PlanetaryCognitionGlobe } from '../world_model/PlanetaryCognitionGlobe';
import { ReplayTimeline } from '../mission_replay/CognitionReplayCinematic';
import { RenderErrorBoundary } from '../runtime/RenderErrorBoundary';
import { OperationalBoot } from './OperationalBoot';
import { CommandHUD } from './CommandHUD';
import { MissionCommandRibbon } from '../mission/MissionCommandRibbon';
import { TelemetryLakeOverlay } from '../analytics/TelemetryLakeOverlay';
import { SystemStatusHud } from './SystemStatusHud';

export function MapNativeShell() {
  useOperatingFabric();
  useTacticalAudio();
  const [cmdOpen, setCmdOpen] = useState(true);

  return (
    <div className="relative h-full w-full overflow-hidden bg-[#010409]">
      <OperationalBoot />
      <SystemStatusHud />
      <CommandHUD />
      <AltariaCommandCenter collapsed={!cmdOpen} onToggle={() => setCmdOpen((o) => !o)} />

      <div className={`absolute inset-0 top-14 ${cmdOpen ? 'left-[300px]' : ''}`}>
        <div className="absolute inset-0">
          <RenderErrorBoundary domain="Planetary Cognition">
            <PlanetaryCognitionGlobe />
          </RenderErrorBoundary>
          <MissionCommandRibbon />
          <DroneConnectionCenter />
        </div>
      </div>

      <footer className={`pointer-events-auto absolute bottom-0 right-0 z-20 border-t border-slate-800/80 bg-[#010409]/95 p-2 ${cmdOpen ? 'left-[300px]' : 'left-0'}`}>
        <ReplayTimeline />
      </footer>
      
      <TelemetryLakeOverlay />
    </div>
  );
}

