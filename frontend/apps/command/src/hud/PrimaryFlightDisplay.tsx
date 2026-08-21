import React, { useState, useEffect } from 'react';
import { Compass, Gauge } from 'lucide-react';
import { useCognitionStore } from '../stores/cognitionStore';

export const PrimaryFlightDisplay: React.FC = () => {
  const [pitch, setPitch] = useState(-3.2); // degrees
  const [roll, setRoll] = useState(4.5); // degrees
  const [airspeed, setAirspeed] = useState(14.8); // m/s
  const [altitude, setAltitude] = useState(48.5); // meters AGL
  const [heading, setHeading] = useState(42); // degrees compass

  // Live gyro oscillation simulation for hyper-realism
  useEffect(() => {
    const interval = setInterval(() => {
      setPitch(p => parseFloat((p + (Math.random() - 0.5) * 0.4).toFixed(1)));
      setRoll(r => parseFloat((r + (Math.random() - 0.5) * 0.6).toFixed(1)));
      setAirspeed(s => parseFloat((s + (Math.random() - 0.5) * 0.2).toFixed(1)));
      setAltitude(a => parseFloat((a + (Math.random() - 0.5) * 0.3).toFixed(1)));
      setHeading(h => (h + (Math.random() > 0.5 ? 1 : -1) * 0.2 + 360) % 360);
    }, 150);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="absolute top-16 left-6 z-20 w-64 bg-[#080c14]/90 border border-slate-800/80 rounded-2xl p-4 backdrop-blur-xl shadow-2xl font-mono text-xs select-none">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2 mb-3">
        <div className="flex items-center gap-1.5 text-sky-400 font-bold text-[11px]">
          <Gauge className="w-3.5 h-3.5" />
          <span>PRIMARY FLIGHT DISPLAY (PFD)</span>
        </div>
        <span className="text-[10px] text-emerald-400 font-semibold bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/30">
          EKF2 AHRS
        </span>
      </div>

      {/* Main Artificial Horizon Indicator */}
      <div className="relative h-32 rounded-xl overflow-hidden border border-slate-800 bg-[#050811] flex items-center justify-center">
        {/* Sky / Ground Pitch Divider */}
        <div
          style={{
            transform: `rotate(${-roll}deg) translateY(${pitch * 2.2}px)`,
          }}
          className="absolute inset-[-50%] transition-transform duration-100 flex flex-col pointer-events-none"
        >
          {/* Sky (Blue-Slate) */}
          <div className="flex-1 bg-gradient-to-b from-sky-950/90 to-sky-900/60 border-b border-sky-400/80 flex items-end justify-center pb-1">
            <div className="w-20 border-t border-sky-400/50 flex justify-between text-[8px] text-sky-300">
              <span>+10°</span>
              <span>+10°</span>
            </div>
          </div>

          {/* Ground (Dark Earth) */}
          <div className="flex-1 bg-gradient-to-b from-[#1a130e] to-[#0d0a07] border-t border-amber-500/60 flex items-start justify-center pt-1">
            <div className="w-20 border-b border-amber-500/50 flex justify-between text-[8px] text-amber-300">
              <span>-10°</span>
              <span>-10°</span>
            </div>
          </div>
        </div>

        {/* Center Aircraft Reticle (Fixed crosshairs) */}
        <div className="relative z-10 flex items-center justify-center pointer-events-none">
          <div className="w-8 h-0.5 bg-sky-400 shadow-md shadow-sky-400/50" />
          <div className="w-2.5 h-2.5 rounded-full border border-white mx-1 bg-sky-500/30" />
          <div className="w-8 h-0.5 bg-sky-400 shadow-md shadow-sky-400/50" />
        </div>

        {/* Left Airspeed Tape */}
        <div className="absolute left-1.5 top-2 bottom-2 w-10 bg-slate-950/80 border border-slate-800/80 rounded p-1 flex flex-col justify-between text-[10px] text-slate-300 font-bold z-10">
          <div className="text-[8px] text-slate-500 uppercase font-mono">SPD</div>
          <div className="text-sky-300 text-xs font-extrabold">{airspeed}</div>
          <div className="text-[8px] text-slate-500">m/s</div>
        </div>

        {/* Right Altitude Tape */}
        <div className="absolute right-1.5 top-2 bottom-2 w-11 bg-slate-950/80 border border-slate-800/80 rounded p-1 flex flex-col justify-between text-[10px] text-slate-300 font-bold text-right z-10">
          <div className="text-[8px] text-slate-500 uppercase font-mono">ALT</div>
          <div className="text-emerald-300 text-xs font-extrabold">{altitude}</div>
          <div className="text-[8px] text-slate-500">m AGL</div>
        </div>
      </div>

      {/* Bottom Compass Heading Ribbon */}
      <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-300">
        <div className="flex items-center gap-1">
          <Compass className="w-3.5 h-3.5 text-sky-400" />
          <span>HDG: <strong className="text-white">{heading.toFixed(0)}°</strong></span>
        </div>
        <div className="text-slate-400 text-[10px]">
          PITCH: <strong className="text-slate-200">{pitch}°</strong> • ROLL: <strong className="text-slate-200">{roll}°</strong>
        </div>
      </div>
    </div>
  );
};
