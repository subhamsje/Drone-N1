import { useOperatingStore } from '../stores/operatingStore';
import { MissionLifecycleRail } from '../mission/MissionLifecycleRail';
import { ReplayTimeline } from '../mission_replay/CognitionReplayCinematic';
import { useQuery } from '@tanstack/react-query';
import { getEnterpriseAnalytics } from '../api/intelligenceApi';
import { useCognitionStore } from '../stores/cognitionStore';
import { WorldFuturesPanel } from '../world_model/WorldFuturesPanel';

function Metric({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
      <p className="font-mono text-[7px] text-slate-500 uppercase">{label}</p>
      <p className="font-mono text-xs font-semibold" style={{ color: color ?? '#cbd5e1' }}>{value}</p>
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

export function GeospatialIntelPanel() {
  const g = useOperatingStore((s) => s.operating?.geospatial);
  const weather = g?.weather as Record<string, number> | undefined;
  const airspace = g?.airspace as Record<string, unknown> | undefined;
  const rf = g?.rf as Record<string, number> | undefined;
  
  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-2 gap-2">
        <Metric label="Wind Velocity" value={`${weather?.wind_mps ?? 0} m/s`} />
        <Metric label="Turbulence" value={`${((weather?.turbulence_index ?? 0) * 100).toFixed(0)}%`} />
        <Metric label="Airspace State" value={String(airspace?.restriction_level ?? 'low').toUpperCase()} />
        <Metric label="RF Congestion" value={`${((rf?.jamming_risk ?? 0) * 100).toFixed(0)}%`} />
      </div>
      <WorldFuturesPanel />
    </div>
  );
}

export function MissionReplayPanel() {
  return <ReplayTimeline />;
}

export function AnalyticsPanel() {
  const setOpen = useOperatingStore((s) => s.setAnalyticsOverlayOpen);
  const open = useOperatingStore((s) => s.analyticsOverlayOpen);
  const activeTenant = useOperatingStore((s) => s.activeTenant);
  const setActiveTenant = useOperatingStore((s) => s.setActiveTenant);

  const entQ = useQuery({
    queryKey: ['enterpriseAnalytics', activeTenant],
    queryFn: () => getEnterpriseAnalytics(activeTenant),
    retry: false,
  });

  const data = entQ.data as Record<string, unknown> | undefined;
  
  if (!data && !entQ.isLoading) {
    return (
      <div className="flex flex-col gap-3">
        <div className="rounded border border-amber-900/40 bg-amber-950/20 p-2 font-mono text-[10px] text-amber-500">
          NO OPERATIONAL DATA AVAILABLE
        </div>
        <div className="rounded bg-slate-900/50 p-2 font-mono text-[8px] text-slate-500">
          Source: ClickHouse Lake<br/>
          Query: SELECT sum(velocity_n)/3600 FROM fleet_telemetry WHERE fleet_id = '{activeTenant}'<br/>
          Rows Returned: 0
        </div>
      </div>
    );
  }

  const flightHours = data?.total_flight_hours ?? '—';
  const successRate = data?.mission_success_rate != null ? `${((data.mission_success_rate as number) * 100).toFixed(1)}%` : '—';
  const crashReduction = data?.crash_reduction_pct != null ? `${((data.crash_reduction_pct as number) * 100).toFixed(1)}%` : '—';
  const readiness = data?.fleet_readiness_pct != null ? `${((data.fleet_readiness_pct as number) * 100).toFixed(0)}%` : '—';
  const missionsFlown = data?.total_missions_flown ?? '—';
  const recovery = data?.recovery_success_rate != null ? `${((data.recovery_success_rate as number) * 100).toFixed(1)}%` : '—';

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-1">
        <label className="font-mono text-[9px] uppercase tracking-widest text-slate-500">Active Fleet</label>
        <select
          value={activeTenant}
          onChange={(e) => setActiveTenant(e.target.value)}
          className="rounded border border-slate-700 bg-slate-900/80 px-2 py-1 font-mono text-[10px] text-cyan-200 outline-none"
        >
          <option value="default-fleet">Default Fleet Operations</option>
          <option value="enterprise-a">Enterprise Logistics Alpha</option>
          <option value="defense-cmd">Defense Command Swarm</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <Metric label="Flight Hours" value={String(flightHours)} color="#38bdf8" />
        <Metric label="Mission Success" value={successRate} color="#4ade80" />
        <Metric label="Crash Reduction" value={crashReduction} color="#22d3a8" />
        <Metric label="Fleet Readiness" value={readiness} />
        <Metric label="Missions Flown" value={String(missionsFlown)} color="#fcd34d" />
        <Metric label="Recovery Success" value={recovery} />
      </div>

      <div className="rounded bg-slate-900/50 p-2 font-mono text-[8px] text-slate-500 leading-relaxed">
        <span className="text-cyan-600 font-bold">CLICKHOUSE PROOF</span><br/>
        Source: ClickHouse distributed telemetry lake<br/>
        Last Update: {new Date().toLocaleTimeString()}<br/>
        Query: SELECT sum(velocity_n)/3600, avg(survivability_score) FROM fleet_telemetry WHERE fleet_id = '{activeTenant}'<br/>
      </div>

      <button
        type="button"
        onClick={() => setOpen(!open)}
        className={`rounded border py-1.5 font-mono text-[10px] uppercase tracking-widest transition-colors ${
          open
            ? 'border-cyan-500 bg-cyan-950/40 text-cyan-300'
            : 'border-slate-700 text-cyan-600 hover:bg-slate-800'
        }`}
      >
        {open ? 'Close Analytics Overlay' : 'Open Deep Dive Analytics'}
      </button>
    </div>
  );
}

