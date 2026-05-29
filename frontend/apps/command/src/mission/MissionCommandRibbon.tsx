import { useState, useEffect } from 'react';
import { useMissionStore, type PlanTool } from '../stores/missionStore';
import { copilotMission, planMission } from '../api/intelligenceApi';
import { cognitionEngine } from '../config/runtime';
import { motion, AnimatePresence } from 'framer-motion';

const TOOLS: { id: PlanTool; label: string }[] = [
  { id: 'navigate', label: 'Navigate' },
  { id: 'waypoint', label: 'Waypoint' },
  { id: 'corridor', label: 'Corridor' },
  { id: 'geofence', label: 'No-fly' },
];

export function MissionCommandRibbon() {
  const tool = useMissionStore((s) => s.tool);
  const setTool = useMissionStore((s) => s.setTool);
  const intent = useMissionStore((s) => s.semanticIntent);
  const setIntent = useMissionStore((s) => s.setSemanticIntent);
  const constraints = useMissionStore((s) => s.constraints);
  const setConstraints = useMissionStore((s) => s.setConstraints);
  const waypoints = useMissionStore((s) => s.waypoints);
  const removeWaypoint = useMissionStore((s) => s.removeWaypoint);
  const clearMission = useMissionStore((s) => s.clearMission);
  const governanceActive = useMissionStore((s) => s.governanceActive);
  const setGovernanceActive = useMissionStore((s) => s.setGovernanceActive);
  const aiRouteSummary = useMissionStore((s) => s.aiRouteSummary);
  const setAiRouteSummary = useMissionStore((s) => s.setAiRouteSummary);
  const planning = useMissionStore((s) => s.planning);
  const setPlanning = useMissionStore((s) => s.setPlanning);
  const [expanded, setExpanded] = useState(true);

  // Typewriter effect for AI responses
  const [displayedSummary, setDisplayedSummary] = useState('');
  useEffect(() => {
    if (!aiRouteSummary) {
      setDisplayedSummary('');
      return;
    }
    let i = 0;
    setDisplayedSummary('');
    const t = setInterval(() => {
      setDisplayedSummary(aiRouteSummary.slice(0, i));
      i++;
      if (i > aiRouteSummary.length) clearInterval(t);
    }, 20);
    return () => clearInterval(t);
  }, [aiRouteSummary]);

  async function generateMission() {
    if (!intent.trim()) return;
    setPlanning(true);
    setAiRouteSummary('');
    try {
      const g = cognitionEngine().renderState.globe;
      const copilot = await copilotMission(intent, g.lat, g.lon, g.altM + 80);
      const plan = copilot.plan as {
        constraints?: Record<string, unknown>;
        waypoints?: Array<{ lat: number; lon: number; altM?: number }>;
      };
      setConstraints((plan.constraints ?? {}) as Parameters<typeof setConstraints>[0]);
      const res = { constraints: plan.constraints ?? {} };
      if (waypoints.length === 0 && plan.waypoints?.length) {
        for (const wp of plan.waypoints) {
          useMissionStore.getState().addWaypoint({
            lon: wp.lon,
            lat: wp.lat,
            altM: wp.altM ?? g.altM + 80,
          });
        }
      } else if (waypoints.length === 0) {
        useMissionStore.getState().addWaypoint({ lon: g.lon, lat: g.lat, altM: g.altM + 80 });
        useMissionStore.getState().addWaypoint({ lon: g.lon + 0.02, lat: g.lat + 0.01, altM: g.altM + 100 });
      }
      if (res.constraints.avoid_populated) {
        useMissionStore.getState().addGeofence({
          lon: g.lon + 0.015,
          lat: g.lat - 0.01,
          radiusM: 2500,
          kind: 'no-fly',
        });
      }
      await planMission({
        intent,
        lat: g.lat,
        lon: g.lon,
        alt_m: g.altM + 80,
        waypoints: useMissionStore.getState().waypoints.map((w) => ({ lat: w.lat, lon: w.lon, altM: w.altM })),
      });
      setAiRouteSummary(
        copilot.operator_summary ??
          `Route optimized · max risk ${((res.constraints.max_risk as number) ?? 0.5) * 100}% · governance ${governanceActive ? 'ON' : 'OFF'}`,
      );
    } catch {
      setAiRouteSummary('Offline planning — using generative world-model routing fallbacks');
    } finally {
      setPlanning(false);
    }
  }

  if (!expanded) {
    return (
      <button
        type="button"
        onClick={() => setExpanded(true)}
        className="pointer-events-auto absolute bottom-20 left-4 z-20 ops-panel px-3 py-2 font-mono text-[10px] text-violet-300 transition-all hover:bg-violet-950/40 flex items-center gap-2"
      >
        <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-violet-500" />
        AI MISSION PLANNING ▸
      </button>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="pointer-events-auto absolute bottom-20 left-4 z-20 w-[min(420px,calc(100vw-2rem))] ops-panel ops-panel-accent p-3 shadow-2xl backdrop-blur-xl"
    >
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-violet-400" />
          <span className="font-mono text-[10px] uppercase tracking-widest text-violet-300">Semantic Copilot</span>
        </div>
        <button type="button" onClick={() => setExpanded(false)} className="text-[10px] text-slate-500 hover:text-slate-300">
          ▾
        </button>
      </div>
      
      <div className="relative mb-3">
        <textarea
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          placeholder="Instruct AI: e.g. Inspect industrial corridor minimizing RF threat, turbulence, and civilian exposure..."
          className="h-20 w-full resize-none rounded-sm border border-slate-700/50 bg-slate-900/60 p-2.5 font-mono text-[11px] leading-relaxed text-slate-200 placeholder:text-slate-600 focus:border-violet-500/50 focus:outline-none"
        />
        {planning && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm">
            <span className="font-mono text-[10px] tracking-widest text-violet-400 animate-pulse">
              ANALYZING TERRAIN & THREATS...
            </span>
          </div>
        )}
      </div>

      <div className="mb-3 flex flex-wrap items-center gap-1 border-b border-slate-800/60 pb-3">
        {TOOLS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTool(t.id)}
            className={`rounded px-2.5 py-1 font-mono text-[9px] uppercase transition-colors ${
              tool === t.id ? 'bg-violet-500/20 text-violet-300 ring-1 ring-violet-500/50' : 'text-slate-500 hover:bg-slate-800/50 hover:text-slate-300'
            }`}
          >
            {t.label}
          </button>
        ))}
        <button
          type="button"
          onClick={() => setGovernanceActive(!governanceActive)}
          className={`ml-auto rounded px-2.5 py-1 font-mono text-[9px] transition-colors ${
            governanceActive ? 'bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/30' : 'text-slate-500 hover:bg-slate-800/50'
          }`}
        >
          GOVERNANCE: {governanceActive ? 'ACTIVE' : 'STANDBY'}
        </button>
      </div>

      <div className="flex gap-2">
        <button
          type="button"
          disabled={planning}
          onClick={() => void generateMission()}
          className="relative flex-1 overflow-hidden rounded-sm bg-violet-600/20 py-2 font-mono text-[10px] tracking-wider text-violet-200 transition-all hover:bg-violet-600/30 disabled:opacity-50"
        >
          {planning ? 'COMPUTING ROUTE...' : 'EXECUTE SEMANTIC PLANNING'}
        </button>
        <button
          type="button"
          onClick={clearMission}
          className="rounded-sm border border-slate-700/50 px-3 py-2 font-mono text-[9px] text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
        >
          RESET
        </button>
      </div>

      <AnimatePresence>
        {(constraints || displayedSummary) && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3 overflow-hidden rounded-sm bg-slate-900/40 p-2 border border-slate-800/50"
          >
            {constraints && (
              <div className="mb-1.5 flex flex-wrap gap-1">
                {Object.entries(constraints)
                  .filter(([, v]) => v)
                  .map(([k]) => (
                    <span key={k} className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[8px] text-slate-300">
                      {k.replace(/_/g, ' ')}
                    </span>
                  ))}
              </div>
            )}
            {displayedSummary && (
              <p className="font-mono text-[10px] leading-relaxed text-cyan-400">
                <span className="text-cyan-600 mr-1">›</span>
                {displayedSummary}
                <span className="animate-pulse">_</span>
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {waypoints.length > 0 && (
        <ul className="mt-3 max-h-24 overflow-y-auto font-mono text-[9px] text-slate-400 space-y-1 pr-1 custom-scrollbar">
          {waypoints.map((w) => (
            <li key={w.id} className="flex items-center justify-between gap-2 rounded bg-slate-800/30 px-2 py-1">
              <span className="flex items-center gap-2">
                <span className="text-violet-400">{w.label}</span>
                <span>{w.lon.toFixed(4)}° {w.lat.toFixed(4)}°</span>
                <span className="text-slate-500">FL{Math.floor(w.altM / 10)}</span>
              </span>
              <button type="button" onClick={() => removeWaypoint(w.id)} className="text-slate-500 hover:text-red-400 transition-colors">
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
    </motion.div>
  );
}