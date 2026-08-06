import React from 'react';
import { useCognitionStore } from '../stores/cognitionStore';

export function AiDebriefCard() {
  const debriefModal = useCognitionStore((s) => s.debriefModal);
  const setDebriefModal = useCognitionStore((s) => s.setDebriefModal);

  if (!debriefModal) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="w-full max-w-2xl rounded-xl border border-purple-500/30 bg-[#050914] text-slate-200 shadow-2xl p-6 relative overflow-hidden font-sans">
        {/* Close Button */}
        <button
          onClick={() => setDebriefModal(false)}
          className="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-mono"
        >
          ✕
        </button>

        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div>
            <span className="px-2.5 py-1 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 text-xs font-mono font-bold">
              POST-FLIGHT AI DEBRIEF
            </span>
            <h2 className="text-xl font-bold text-white tracking-tight mt-1">
              Mission 901 — Grid Alpha Thermal Patrol
            </h2>
          </div>
          <div className="text-right">
            <div className="text-3xl font-extrabold text-emerald-400">94%</div>
            <div className="text-[10px] font-mono text-slate-400">OVERALL MISSION SCORE</div>
          </div>
        </div>

        {/* Performance Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-center">
            <div className="text-[10px] font-mono text-slate-400 uppercase">Battery Efficiency</div>
            <div className="text-xl font-bold text-cyan-400 mt-1">88%</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Optimal Discharge</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-center">
            <div className="text-[10px] font-mono text-slate-400 uppercase">Safety Rating</div>
            <div className="text-xl font-bold text-emerald-400 mt-1">98%</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Zero Infringements</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-center">
            <div className="text-[10px] font-mono text-slate-400 uppercase">Operator Errors</div>
            <div className="text-xl font-bold text-amber-400 mt-1">1</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Late Manual Override</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-center">
            <div className="text-[10px] font-mono text-slate-400 uppercase">AI Interventions</div>
            <div className="text-xl font-bold text-purple-400 mt-1">3</div>
            <div className="text-[10px] text-slate-500 mt-0.5">Wind Nudge / Avoid</div>
          </div>
        </div>

        {/* AI Recommendations */}
        <div className="space-y-3 mb-6">
          <h4 className="text-xs font-mono text-slate-400 uppercase">AI Copilot Suggestions for Next Flight</h4>
          <div className="p-3 rounded bg-slate-900/60 border border-slate-800 text-xs text-slate-300 space-y-1">
            <div className="font-semibold text-cyan-300">1. Increase Corridor Cruise Altitude by +10m</div>
            <div className="text-slate-400">Reduces ground effect turbulence over industrial roof structures by 14%.</div>
          </div>
          <div className="p-3 rounded bg-slate-900/60 border border-slate-800 text-xs text-slate-300 space-y-1">
            <div className="font-semibold text-cyan-300">2. Pre-heat Battery Module 4 to 28°C</div>
            <div className="text-slate-400">Prevents voltage sag during initial high-rate takeoff ascent.</div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
          <button
            onClick={() => setDebriefModal(false)}
            className="px-4 py-2 rounded bg-purple-600 hover:bg-purple-500 text-xs font-mono font-bold text-white shadow-lg"
          >
            Acknowledge & Save Debrief
          </button>
        </div>
      </div>
    </div>
  );
}
