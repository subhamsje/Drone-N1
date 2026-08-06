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
    <header className="relative z-40 flex h-14 shrink-0 items-center border-b border-teal-500/20 bg-slate-950/90 px-4 backdrop-blur-xl">
      {/* Decorative scanline overlay on header */}
      <div className="absolute inset-0 pointer-events-none ops-scanlines opacity-50" />

      {/* Left Sector: Branding & System State */}
      <div className="flex w-1/3 items-center gap-4 z-10 overflow-hidden">
        <div className="flex items-center gap-2 shrink-0">
          <div className="h-4 w-1 bg-teal-500 shadow-[0_0_8px_rgba(20,184,166,0.6)]" />
          <div className="flex flex-col">
            <span className="font-mono text-sm font-bold tracking-[0.2em] text-teal-400 ops-hud-glow">ALTARIA</span>
            <span className="text-[7px] uppercase tracking-[0.1em] text-teal-500/60 leading-none">Command environment</span>
          </div>
        </div>
        
        <div className="hidden lg:flex items-center gap-3 border-l border-slate-800/80 pl-4 overflow-hidden">
          <span className="font-mono text-[9px] text-slate-500 tracking-wider whitespace-nowrap">
            [KERNEL] <span className="text-slate-300">{os ?? 'A.8.0'}</span>
          </span>
          {surv != null && (
            <span className="font-mono text-[9px] text-emerald-400 tracking-wider whitespace-nowrap border-l border-slate-800/80 pl-3">
              [SURV] <span className="font-bold">{(surv * 100).toFixed(1)}%</span>
            </span>
          )}
        </div>
      </div>

      {/* Center Sector: View Controls — Phase 4 */}
      <div className="flex flex-1 justify-center z-10">
        <div className="flex gap-0.5 rounded border border-slate-800/60 p-0.5 bg-black/20">
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
              className={`px-4 py-1.5 font-mono text-[9px] font-bold uppercase tracking-[0.15em] transition-all ${
                viewMode === m.id
                  ? 'bg-teal-500/20 text-teal-300 shadow-[inset_0_0_10px_rgba(20,184,166,0.2)]'
                  : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/40'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>

      {/* Right Sector: Telemetry & Connection */}
      <div className="flex w-1/3 justify-end items-center gap-6 z-10 overflow-hidden">
        {degraded && (
          <span className="hidden xl:inline-block animate-pulse font-mono text-[8px] font-bold text-red-500 tracking-tighter border border-red-900/50 px-1.5 py-0.5 rounded bg-red-950/20">
            ! RENDER DEGRADATION !
          </span>
        )}
        
        <div className="flex flex-col items-end border-r border-slate-800/80 pr-4 mr-1 shrink-0">
          <span className={`font-mono text-[9px] font-bold tracking-widest leading-none ${
            connection === 'connected' ? 'text-teal-400 ops-hud-glow' : 'text-red-500'
          }`}>
            UPLINK_{connection === 'connected' ? 'SECURE' : 'LOST'}
          </span>
          <span className="font-mono text-[8px] text-slate-600 tracking-wider mt-1 leading-none uppercase">
            {latency.toFixed(0)}ms latency {dropped > 0 ? `| ${dropped} drop` : ''}
          </span>
        </div>
      </div>
    </header>
  );
}
