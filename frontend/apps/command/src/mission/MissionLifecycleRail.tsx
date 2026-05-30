import { useState } from 'react';
import { useMissionStore } from '../stores/missionStore';
import { cognitionEngine } from '../config/runtime';
import { planMission, advanceMission } from '../api/intelligenceApi';
import { useOperatingStore } from '../stores/operatingStore';

const PHASES = [
  { id: 'plan', label: 'PLANNED' },
  { id: 'validate', label: 'VALIDATED' },
  { id: 'approve', label: 'APPROVED' },
  { id: 'upload', label: 'UPLOADED' },
  { id: 'execute', label: 'EXECUTING' },
  { id: 'learn', label: 'COMPLETE' },
] as const;

export function MissionLifecycleRail({ embedded = false }: { embedded?: boolean }) {
  const intent = useMissionStore((s) => s.semanticIntent);
  const setActiveMissionId = useOperatingStore((s) => s.setActiveMissionId);
  const waypoints = useMissionStore((s) => s.waypoints);
  const [missionId, setMissionId] = useState<string | null>(null);
  const [phase, setPhase] = useState<string>('—');
  const [busy, setBusy] = useState(false);
  const [log, setLog] = useState<string>('');

  async function runPlan() {
    if (!intent.trim()) return;
    setBusy(true);
    try {
      const g = cognitionEngine().renderState.globe;
      const res = await planMission({
        intent,
        lat: g.lat,
        lon: g.lon,
        alt_m: g.altM + 80,
        waypoints: waypoints.map((w) => ({ lat: w.lat, lon: w.lon, altM: w.altM })),
      });
      setMissionId(res.mission_id);
      setActiveMissionId(res.mission_id);
      setPhase(res.phase);
      setLog(res.operator_summary ?? 'Mission planned');
    } catch (e) {
      setLog(`Plan failed — ${e instanceof Error ? e.message : 'offline'}`);
    } finally {
      setBusy(false);
    }
  }

  async function runAdvance(target?: string) {
    if (!missionId) {
      await runPlan();
      return;
    }
    setBusy(true);
    try {
      const res = await advanceMission(missionId, target);
      if (res.mission) {
        setPhase(res.mission.phase);
        const v = res.mission.validation;
        if (v && !v.passed) setLog('VALIDATION FAILED — Safety gate engaged');
        else if (target === 'approve') setLog('MISSION APPROVED — Command authority granted');
        else if (target === 'upload') setLog('ROUTE UPLOADED — MAVLink handoff complete');
        else if (target === 'execute') setLog('EXECUTING — Autonomy loop active');
        else if (target === 'learn') setLog('MISSION COMPLETE — Evidence archived to ClickHouse');
        else setLog(`STATE: ${res.mission.phase.toUpperCase()}`);
      }
    } catch (e) {
      setLog(`Advance failed — ${e instanceof Error ? e.message : 'error'}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div
      className={`flex w-full flex-col gap-1 font-mono text-[10px] ${
        embedded ? '' : 'pointer-events-auto border-t border-slate-800/80 bg-[#010409]/95 px-3 py-2'
      }`}
    >
      {!embedded && (
      <div className="flex items-center justify-between text-slate-500">
        <span className="uppercase tracking-widest text-cyan-700">Mission lifecycle</span>
        <span className="text-cyan-600 font-bold">
          {missionId ? `${missionId.toUpperCase()} :: ${phase.toUpperCase()}` : 'IDLE'}
        </span>
      </div>
      )}
      <div className="flex flex-wrap items-center gap-1">
        {PHASES.map((p) => (
          <button
            key={p.id}
            type="button"
            disabled={busy}
            onClick={() => runAdvance(p.id)}
            className={`rounded px-1.5 py-1 text-[8px] font-bold tracking-tighter transition-all ${
              phase === p.id
                ? 'bg-cyan-500 text-[#010409] ring-1 ring-cyan-400'
                : 'bg-slate-900/60 text-slate-500 hover:text-cyan-400 hover:bg-slate-800'
            }`}
          >
            {p.label}
          </button>
        ))}
        <button
          type="button"
          disabled={busy}
          onClick={() => runAdvance()}
          className="ml-auto rounded bg-emerald-950/60 px-3 py-1 text-emerald-300 ring-1 ring-emerald-900 text-[8px] font-bold"
        >
          STEP →
        </button>
      </div>
      {log && <p className="text-slate-400 text-[9px] mt-1 italic">{log}</p>}
    </div>
  );
}
