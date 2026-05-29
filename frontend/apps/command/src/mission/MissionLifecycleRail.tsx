import { useState } from 'react';
import { useMissionStore } from '../stores/missionStore';
import { cognitionEngine } from '../config/runtime';
import { planMission, advanceMission } from '../api/intelligenceApi';
import { useOperatingStore } from '../stores/operatingStore';

const PHASES = [
  'plan',
  'simulate',
  'validate',
  'approve',
  'upload',
  'execute',
  'monitor',
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
        if (v && !v.passed) setLog('Validation failed — adjust route or intent');
        else if (target === 'approve') setLog('Mission approved · ready for upload');
        else if (target === 'upload') setLog('Route uploaded to flight stack (MAVSDK)');
        else if (target === 'execute') setLog('Mission executing — monitor cognition stream');
        else setLog(`Phase: ${res.mission.phase}`);
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
        <span className="uppercase tracking-widest text-cyan-700">Mission intelligence</span>
        <span>
          {missionId ? `${missionId} · ${phase}` : 'No active mission'}
        </span>
      </div>
      )}
      <div className="flex flex-wrap items-center gap-1">
        {PHASES.map((p) => (
          <button
            key={p}
            type="button"
            disabled={busy}
            onClick={() => runAdvance(p)}
            className={`rounded px-2 py-1 uppercase tracking-wider ${
              phase === p
                ? 'bg-cyan-950 text-cyan-300 ring-1 ring-cyan-800'
                : 'bg-slate-900/80 text-slate-400 hover:text-cyan-400'
            }`}
          >
            {p}
          </button>
        ))}
        <button
          type="button"
          disabled={busy}
          onClick={() => runAdvance()}
          className="ml-auto rounded bg-teal-950/60 px-3 py-1 text-teal-300 ring-1 ring-teal-900"
        >
          Next →
        </button>
      </div>
      {log && <p className="text-slate-400">{log}</p>}
    </div>
  );
}
