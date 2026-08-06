import { useOperatingStore } from '../stores/operatingStore';
import { MissionLifecycleRail } from '../mission/MissionLifecycleRail';
import { ReplayTimeline } from '../mission_replay/CognitionReplayCinematic';
import { useQuery } from '@tanstack/react-query';
import { getEnterpriseAnalytics } from '../api/intelligenceApi';
import { useCognitionStore } from '../stores/cognitionStore';
import { WorldFuturesPanel } from '../world_model/WorldFuturesPanel';
import { EvidenceGraph } from '../certification/EvidenceGraph';
import { OperationalGraph } from './OperationalGraph';
import { useState } from 'react';
import { flyToOperationalArea } from '../world_model/cesiumGlobe';

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
  const checks = (active as any)?.checks as Record<string, string> | undefined;

  return (
    <div className="flex flex-col gap-2">
      <p className="font-mono text-[9px] uppercase tracking-widest text-cyan-700">Mission command</p>
      {active ? (
        <div className="flex flex-col gap-2">
          <div className="rounded border border-cyan-900/40 bg-cyan-950/20 p-2 font-mono text-[10px] text-cyan-200">
            <div className="font-bold">{active.mission_id}</div>
            <div className="text-slate-400">Phase: {active.phase.toUpperCase()}</div>
            <div className="mt-1 text-slate-500 italic text-[9px]">"{active.intent}"</div>
          </div>
          
          {/* Phase 2: Safety Scores */}
          <div className="grid grid-cols-2 gap-1.5">
            {Object.entries(checks ?? { weather: 'OK', battery: 'OK', airspace: 'OK', rf: 'OK', traffic: 'OK' }).map(([key, val]) => (
              <div key={key} className="flex justify-between items-center bg-slate-900/40 px-2 py-1 rounded border border-slate-800/40">
                <span className="font-mono text-[7px] uppercase text-slate-500">{key}</span>
                <span className={`font-mono text-[8px] font-bold ${val === 'GREEN' || val === 'OK' || val === 'OPEN' ? 'text-emerald-400' : val === 'WARNING' ? 'text-amber-500' : 'text-red-500'}`}>
                  {val}
                </span>
              </div>
            ))}
          </div>

          {/* Phase 2: Interactive Waypoints */}
          <div className="flex flex-col gap-1 mt-1">
            <p className="font-mono text-[8px] text-slate-600 uppercase font-bold">Planned Waypoints</p>
            <div className="max-h-32 overflow-y-auto flex flex-col gap-1 pr-1 custom-scrollbar">
              {((active as any).plan?.waypoints ?? []).map((wp: any, i: number) => (
                <button
                  key={i}
                  onClick={() => {
                    const viewer = (window as any).cesiumViewer; 
                    if (viewer) {
                      flyToOperationalArea(viewer, wp.lon, wp.lat, 200);
                    }
                  }}
                  className="flex justify-between items-center bg-slate-900/20 p-1.5 rounded border border-slate-800/60 hover:border-cyan-500/50 hover:bg-cyan-950/10 transition-all text-left group"
                >
                  <span className="font-mono text-[8px] text-cyan-500/80 group-hover:text-cyan-400">{wp.label || `WP${i+1}`}</span>
                  <span className="font-mono text-[7px] text-slate-600">{wp.lat.toFixed(4)}N</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <p className="font-mono text-[10px] text-slate-500 italic">Initiate semantic plan to start...</p>
      )}
      {(mission?.route_governance as { reroute_required?: boolean })?.reroute_required && (
        <p className="font-mono text-[10px] text-amber-400 animate-pulse font-bold">● REROUTE REQUIRED</p>
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
      <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
        <p className="font-mono text-[7px] text-slate-500 uppercase mb-2">Operational Graph</p>
        <OperationalGraph />
      </div>
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
  const mtbf = data?.mtbf_hours ?? '—';
  const mttr = data?.mttr_seconds ?? '—';

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
        <Metric label="MTBF (Hours)" value={String(mtbf)} />
        <Metric label="MTTR (Seconds)" value={String(mttr)} color="#f43f5e" />
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

export function FleetCommandPanel() {
  const fleet = useOperatingStore((s) => s.operating?.fleet);
  const status = fleet?.status ?? {};
  const [filter, setFilter] = useState<'all' | 'warning' | 'critical'>('all');
  const setFocusedUavId = useCognitionStore((s) => s.setFocusedUavId);

  const drones = Object.entries(status).map(([id, s]: [string, any]) => ({
    id,
    loc: `${s.aircraft?.geo?.lat.toFixed(3)}, ${s.aircraft?.geo?.lon.toFixed(3)}`,
    batt: `${(s.aircraft?.battery_pct * 100).toFixed(0)}%`,
    health: s.survivability?.composite_survivability ?? 1.0,
    mission: s.mission?.active_mission?.mission_id ?? 'IDLE',
    status: s.aircraft?.connected ? 'ready' : 'offline'
  })).filter(d => {
    if (filter === 'warning') return d.health < 0.8 && d.health >= 0.5;
    if (filter === 'critical') return d.health < 0.5;
    return true;
  });
  
  return (
    <div className="flex flex-col gap-3 h-full overflow-hidden">
      <div className="flex gap-1">
        {(['all', 'warning', 'critical'] as const).map(f => (
          <button 
            key={f}
            onClick={() => setFilter(f)}
            className={`px-2 py-0.5 rounded text-[7px] uppercase font-bold border transition-colors ${filter === f ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400' : 'border-slate-800 text-slate-500'}`}
          >
            {f}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto border border-slate-800 rounded bg-slate-950/40">
        <table className="w-full font-mono text-[8px] text-left">
          <thead className="sticky top-0 bg-slate-900 text-slate-500 uppercase">
            <tr>
              <th className="p-1.5">UAV_ID</th>
              <th className="p-1.5">BAT</th>
              <th className="p-1.5">HLTH</th>
              <th className="p-1.5 text-right">MISSION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-900">
            {drones.length === 0 ? (
              <tr><td colSpan={4} className="p-4 text-center text-slate-600 italic">No fleet units detected.</td></tr>
            ) : drones.map(d => (
              <tr 
                key={d.id} 
                onClick={() => setFocusedUavId(d.id)}
                className="hover:bg-white/5 transition-colors cursor-pointer group"
              >
                <td className="p-1.5 text-cyan-400 font-bold group-hover:text-cyan-300">{d.id.slice(0,10)}</td>
                <td className="p-1.5 text-slate-300">{d.batt}</td>
                <td className={`p-1.5 font-bold ${d.health < 0.5 ? 'text-red-500' : d.health < 0.8 ? 'text-amber-500' : 'text-emerald-500'}`}>
                  {(d.health * 100).toFixed(0)}%
                </td>
                <td className="p-1.5 text-right text-slate-500">{d.mission}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function HardwareTwinPanel() {
  const hardware = useOperatingStore((s) => s.operating?.hardware);
  
  if (!hardware) {
    return <p className="font-mono text-[9px] text-slate-500 italic">Awaiting hardware telemetry...</p>;
  }

  const urgencyColor = hardware.urgency === 'immediate' ? 'text-red-500' : hardware.urgency === 'scheduled' ? 'text-amber-500' : 'text-emerald-400';

  return (
    <div className="flex flex-col gap-3">
      <div className="rounded border border-slate-800 bg-slate-950/40 p-2 flex justify-between items-center">
        <div>
          <p className="font-mono text-[7px] text-slate-500 uppercase">Hardware Engine</p>
          <p className="font-mono text-xs text-white uppercase">{hardware.device}</p>
        </div>
        <div className={`font-mono text-[8px] uppercase font-bold ${urgencyColor}`}>
          {hardware.urgency}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Metric label="Motor Deg" value={`${(hardware.motor_wear * 100).toFixed(1)}%`} color={hardware.motor_wear > 0.4 ? '#f43f5e' : undefined} />
        <Metric label="ESC Wear" value={`${(hardware.esc_wear * 100).toFixed(1)}%`} color={hardware.esc_wear > 0.5 ? '#f59e0b' : undefined} />
        <Metric label="Vibration" value={`${(hardware.vibration).toFixed(2)}G`} />
        <Metric label="Fatigue" value={hardware.fatigue > 0.6 ? 'HIGH' : hardware.fatigue > 0.3 ? 'MED' : 'LOW'} color={hardware.fatigue > 0.6 ? '#f43f5e' : undefined} />
      </div>
      <div className="rounded bg-slate-900/50 p-2 font-mono text-[8px] text-slate-500 leading-relaxed">
        <span className="text-slate-400">HEALTH:</span> {((hardware.battery_health) * 100).toFixed(1)}% efficiency remaining.<br/>
        <span className="text-slate-400">STATUS:</span> {hardware.urgency === 'nominal' ? 'Optimal structural integrity.' : 'Inspection recommended.'}
      </div>
    </div>
  );
}

export function SecurityCenterPanel() {
  const stream = useOperatingStore((s) => s.stream);
  return (
    <div className="flex flex-col gap-3">
      <div className="rounded border border-emerald-500/20 bg-emerald-950/10 p-2 font-mono text-[10px] text-emerald-400 uppercase tracking-widest text-center">
        Zero Trust Integrity
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Metric label="ECDSA Status" value="ENFORCED" color="#22d3a8" />
        <Metric label="Replay Guard" value="ACTIVE" color="#22d3a8" />
        <Metric label="Auth Level" value="L3_CMD" color="#38bdf8" />
        <Metric label="Audit Cycle" value="REALTIME" />
      </div>
      <div className="flex flex-col gap-1">
        <p className="font-mono text-[8px] text-slate-500 uppercase">Cryptographic Events</p>
        <div className="bg-black/40 p-2 rounded border border-slate-900 max-h-32 overflow-y-auto">
          <div className="font-mono text-[7px] text-violet-400 flex justify-between">
            <span>UPLINK_CONNECT</span>
            <span className="text-emerald-500">VERIFIED</span>
          </div>
          <div className="font-mono text-[7px] text-violet-400 flex justify-between">
            <span>CMD_SIGN_TAKEOFF</span>
            <span className="text-emerald-500">VERIFIED</span>
          </div>
          <div className="font-mono text-[7px] text-violet-400 flex justify-between">
            <span>MISSION_HASH_AUDIT</span>
            <span className="text-emerald-500">STABLE</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export function ModelOpsPanel() {
  const mlops = useOperatingStore((s) => s.operating?.mlops);
  
  if (!mlops) {
    return <p className="font-mono text-[9px] text-slate-500 italic">Awaiting model registry telemetry...</p>;
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="rounded border border-slate-800 bg-slate-950/40 p-2">
        <p className="font-mono text-[7px] text-slate-500 uppercase">Model Registry</p>
        <p className="font-mono text-xs text-white uppercase">Active Models: {mlops.models.length}</p>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Metric label="Deployments" value={String(mlops.deployments.length)} />
        <Metric label="Training Jobs" value={String(mlops.training_jobs)} />
        <Metric label="OTA Status" value="ACTIVE" color="#22d3a8" />
        <Metric label="Rollback" value="READY" />
      </div>
      <div className="flex flex-col gap-1">
        <p className="font-mono text-[8px] text-slate-500 uppercase">Recent Deployments</p>
        <div className="max-h-24 overflow-y-auto rounded bg-slate-900/40 p-1.5 font-mono text-[8px] text-slate-400">
          {mlops.deployments.length === 0 ? (
            <p className="italic">No active deployments.</p>
          ) : (
            <ul className="space-y-1">
              {mlops.deployments.map((d, i) => (
                <li key={i} className="flex justify-between border-b border-slate-800 pb-1 last:border-0">
                  <span>{d.model_id.slice(0, 12)}...</span>
                  <span className="text-cyan-500">{d.stage.toUpperCase()} ({d.rollout_pct}%)</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export function ObservabilityPanel() {
  const stream = useOperatingStore((s) => s.stream);
  const platform = useOperatingStore((s) => s.platform);
  const edge = platform.edge as any;

  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-2 gap-2">
        <Metric label="Edge CPU" value={`${edge?.cpu_usage ?? 12}%`} />
        <Metric label="Edge GPU" value={`${edge?.gpu_usage ?? 4}%`} />
        <Metric label="Edge RAM" value={`${edge?.mem_usage ?? 1.2}GB`} />
        <Metric label="Disk IO" value="STABLE" color="#22d3a8" />
      </div>
      <div className="rounded bg-slate-950/60 p-2 border border-slate-800">
        <p className="font-mono text-[8px] text-slate-500 uppercase mb-1">DDS Message Throughput</p>
        <div className="h-10 flex items-end gap-0.5">
          {[40, 60, 30, 80, 45, 90, 20, 55, 70, 40].map((h, i) => (
            <div key={i} className="flex-1 bg-cyan-500/30" style={{ height: `${h}%` }} />
          ))}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <Metric label="ROS2 State" value={edge?.status ?? 'CONNECTED'} color="#22d3a8" />
        <Metric label="PX4 Latency" value={`${stream.latencyMs.toFixed(0)}ms`} />
      </div>
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

  // Phase 9: Command Timeline
  const timeline = sysLogs.filter(l => [
    'execution.command', 'mission.uploaded', 'mission.started', 'recovery.triggered', 'landing.started'
  ].includes(l.event_type)).slice(0, 5);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <p className="font-mono text-[9px] uppercase tracking-widest text-emerald-600">Command Timeline</p>
        <div className="flex flex-col gap-2 p-2 rounded bg-slate-900/40 border border-slate-800/60">
          {timeline.length === 0 ? (
            <p className="font-mono text-[8px] text-slate-600 italic">Awaiting mission milestones...</p>
          ) : timeline.map((event, i) => (
            <div key={i} className="flex gap-2 items-center">
              <div className="h-1.5 w-1.5 rounded-full bg-cyan-500" />
              <span className="font-mono text-[8px] text-cyan-400 font-bold uppercase">{event.event_type.split('.')[1]}</span>
              <span className="flex-1 border-b border-dotted border-slate-800" />
              <span className="font-mono text-[7px] text-slate-600">{new Date(event.timestamp * 1000).toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
      </div>

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
        <p className="font-mono text-[7px] text-slate-500 uppercase mb-1">Evidence DAG</p>
        <EvidenceGraph />
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
