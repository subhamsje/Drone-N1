import { useOperatingStore } from '../stores/operatingStore';
import { survivabilityColor } from '@altaria/cognition-sdk';
import { MissionLifecycleRail } from '../mission/MissionLifecycleRail';
import { EvidenceDAG } from '../certification/EvidenceDAG';
import { ReplayTimeline } from '../mission_replay/CognitionReplayCinematic';

function Metric({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="rounded border border-slate-800/80 bg-slate-950/60 px-2 py-1.5">
      <div className="font-mono text-[8px] uppercase tracking-widest text-slate-500">{label}</div>
      <div className="font-mono text-sm font-semibold" style={{ color: color ?? '#94a3b8' }}>
        {value}
      </div>
    </div>
  );
}

export function MissionCommandPanel() {
  const mission = useOperatingStore((s) => s.operating?.mission);
  const active = mission?.active_mission;
  return (
    <div className="flex flex-col gap-2">
      <p className="font-mono text-[9px] uppercase tracking-widest text-cyan-700">Mission command</p>
      {active ? (
        <div className="rounded border border-cyan-900/40 bg-cyan-950/20 p-2 font-mono text-[10px] text-cyan-200">
          <div>{active.mission_id}</div>
          <div className="text-slate-400">Phase: {active.phase}</div>
          <div className="mt-1 text-slate-500">{active.intent}</div>
        </div>
      ) : (
        <p className="font-mono text-[10px] text-slate-500">No active mission — plan below</p>
      )}
      {(mission?.route_governance as { reroute_required?: boolean })?.reroute_required && (
        <p className="font-mono text-[10px] text-amber-400">Route governance: REROUTE REQUIRED</p>
      )}
      <MissionLifecycleRail embedded />
    </div>
  );
}

export function SurvivabilityCenterPanel() {
  const s = useOperatingStore((s) => s.operating?.survivability);
  if (!s) return <p className="font-mono text-[10px] text-slate-500">Awaiting survivability stream…</p>;
  const col = survivabilityColor(s.composite_survivability);
  return (
    <div className="grid grid-cols-2 gap-2">
      <Metric label="Survivability" value={`${(s.composite_survivability * 100).toFixed(1)}%`} color={col} />
      <Metric label="Crash P" value={`${(s.crash_probability * 100).toFixed(1)}%`} color="#f87171" />
      <Metric label="Mission continuity" value={`${(s.mission_continuity * 100).toFixed(0)}%`} />
      <Metric label="Landing success" value={`${(s.landing_success_probability * 100).toFixed(0)}%`} />
      <Metric label="Recovery P" value={`${(s.recovery_success_probability * 100).toFixed(0)}%`} />
      <Metric label="Strategy" value={s.strategy ?? s.urgency ?? '—'} />
      {s.landing_zone != null && (
        <p className="col-span-2 font-mono text-[9px] text-teal-400">Emergency LZ computed</p>
      )}
    </div>
  );
}

export function WorldModelPanel() {
  const w = useOperatingStore((s) => s.operating?.world);
  const forecast = w?.forecast as { nodes?: Array<{ state_key: string; probability: number; consequence?: string }> } | undefined;
  const nodes = forecast?.nodes ?? [];
  return (
    <div className="flex flex-col gap-2">
      <p className="font-mono text-[9px] uppercase tracking-widest text-violet-600">Predictive world model</p>
      {nodes.length === 0 ? (
        <p className="font-mono text-[10px] text-slate-500">Run SIMULATE on mission to load futures</p>
      ) : (
        <ul className="max-h-40 space-y-1 overflow-y-auto">
          {nodes.map((n) => (
            <li key={n.state_key} className="flex justify-between font-mono text-[9px] text-slate-400">
              <span>{n.state_key}</span>
              <span>{(n.probability * 100).toFixed(0)}%</span>
            </li>
          ))}
        </ul>
      )}
      <p className="font-mono text-[9px] text-slate-600">Branches render on globe + twin</p>
    </div>
  );
}

