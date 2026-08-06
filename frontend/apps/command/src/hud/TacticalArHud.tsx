import React from 'react';
import { useCognitionStore } from '../stores/cognitionStore';

export function TacticalArHud() {
  const envelope = useCognitionStore((s) => s.envelope);
  const opticMode = useCognitionStore((s) => s.opticMode);
  const setOpticMode = useCognitionStore((s) => s.setOpticMode);
  const workspaceMode = useCognitionStore((s) => s.workspaceMode);

  if (workspaceMode !== 'command_globe') return null;

  const alt = envelope?.pose?.altitude_m?.toFixed(1) ?? '120.5';
  const ned = envelope?.pose?.velocity_ned;
  const speed = ned ? Math.sqrt(ned[0] ** 2 + ned[1] ** 2 + ned[2] ** 2).toFixed(1) : '12.4';
  const heading = Math.round(envelope?.pose?.heading_deg ?? 185);

  return (
    <div className="absolute inset-0 pointer-events-none z-20 overflow-hidden font-sans">
      {/* Top Heading Tape */}
      <div className="absolute top-16 left-1/2 -translate-x-1/2 bg-slate-950/80 backdrop-blur-md px-6 py-1.5 rounded-full border border-cyan-500/30 text-xs font-mono text-cyan-400 flex items-center space-x-6 shadow-xl pointer-events-auto">
        <span>150°</span>
        <span>165°</span>
        <span className="text-white font-bold text-sm bg-cyan-500/20 px-2 py-0.5 rounded border border-cyan-400">
          ▲ {heading}° HDG
        </span>
        <span>205°</span>
        <span>220°</span>
      </div>

      {/* Left Altitude Ladder */}
      <div className="absolute top-1/3 left-6 -translate-y-1/2 bg-slate-950/80 backdrop-blur-md px-3 py-4 rounded-xl border border-cyan-500/30 font-mono text-xs text-cyan-400 space-y-2 text-center pointer-events-auto">
        <div className="text-[9px] text-slate-400 uppercase">ALT (M)</div>
        <div>140.0</div>
        <div>130.0</div>
        <div className="text-white font-bold text-sm bg-cyan-500/30 py-1 rounded border border-cyan-400">
          ▶ {alt}m
        </div>
        <div>110.0</div>
        <div>100.0</div>
      </div>

      {/* Right Airspeed Tape */}
      <div className="absolute top-1/3 right-6 -translate-y-1/2 bg-slate-950/80 backdrop-blur-md px-3 py-4 rounded-xl border border-cyan-500/30 font-mono text-xs text-cyan-400 space-y-2 text-center pointer-events-auto">
        <div className="text-[9px] text-slate-400 uppercase">SPEED (M/S)</div>
        <div>18.0</div>
        <div>15.0</div>
        <div className="text-white font-bold text-sm bg-cyan-500/30 py-1 rounded border border-cyan-400">
          ◀ {speed} m/s
        </div>
        <div>10.0</div>
        <div>08.0</div>
      </div>

      {/* Bottom Center Multi-Optic Shader Switcher */}
      <div className="absolute bottom-16 left-1/2 -translate-x-1/2 bg-slate-950/90 backdrop-blur-md px-4 py-2 rounded-full border border-slate-800 flex items-center space-x-2 text-xs font-mono pointer-events-auto shadow-2xl">
        <span className="text-[10px] text-slate-400 uppercase mr-2">MULTI-OPTIC:</span>
        {(['satellite', 'tactical', 'thermal', 'nightvision', 'wireframe'] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => setOpticMode(mode)}
            className={`px-3 py-1 rounded-full text-xs transition-all uppercase ${
              opticMode === mode
                ? 'bg-cyan-500 text-black font-bold shadow-md shadow-cyan-500/40'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            {mode}
          </button>
        ))}
      </div>
    </div>
  );
}
