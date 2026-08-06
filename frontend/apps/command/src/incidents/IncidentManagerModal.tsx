import React from 'react';
import { useCognitionStore } from '../stores/cognitionStore';

export function IncidentManagerModal() {
  const activeIncidentModal = useCognitionStore((s) => s.activeIncidentModal);
  const setActiveIncidentModal = useCognitionStore((s) => s.setActiveIncidentModal);

  if (!activeIncidentModal) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="w-full max-w-3xl rounded-xl border border-rose-500/30 bg-[#050914] text-slate-200 shadow-2xl p-6 relative overflow-hidden font-sans">
        {/* Close Button */}
        <button
          onClick={() => setActiveIncidentModal(false)}
          className="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-mono"
        >
          ✕
        </button>

        {/* Header */}
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-4 mb-4">
          <span className="px-2.5 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-xs font-mono font-bold">
            INCIDENT REPORT #INC-882
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            GPS Multipath & Wind Spike Emergency Landing
          </h2>
        </div>

        {/* Content Body */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left 2 cols */}
          <div className="md:col-span-2 space-y-4">
            <div>
              <h4 className="text-xs font-mono text-slate-400 uppercase">AI Root Cause Analysis</h4>
              <p className="text-xs text-slate-200 mt-1 leading-relaxed bg-slate-900/80 p-3 rounded border border-slate-800">
                At t=142.4s during Mission 880, GPS lock degraded from 98% to 24% due to multipath reflection from nearby structural facade, coinciding with a 14.8 m/s localized wind gust. EKF Rollback Buffer engaged and ORB-SLAM3 VIO fallback assumed primary odometry.
              </p>
            </div>

            <div>
              <h4 className="text-xs font-mono text-slate-400 uppercase">Chronological Event Timeline</h4>
              <div className="space-y-2 mt-1">
                <div className="p-2 rounded bg-slate-900/60 border border-slate-800 text-xs flex justify-between">
                  <span className="font-mono text-cyan-400">14:12:04</span>
                  <span>Normal Flight Corridor (Speed 12.4 m/s)</span>
                  <span className="text-emerald-400">NOMINAL</span>
                </div>
                <div className="p-2 rounded bg-slate-900/60 border border-rose-500/30 text-xs flex justify-between">
                  <span className="font-mono text-rose-400">14:14:22</span>
                  <span>GPS Trust Dropped &lt; 30% • Wind 14.8 m/s</span>
                  <span className="text-rose-400">WARNING</span>
                </div>
                <div className="p-2 rounded bg-slate-900/60 border border-purple-500/30 text-xs flex justify-between">
                  <span className="font-mono text-purple-400">14:14:23</span>
                  <span>ORB-SLAM3 VIO Fallback Activated by RecoveryAgent</span>
                  <span className="text-purple-400">RECOVERY</span>
                </div>
                <div className="p-2 rounded bg-slate-900/60 border border-emerald-500/30 text-xs flex justify-between">
                  <span className="font-mono text-emerald-400">14:15:02</span>
                  <span>Touchdown at Emergency LZ Alpha (Slope &lt; 2°)</span>
                  <span className="text-emerald-400 font-bold">SUCCESS</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-mono text-slate-400 uppercase">AI Recommendation & Offline Memory</h4>
              <div className="p-3 rounded bg-purple-500/10 border border-purple-500/30 text-xs text-purple-200">
                This incident experience has been logged to the Offline Retraining Store. Recommend updating corridor clearance buffer by +5.0m near structural facade Alpha.
              </div>
            </div>
          </div>

          {/* Right 1 col: Details & Actions */}
          <div className="space-y-4">
            <div className="p-3 rounded bg-slate-900/80 border border-slate-800 space-y-2 text-xs">
              <div className="text-[10px] font-mono text-slate-400 uppercase">Incident Details</div>
              <div className="flex justify-between font-mono">
                <span className="text-slate-400">UAV ID:</span>
                <span className="text-white">Altaria-Alpha</span>
              </div>
              <div className="flex justify-between font-mono">
                <span className="text-slate-400">Pilot in Command:</span>
                <span className="text-white">Capt. Vance</span>
              </div>
              <div className="flex justify-between font-mono">
                <span className="text-slate-400">Damages:</span>
                <span className="text-emerald-400">ZERO (0.00$)</span>
              </div>
              <div className="flex justify-between font-mono">
                <span className="text-slate-400">Airworthiness:</span>
                <span className="text-cyan-400">PASSED</span>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <button 
                onClick={() => setActiveIncidentModal(false)}
                className="w-full py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-xs font-mono font-bold text-white shadow-lg"
              >
                Sign Off & Close Incident
              </button>
              <button className="w-full py-2 rounded bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-300 border border-slate-700">
                Export FAA/EASA Audit Log PDF
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
