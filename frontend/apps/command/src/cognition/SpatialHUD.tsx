import { cognitionEngine } from '../config/runtime';
import { useCognitionStore } from '../stores/cognitionStore';

export function SpatialHUD() {
  const envelope = useCognitionStore((s) => s.envelope);
  const t = cognitionEngine().renderState.twin;
  const action = envelope?.cognition?.action ?? t.action;
  const preempt = envelope?.cognition?.preempt;
  const pulse = 0.5 + 0.5 * Math.sin(performance.now() * 0.002);
  const [s5, s15, s30] = t.futureSurvivability;

  return (
    <div className="pointer-events-none absolute inset-0 z-10">
      <div className="ops-scanlines absolute inset-0 opacity-40" />
      <div className="absolute left-0 top-0 h-20 w-20 border-l-2 border-t border-cyan-500/25" />
      <div className="absolute right-0 top-0 h-20 w-20 border-r-2 border-t border-cyan-500/25" />
      <div className="absolute bottom-0 left-0 h-20 w-20 border-b border-l-2 border-cyan-500/25" />
      <div className="absolute bottom-0 right-0 h-20 w-20 border-b border-r-2 border-cyan-500/25" />

      <div className="absolute left-4 top-4 ops-panel ops-panel-accent px-3 py-2">
        <p className="font-mono text-[9px] uppercase tracking-[0.2em] text-slate-500">Cognition battlefield</p>
        <p className="font-mono text-sm text-cyan-300">{t.uavId}</p>
        <p className="font-mono text-[10px] text-emerald-400" style={{ opacity: 0.7 + pulse * 0.3 }}>
          NOW {(t.survivability * 100).toFixed(1)}% → 5s {(s5 * 100).toFixed(0)}% → 30s {(s30 * 100).toFixed(0)}%
        </p>
      </div>

      <div className="absolute right-4 top-4 ops-panel px-3 py-2 text-right">
        <p className="font-mono text-[9px] uppercase text-slate-600">Predictive futures</p>
        {t.branches.map((b) => (
          <p key={b.label} className="font-mono text-[9px] text-slate-400">
            <span className="text-sky-400">{b.label}</span> {(b.probability * 100).toFixed(0)}% · surv{' '}
            {(b.survivability * 100).toFixed(0)}%
          </p>
        ))}
        <p className="mt-1 font-mono text-[10px] text-red-400/90">
          CRASH PATH · {(t.crashRisk * 100).toFixed(1)}%
        </p>
        <p className="font-mono text-[9px] text-violet-400">RECOVERY {(t.recoveryProb * 100).toFixed(0)}%</p>
      </div>

      <div
        className={`absolute bottom-16 left-1/2 -translate-x-1/2 rounded border px-4 py-1.5 font-mono text-[11px] tracking-wider ${
          preempt
            ? 'ops-threat-glow border-orange-500/50 bg-orange-950/40 text-orange-200'
            : 'border-cyan-800/50 bg-slate-950/80 text-cyan-200'
        }`}
      >
        {preempt ? `PREEMPT · ${preempt}` : `COGNITION · ${action}`}
      </div>

      <div className="absolute bottom-4 left-4 flex gap-3 font-mono text-[8px] text-slate-600">
        <span>GPS ±{(t.gpsUncertainty * 100).toFixed(0)}%</span>
        <span>VIS ±{(t.visionUncertainty * 100).toFixed(0)}%</span>
        <span>THERM {(t.thermalLoad * 100).toFixed(0)}%</span>
      </div>

      {t.threatLevel > 0.12 && (
        <div className="absolute right-4 bottom-24 ops-panel border-orange-500/30 px-2 py-1 font-mono text-[10px] text-orange-300">
          THREAT {(t.threatLevel * 100).toFixed(0)}%
        </div>
      )}
      {t.rfDenied > 0.08 && (
        <div className="absolute left-4 bottom-24 ops-panel border-yellow-500/30 px-2 py-1 font-mono text-[10px] text-yellow-300">
          RF DENIED {(t.rfDenied * 100).toFixed(0)}%
        </div>
      )}
    </div>
  );
}