export function EvidenceCenterPanel() {
  const envelope = useCognitionStore((s) => s.envelope);
  const stream = useOperatingStore((s) => s.stream);
  
  const chain = envelope?.cognition?.reasoning_chain ?? [];

  const logsQ = useQuery({
    queryKey: ['systemLogs'],
    queryFn: async () => {
      const res = await fetch(`${import.meta.env.VITE_API_URL ?? ''}/api/v1/platform/logs`);
      if (!res.ok) return [];
      return res.json();
    },
    refetchInterval: 2000,
  });

  const sysLogs = (logsQ.data as Array<{ event_type: string; timestamp: number; payload: any }>) ?? [];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <p className="font-mono text-[9px] uppercase tracking-widest text-emerald-600">Cognition Reasoning Chain</p>
        <div className="max-h-32 overflow-y-auto rounded bg-slate-950/80 p-2 border border-slate-800">
          {chain.length === 0 ? (
            <p className="font-mono text-[9px] text-slate-600 italic">Awaiting cognitive broadcast...</p>
          ) : (
            <ul className="space-y-1">
              {chain.map((msg, i) => (
                <li key={i} className="font-mono text-[8px] text-emerald-400">
                  <span className="text-slate-600 mr-2">[{new Date().toLocaleTimeString()}]</span>
                  {msg}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <p className="font-mono text-[9px] uppercase tracking-widest text-cyan-600">System Event History</p>
        <div className="max-h-48 overflow-y-auto rounded bg-slate-950/80 p-2 border border-slate-800">
          {sysLogs.length === 0 ? (
            <p className="font-mono text-[8px] text-slate-600 italic">No system logs available.</p>
          ) : (
            <ul className="space-y-1.5">
              {sysLogs.map((log, i) => (
                <li key={i} className="font-mono text-[8px] border-b border-slate-900 pb-1 last:border-0">
                  <div className="flex justify-between items-start mb-0.5">
                    <span className="text-cyan-500 font-bold uppercase">{log.event_type}</span>
                    <span className="text-slate-600">{new Date(log.timestamp * 1000).toLocaleTimeString()}</span>
                  </div>
                  <div className="text-slate-400 truncate opacity-80">
                    {JSON.stringify(log.payload)}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <p className="font-mono text-[9px] uppercase tracking-widest text-slate-500">WebSocket Diagnostics</p>
        <div className="grid grid-cols-2 gap-2 rounded bg-slate-900/40 p-2 font-mono text-[8px] text-slate-400">
          <span>State:</span> <span className={stream.connection === 'connected' ? 'text-emerald-500' : 'text-red-500'}>{stream.connection.toUpperCase()}</span>
          <span>Latency:</span> <span className="text-white">{stream.latencyMs.toFixed(1)}ms</span>
          <span>Dropped:</span> <span className="text-white">{stream.packetsDropped}</span>
          <span>Hz:</span> <span className="text-white">{stream.uiFlushHz}</span>
        </div>
      </div>
    </div>
  );
}
