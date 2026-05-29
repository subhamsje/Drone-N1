import { useState } from 'react';
import { motion } from 'framer-motion';
import { useOperatingStore } from '../stores/operatingStore';

const API = import.meta.env.VITE_API_URL ?? '';

export function DroneConnectionCenter() {
  const [expanded, setExpanded] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [connectionType, setConnectionType] = useState('udp');
  const [connectionString, setConnectionString] = useState('127.0.0.1:14540');
  const [stack, setStack] = useState('px4');

  const operating = useOperatingStore((s) => s.operating);
  const platformExec = useOperatingStore((s) => s.platform.execution);
  const streamConnected = useOperatingStore((s) => s.stream.connection === 'connected');

  const aircraft = operating?.aircraft;
  const flightStack = operating?.flight_stack ?? platformExec;
  const fcConnected = Boolean(flightStack?.connected);

  const uavId = operating?.uav_id ?? 'ALTARIA-1';
  const batt = aircraft?.battery_pct ?? 0.85;
  const vel = (aircraft?.velocity_mps ?? 0).toFixed(1);
  const alt = (aircraft?.altitude_m ?? 0).toFixed(1);
  const surv = operating?.survivability?.composite_survivability ?? 0;
  const crashRisk = operating?.survivability?.crash_probability ?? 0;
  const os = operating?.os_version ?? '8.0.0';
  const geo = aircraft?.geo;

  const handleConnect = async () => {
    setConnecting(true);
    try {
      await fetch(`${API}/api/v1/execution/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          command: 'CONNECT',
          params: { type: connectionType, uri: connectionString, stack, mode: 'sitl' },
        }),
      });
    } catch (e) {
      console.error('Connection failed', e);
    } finally {
      setConnecting(false);
    }
  };

  const dispatchCommand = async (cmd: string) => {
    try {
      await fetch(`${API}/api/v1/execution/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd, params: { source: 'operator_override' } }),
      });
    } catch (e) {
      console.error(`Failed to dispatch ${cmd}`, e);
    }
  };

  if (!expanded) {
    return (
      <button
        type="button"
        onClick={() => setExpanded(true)}
        className="pointer-events-auto absolute top-20 right-4 z-30 flex items-center gap-2 ops-panel px-3 py-2 font-mono text-[10px] text-teal-300 transition-all hover:bg-teal-950/40"
      >
        <div
          className={`h-1.5 w-1.5 rounded-full ${fcConnected ? 'animate-pulse bg-emerald-500' : streamConnected ? 'bg-cyan-500' : 'bg-red-500'}`}
        />
        FLIGHT STACK · {fcConnected ? 'LINKED' : 'STANDBY'}
      </button>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="pointer-events-auto absolute top-20 right-4 z-30 w-[360px] ops-panel ops-panel-accent p-3 shadow-2xl backdrop-blur-xl"
    >
      <div className="mb-3 flex items-center justify-between border-b border-slate-800/80 pb-2">
        <div className="flex items-center gap-2">
          <div className={`h-1.5 w-1.5 rounded-full ${fcConnected ? 'animate-pulse bg-emerald-500' : 'bg-red-500'}`} />
          <span className="font-mono text-[10px] uppercase tracking-widest text-teal-300">Flight Stack</span>
        </div>
        <button type="button" onClick={() => setExpanded(false)} className="text-[10px] text-slate-500 hover:text-slate-300">
          ✕
        </button>
      </div>

      <p className="mb-2 font-mono text-[8px] text-slate-500">
        PX4 / ArduPilot via MAVSDK · Altaria does not replace autopilot
      </p>

      {!fcConnected && !connecting && (
        <div className="mb-4">
          <div className="mb-2 grid grid-cols-2 gap-1">
            {['px4', 'ardupilot'].map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setStack(s)}
                className={`rounded-sm border px-2 py-1 font-mono text-[9px] ${
                  stack === s ? 'border-teal-500/50 bg-teal-500/10 text-teal-300' : 'border-slate-800 text-slate-500'
                }`}
              >
                {s.toUpperCase()}
              </button>
            ))}
          </div>
          <div className="mb-2 grid grid-cols-2 gap-1">
            {['udp', 'tcp', 'serial'].map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => setConnectionType(type)}
                className={`rounded-sm border px-2 py-1 font-mono text-[9px] ${
                  connectionType === type
                    ? 'border-teal-500/50 bg-teal-500/10 text-teal-300'
                    : 'border-slate-800 text-slate-500'
                }`}
              >
                {type.toUpperCase()}
              </button>
            ))}
          </div>
          <input
            type="text"
            value={connectionString}
            onChange={(e) => setConnectionString(e.target.value)}
            className="mb-2 w-full rounded-sm border border-slate-700/50 bg-slate-900/60 px-2 py-1.5 font-mono text-[10px] text-teal-100"
          />
          <button
            type="button"
            onClick={handleConnect}
            className="w-full rounded-sm border border-teal-500/30 bg-teal-600/20 py-1.5 font-mono text-[10px] tracking-widest text-teal-300 hover:bg-teal-600/30"
          >
            CONNECT MAVSDK
          </button>
        </div>
      )}

      {connecting && (
        <p className="mb-4 py-4 text-center font-mono text-[9px] text-teal-400 animate-pulse">LINKING…</p>
      )}

      {(fcConnected || streamConnected) && (
        <div className="mb-4">
          <div className="mb-3 rounded-sm border border-slate-800/80 bg-slate-900/50 p-2">
            <div className="mb-1 flex justify-between font-mono text-[11px] font-bold text-teal-400">
              <span>{uavId}</span>
              <span className="text-[9px] text-emerald-400">{String(flightStack?.mode ?? 'sitl').toUpperCase()}</span>
            </div>
            <div className="grid grid-cols-2 gap-1 font-mono text-[9px]">
              <span className="text-slate-500">BATT {(batt * 100).toFixed(0)}%</span>
              <span className="text-slate-500">VEL {vel} m/s</span>
              <span className="text-slate-500">ALT {alt}m</span>
              <span className="text-slate-500">GPS {(aircraft?.gps_trust ?? 1) * 100}%</span>
            </div>
            {geo && (
              <p className="mt-1 font-mono text-[8px] text-slate-500">
                {geo.lat.toFixed(5)}, {geo.lon.toFixed(5)} ({geo.source})
              </p>
            )}
          </div>
          <div className="mb-3 grid grid-cols-2 gap-2">
            <div>
              <span className="font-mono text-[8px] text-slate-500">SURVIVABILITY</span>
              <div className="font-mono text-[12px] font-bold text-emerald-400">{(surv * 100).toFixed(1)}%</div>
            </div>
            <div>
              <span className="font-mono text-[8px] text-slate-500">CRASH RISK</span>
              <div className={`font-mono text-[12px] font-bold ${crashRisk > 0.5 ? 'text-red-500' : 'text-slate-300'}`}>
                {(crashRisk * 100).toFixed(1)}%
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-1">
            <button type="button" onClick={() => dispatchCommand('HOLD')} className="rounded-sm bg-slate-800/80 py-1.5 font-mono text-[9px] text-slate-300">
              HOLD
            </button>
            <button type="button" onClick={() => dispatchCommand('RETURN_HOME')} className="rounded-sm border border-amber-500/30 bg-amber-900/40 py-1.5 font-mono text-[9px] text-amber-400">
              RTL
            </button>
            <button type="button" onClick={() => dispatchCommand('EMERGENCY_LAND')} className="rounded-sm bg-slate-800/80 py-1.5 font-mono text-[9px] text-slate-300">
              LAND
            </button>
            <button
              type="button"
              onClick={() => dispatchCommand('KILL')}
              className="col-span-2 rounded-sm border border-red-500/50 bg-red-950/60 py-2 font-mono text-[10px] font-bold text-red-400"
            >
              KILL SWITCH
            </button>
          </div>
          <p className="mt-2 font-mono text-[8px] text-slate-600">OS {os}</p>
        </div>
      )}
    </motion.div>
  );
}
