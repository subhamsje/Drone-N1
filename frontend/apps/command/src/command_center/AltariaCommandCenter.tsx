import { useOperatingStore } from '../stores/operatingStore';
import {
  MissionCommandPanel,
  SurvivabilityCenterPanel,
  WorldModelPanel,
  SwarmFleetPanel,
  TrustCertificationPanel,
  GeospatialIntelPanel,
  EdgeOpsPanel,
  MlopsPanel,
  MissionReplayPanel,
} from './panels';

const TABS = [
  { id: 'mission', label: 'Mission' },
  { id: 'survive', label: 'Survive' },
  { id: 'world', label: 'World' },
  { id: 'swarm', label: 'Swarm' },
  { id: 'trust', label: 'Trust' },
  { id: 'geo', label: 'Earth' },
  { id: 'edge', label: 'Edge' },
  { id: 'mlops', label: 'MLOps' },
  { id: 'replay', label: 'Replay' },
] as const;

export function AltariaCommandCenter({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const tab = useOperatingStore((s) => s.commandTab);
  const setTab = useOperatingStore((s) => s.setCommandTab);
  const stream = useOperatingStore((s) => s.stream);
  const uav = useOperatingStore((s) => s.operating?.uav_id ?? '—');

  if (collapsed) {
    return (
      <button
        type="button"
        onClick={onToggle}
        className="pointer-events-auto absolute left-0 top-1/2 z-30 -translate-y-1/2 rounded-r ops-panel px-1 py-4 font-mono text-[9px] uppercase tracking-widest text-cyan-600"
        style={{ writingMode: 'vertical-rl' }}
      >
        Command OS
      </button>
    );
  }

  return (
    <aside className="pointer-events-auto absolute left-0 top-14 z-30 flex h-[calc(100%-8rem)] w-[300px] flex-col border-r border-slate-800/80 bg-[#010409]/94 backdrop-blur-md">
      <header className="flex items-center justify-between border-b border-slate-800/80 px-2 py-2">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-widest text-cyan-600">Altaria Command OS</div>
          <div className="font-mono text-[9px] text-slate-500">
            {uav} · {stream.connection} · {stream.latencyMs.toFixed(0)}ms
          </div>
        </div>
        <button type="button" onClick={onToggle} className="text-slate-500 hover:text-slate-300">
          ‹
        </button>
      </header>
      <nav className="flex flex-wrap gap-0.5 border-b border-slate-800/60 p-1">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`rounded px-1.5 py-0.5 font-mono text-[8px] uppercase tracking-wide ${
              tab === t.id ? 'bg-cyan-950 text-cyan-300' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <div className="flex-1 overflow-y-auto p-2">
        {tab === 'mission' && <MissionCommandPanel />}
        {tab === 'survive' && <SurvivabilityCenterPanel />}
        {tab === 'world' && <WorldModelPanel />}
        {tab === 'swarm' && <SwarmFleetPanel />}
        {tab === 'trust' && <TrustCertificationPanel />}
        {tab === 'geo' && <GeospatialIntelPanel />}
        {tab === 'edge' && <EdgeOpsPanel />}
        {tab === 'mlops' && <MlopsPanel />}
        {tab === 'replay' && <MissionReplayPanel />}
      </div>
    </aside>
  );
}
