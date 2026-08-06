import React from 'react';
import { useCognitionStore } from '../stores/cognitionStore';

export function FpvVisionHud() {
  const fpvExpanded = useCognitionStore((s) => s.fpvExpanded);
  const setFpvExpanded = useCognitionStore((s) => s.setFpvExpanded);
  const opticMode = useCognitionStore((s) => s.opticMode);

  return (
    <div
      className={`transition-all duration-300 backdrop-blur-md rounded-xl border border-cyan-500/30 bg-slate-950/90 overflow-hidden shadow-2xl ${
        fpvExpanded
          ? 'fixed inset-12 z-40'
          : 'absolute bottom-20 right-6 w-80 h-48 z-30'
      }`}
    >
      {/* Feed Header */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900/90 border-b border-slate-800 text-xs font-mono">
        <div className="flex items-center space-x-2">
          <span className="h-2 w-2 rounded-full bg-rose-500 animate-ping" />
          <span className="font-bold text-white uppercase">FPV AI VISION FEED — 1080P 60FPS</span>
        </div>
        <div className="flex items-center space-x-2 text-slate-400">
          <span className="text-[10px] text-cyan-400">OPTIC: {opticMode.toUpperCase()}</span>
          <button
            onClick={() => setFpvExpanded(!fpvExpanded)}
            className="hover:text-white"
          >
            {fpvExpanded ? '🗗' : '🗖'}
          </button>
        </div>
      </div>

      {/* Video / AI Canvas Viewport */}
      <div className="relative w-full h-[calc(100%-30px)] bg-[#020617] flex items-center justify-center overflow-hidden">
        {/* Simulated Thermal / Night Vision Shader Filter */}
        <div
          className={`absolute inset-0 pointer-events-none ${
            opticMode === 'thermal'
              ? 'bg-amber-500/20 mix-blend-color-dodge'
              : opticMode === 'nightvision'
              ? 'bg-emerald-500/20 mix-blend-color-dodge'
              : opticMode === 'wireframe'
              ? 'bg-cyan-500/10'
              : ''
          }`}
        />

        {/* Tactical Crosshair Center */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-40">
          <div className="w-12 h-12 border border-cyan-400 rounded-full flex items-center justify-center">
            <div className="w-1 h-1 bg-cyan-400 rounded-full" />
          </div>
        </div>

        {/* AI Object Bounding Box #1 (Vehicle) */}
        <div className="absolute top-[25%] left-[30%] w-24 h-16 border-2 border-emerald-400 rounded p-1 flex flex-col justify-between animate-pulse">
          <div className="flex justify-between items-start text-[9px] font-mono font-bold text-emerald-400 bg-emerald-950/80 px-1 rounded">
            <span>TARGET #01</span>
            <span>98.4%</span>
          </div>
          <div className="text-[8px] font-mono text-emerald-300">VEHICLE • 42.1m</div>
        </div>

        {/* AI Object Bounding Box #2 (Human/Threat) */}
        <div className="absolute top-[45%] right-[25%] w-16 h-24 border-2 border-rose-500 rounded p-1 flex flex-col justify-between">
          <div className="flex justify-between items-start text-[9px] font-mono font-bold text-rose-400 bg-rose-950/80 px-1 rounded">
            <span>THREAT #02</span>
            <span>94.1%</span>
          </div>
          <div className="text-[8px] font-mono text-rose-300">HUMAN • LOCK_ON</div>
        </div>

        {/* FPV Telemetry HUD Watermark */}
        <div className="absolute bottom-2 left-3 text-[10px] font-mono text-cyan-400 space-y-0.5 pointer-events-none bg-slate-950/60 p-1.5 rounded border border-slate-800">
          <div>GIMBAL PITCH: -45° | YAW: 182°</div>
          <div>LATENCY: 12ms | CODEC: H.265</div>
        </div>
      </div>
    </div>
  );
}
