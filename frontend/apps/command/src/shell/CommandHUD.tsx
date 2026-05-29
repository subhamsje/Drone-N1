import { useCognitionStore } from '../stores/cognitionStore';

export function CommandHUD() {
  const connection = useCognitionStore((s) => s.connection);
  const latency = useCognitionStore((s) => s.latencyMs);
  const dropped = useCognitionStore((s) => s.packetsDropped);
  const degraded = useCognitionStore((s) => s.degraded);
  const os = useCognitionStore((s) => s.envelope?.os_version);
  const surv = useCognitionStore((s) => s.envelope?.cognition.composite_survivability);
  const viewMode = useCognitionStore((s) => s.viewMode);
  const setViewMode = useCognitionStore((s) => s.setViewMode);

  return (
    <header className="relative z-20 flex h-14 shrink-0 items-center justify-between border-b border-teal-500/20 bg-slate-950/90 px-6 backdrop-blur-xl">
      {/* Decorative scanline overlay on header */}
      <div className="absolute inset-0 pointer-events-none ops-scanlines opacity-50" />

      <div className="flex items-center gap-6 z-10">
        <div className="flex items-center gap-4">
          <div className="h-4 w-1 bg-teal-500" />
          <div className="flex flex-col">
            <span className="font-mono text-sm font-bold tracking-[0.3em] text-teal-400 ops-hud-glow">ALTARIA</span>
            <span className="text-[8px] uppercase tracking-[0.2em] text-teal-500/60">Planetary Cognition</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3 border-l border-slate-800/80 pl-6">
          <span className="font-mono text-[10px] text-slate-400 tracking-wider">
            [SYS] KERNEL <span className="text-slate-300">{os ?? 'A.3.1'}</span>
          </span>
          {surv != null && (
            <span className="font-mono text-[10px] text-emerald-400 tracking-wider">
              [AI] SURV_CONF <span className="font-bold">{(surv * 100).toFixed(1)}%</span>
            </span>
          )}
          {degraded && (
            <span className="ml-2 font-mono text-[10px] font-bold text-red-500 tracking-widest ops-threat-glow">
              ! RENDER DEGRADATION DETECTED !
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-8 z-10">
        <div className="flex gap-1">
          {(
            [
              { id: 'planet' as const, label: 'PLANET' },
              { id: 'twin' as const, label: 'TWIN' },
              { id: 'dual' as const, label: 'DUAL' },
            ] as const
          ).map((m) => (
            <button
              key={m.id}
              type="button"
              onClick={() => setViewMode(m.id)}
              className={`px-4 py-1.5 font-mono text-[9px] uppercase tracking-widest transition-all border border-transparent ${
                viewMode === m.id
                  ? 'border-teal-500/50 bg-teal-500/10 text-teal-300 ops-hud-glow'
                  : 'text-slate-500 hover:border-slate-700 hover:text-slate-300'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>

        <div className="flex flex-col items-end border-l border-slate-800/80 pl-6">
          <span
            className={`font-mono text-[10px] font-bold tracking-widest ${
              connection === 'connected' ? 'text-teal-400 ops-hud-glow' : 'text-red-500 ops-threat-glow'
            }`}
          >
            UPLINK {connection === 'connected' ? 'SECURE' : 'OFFLINE'}
          </span>
          <span className="font-mono text-[9px] text-slate-500 tracking-wider mt-0.5">
            LATENCY {latency.toFixed(0)}MS {dropped > 0 ? `| DROP ${dropped}` : ''}
          </span>
        </div>
      </div>
    </header>
  );
}
