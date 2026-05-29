import { DroneConnectionCenter } from '../hardware/DroneConnectionCenter';
import { useState, type ReactNode } from 'react';
import { useOperatingFabric } from '../hooks/useOperatingFabric';
import { AltariaCommandCenter } from '../command_center/AltariaCommandCenter';
import { useTacticalAudio } from '../hooks/useTacticalAudio';
import { useCognitionStore } from '../stores/cognitionStore';
import { useOperatingStore } from '../stores/operatingStore';
import { PlanetaryCognitionGlobe } from '../world_model/PlanetaryCognitionGlobe';
import { CognitiveTwin } from '../cognition/CognitiveTwin';
import { CognitionPanel } from '../cognition/CognitionPanel';
import { SurvivalView } from '../survival/SurvivalView';
import { SwarmTopology } from '../swarm/SwarmCognitionField';
import { AdversarialView } from '../adversarial/AdversarialView';
import { HardwareCognition } from '../hardware/HardwareStressField';
import { TrustLayer } from '../trust/TrustLayer';
import { ReplayTimeline } from '../mission_replay/CognitionReplayCinematic';
import { RenderErrorBoundary } from '../runtime/RenderErrorBoundary';
import { OperationalBoot } from './OperationalBoot';
import { CommandHUD } from './CommandHUD';
import { MissionCommandRibbon } from '../mission/MissionCommandRibbon';

function CognitionDrawer({
  open,
  side,
  title,
  onClose,
  children,
}: {
  open: boolean;
  side: 'left' | 'right';
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  if (!open) {
    return (
      <button
        type="button"
        onClick={onClose}
        className={`pointer-events-auto absolute top-16 z-20 ops-panel px-2 py-3 font-mono text-[9px] uppercase tracking-widest text-slate-500 ${
          side === 'left' ? 'left-0 rounded-r' : 'right-0 rounded-l'
        }`}
        style={{ writingMode: 'vertical-rl' }}
      >
        {title}
      </button>
    );
  }
  return (
    <aside
      className={`pointer-events-auto absolute top-12 z-20 flex h-[calc(100%-7.5rem)] w-[280px] flex-col gap-2 overflow-y-auto border-slate-800/80 bg-[#010409]/92 p-2 backdrop-blur-md ${
        side === 'left' ? 'left-0 border-r' : 'right-0 border-l'
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-cyan-600">{title}</span>
        <button type="button" onClick={onClose} className="text-slate-500">
          ✕
        </button>
      </div>
      {children}
    </aside>
  );
}

export function MapNativeShell() {
  useOperatingFabric();
  useTacticalAudio();
  const viewMode = useCognitionStore((s) => s.viewMode);
  const connected = useOperatingStore((s) => s.stream.connection === 'connected');
  const [cmdOpen, setCmdOpen] = useState(true);
  const [leftOpen, setLeftOpen] = useState(false);
  const [rightOpen, setRightOpen] = useState(false);

  const showPlanet = viewMode === 'planet' || viewMode === 'dual';
  const showTwin = viewMode === 'twin' || viewMode === 'dual';

  return (
    <div className="relative h-full w-full overflow-hidden bg-[#010409]">
      <OperationalBoot />
      <CommandHUD />
      <AltariaCommandCenter collapsed={!cmdOpen} onToggle={() => setCmdOpen((o) => !o)} />

      <div className={`absolute inset-0 top-14 ${cmdOpen ? 'left-[300px]' : ''}`}>
        {!connected && (
          <div className="absolute inset-x-0 top-0 z-30 bg-amber-950/90 py-1 text-center font-mono text-[10px] text-amber-300">
            COGNITION STREAM OFFLINE — PLANETARY RENDER ONLY
          </div>
        )}

        {showPlanet && (
          <div className={showTwin ? 'absolute inset-0 left-0 w-1/2' : 'absolute inset-0'}>
            <RenderErrorBoundary domain="Planetary Cognition">
              <PlanetaryCognitionGlobe />
            </RenderErrorBoundary>
            <MissionCommandRibbon />
            <DroneConnectionCenter />
          </div>
        )}

        {showTwin && (
          <div className={showPlanet ? 'absolute inset-0 right-0 w-1/2 border-l border-slate-800/60' : 'absolute inset-0'}>
            <RenderErrorBoundary domain="Cognition Battlefield">
              <CognitiveTwin />
            </RenderErrorBoundary>
            {!showPlanet && <DroneConnectionCenter />}
          </div>
        )}
      </div>

      <CognitionDrawer open={leftOpen} side="left" title="Cognition" onClose={() => setLeftOpen(!leftOpen)}>
        <CognitionPanel />
        <SurvivalView />
        <TrustLayer />
      </CognitionDrawer>

      <CognitionDrawer open={rightOpen} side="right" title="Operations" onClose={() => setRightOpen(!rightOpen)}>
        <SwarmTopology />
        <AdversarialView />
        <HardwareCognition />
      </CognitionDrawer>

      <footer className={`pointer-events-auto absolute bottom-0 right-0 z-20 border-t border-slate-800/80 bg-[#010409]/95 p-2 ${cmdOpen ? 'left-[300px]' : 'left-0'}`}>
        <ReplayTimeline />
      </footer>
    </div>
  );
}