export function SwarmFleetPanel() {
  const fleet = useOperatingStore((s) => s.operating?.fleet);
  const analytics = useOperatingStore((s) => s.operating?.analytics);
  const intel = fleet?.intelligence as { member_count?: number; scale_tier?: string } | undefined;
  return (
    <div className="flex flex-col gap-2">
      <Metric label="Fleet tier" value={intel?.scale_tier ?? 'squad'} />
      <Metric label="Members" value={String(intel?.member_count ?? 4)} />
      <Metric
        label="Fleet readiness"
        value={`${((analytics?.fleet_readiness as number) ?? 0.7) * 100}%`}
        color={survivabilityColor((analytics?.fleet_readiness as number) ?? 0.7)}
      />
      <Metric label="Mean survivability" value={`${(((analytics?.mean_survivability as number) ?? 0.5) * 100).toFixed(0)}%`} />
    </div>
  );
}

export function TrustCertificationPanel() {
  const cognition = useOperatingStore((s) => s.operating?.cognition);
  const cert = cognition?.certification;
  const chain = cognition?.cognition?.reasoning_chain ?? [];

  async function exportAudit() {
    const API = import.meta.env.VITE_API_URL ?? '';
    const res = await fetch(`${API}/api/v1/intelligence/certification/export`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `altaria-audit-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex flex-col gap-2">
      <p className="font-mono text-[9px] uppercase tracking-widest text-slate-500">Decision lineage</p>
      <ul className="max-h-28 space-y-0.5 overflow-y-auto font-mono text-[9px] text-slate-400">
        {chain.map((line, i) => (
          <li key={i}>› {line}</li>
        ))}
      </ul>
      <EvidenceDAG evidence={(cert as { evidence_dag?: unknown })?.evidence_dag} />
      <button
        type="button"
        onClick={() => void exportAudit()}
        className="rounded border border-slate-700 py-1 font-mono text-[9px] uppercase tracking-widest text-cyan-600 hover:bg-cyan-950/30"
      >
        Export audit package
      </button>
    </div>
  );
}

export function GeospatialIntelPanel() {
  const g = useOperatingStore((s) => s.operating?.geospatial);
  const weather = g?.weather as Record<string, number> | undefined;
  const airspace = g?.airspace as Record<string, unknown> | undefined;
  const rf = g?.rf as Record<string, number> | undefined;
  return (
    <div className="grid grid-cols-2 gap-2">
      <Metric label="Wind" value={`${weather?.wind_mps ?? 0} m/s`} />
      <Metric label="Turbulence" value={`${((weather?.turbulence_index ?? 0) * 100).toFixed(0)}%`} />
      <Metric label="Airspace" value={String(airspace?.restriction_level ?? '—')} />
      <Metric label="Jamming risk" value={`${((rf?.jamming_risk ?? 0) * 100).toFixed(0)}%`} />
    </div>
  );
}

export function EdgeOpsPanel() {
  const edge = useOperatingStore((s) => s.operating?.edge ?? useOperatingStore.getState().platform.edge);
  const e = edge as Record<string, unknown> | undefined;
  return (
    <div className="grid grid-cols-2 gap-2">
      <Metric label="Device" value={String(e?.device ?? 'jetson_orin')} />
      <Metric label="Cloud sync" value={e?.cloud_connected ? 'ONLINE' : 'EDGE AUTHORITY'} color={e?.cloud_connected ? '#22d3a8' : '#f59e0b'} />
      <Metric label="Buffer" value={String(e?.buffered_frames ?? 0)} />
      <Metric label="Offline mode" value={e?.offline_mode ? 'YES' : 'NO'} />
    </div>
  );
}

export function MlopsPanel() {
  const m = useOperatingStore((s) => s.platform.mlops) as { models?: unknown[]; deployments?: unknown[] } | undefined;
  return (
    <div className="font-mono text-[10px] text-slate-400">
      <p>Models: {m?.models?.length ?? 0}</p>
      <p>Deployments: {m?.deployments?.length ?? 0}</p>
    </div>
  );
}

export function MissionReplayPanel() {
  return <ReplayTimeline />;
}
