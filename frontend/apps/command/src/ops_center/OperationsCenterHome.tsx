import React, { useState } from 'react';
import { useCognitionStore } from '../stores/cognitionStore';
import { useOperatingStore } from '../stores/operatingStore';

export function OperationsCenterHome() {
  const setWorkspaceMode = useCognitionStore((s) => s.setWorkspaceMode);
  const setDebriefModal = useCognitionStore((s) => s.setDebriefModal);
  const setActiveIncidentModal = useCognitionStore((s) => s.setActiveIncidentModal);
  const envelope = useCognitionStore((s) => s.envelope);
  const confidence = useCognitionStore((s) => s.confidence);
  const sensorTrust = useCognitionStore((s) => s.sensorTrust);

  const [activeTab, setActiveTab] = useState<'overview' | 'queue' | 'incidents' | 'topology' | 'analytics'>('overview');

  const runningMissions = [
    { id: 'MSN-902', name: 'Grid Alpha Thermal Patrol', drone: 'Altaria-Alpha', status: 'EXECUTING', battery: 84, risk: 'LOW', progress: 68 },
    { id: 'MSN-903', name: 'Perimeter ISR Scan', drone: 'UAV-101', status: 'IN_TRANSIT', battery: 92, risk: 'NOMINAL', progress: 34 },
    { id: 'MSN-904', name: 'Coastal Wind Corridor', drone: 'UAV-102', status: 'RECOVERY_EVAL', battery: 41, risk: 'MEDIUM', progress: 89 },
  ];

  const pendingApprovals = [
    { id: 'APP-104', name: 'Industrial Solar Array Mesh', pilot: 'Capt. Vance', riskScore: '12%', status: 'PENDING_APPROVAL' },
    { id: 'APP-105', name: 'Nighttime Port Patrol', pilot: 'Lt. Chen', riskScore: '24%', status: 'PENDING_SIMULATION' },
  ];

  const recentIncidents = [
    { id: 'INC-882', msn: 'MSN-880', type: 'GPS Multipath & Wind Spike', severity: 'WARNING', time: '14 mins ago', status: 'RESOLVED_BY_AI' },
    { id: 'INC-881', msn: 'MSN-874', type: 'Motor 2 Thermal Deg', severity: 'CRITICAL', time: '1 hour ago', status: 'LANDED_EMERGENCY_LZ' },
  ];

  return (
    <div className="h-full w-full bg-[#010409] text-slate-200 p-6 overflow-y-auto font-sans">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-slate-800 pb-5 mb-6 gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-mono font-medium text-cyan-400 border border-cyan-500/30">
              <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse mr-2" />
              ALTARIA OS v8.0 — OPERATIONS CENTER
            </span>
            <span className="text-xs font-mono text-slate-500">TENANT: DEFAULT-FLEET</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white mt-2">
            Executive Mission Command & Operations Hub
          </h1>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setWorkspaceMode('command_globe')}
            className="flex items-center space-x-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-cyan-600/20 transition-all"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 002 2h1.5a2.5 2.5 0 002.5-2.5V14M12 21a9 9 0 100-18 9 9 0 000 18z" />
            </svg>
            <span>Launch 3D Command Globe</span>
          </button>
          <button
            onClick={() => setWorkspaceMode('mission_studio')}
            className="flex items-center space-x-2 rounded-lg bg-slate-800 hover:bg-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 border border-slate-700 transition-all"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <span>Node Mission Studio</span>
          </button>
        </div>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 backdrop-blur-md">
          <div className="text-xs font-mono uppercase text-slate-400">Active Fleet Units</div>
          <div className="text-3xl font-bold text-white mt-1 flex items-baseline justify-between">
            <span>4 UAVs</span>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">100% READY</span>
          </div>
          <div className="text-xs text-slate-400 mt-2">Altaria-Alpha (Lead), UAV-101, UAV-102, UAV-103</div>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 backdrop-blur-md">
          <div className="text-xs font-mono uppercase text-slate-400">Global AI Confidence</div>
          <div className="text-3xl font-bold text-cyan-400 mt-1 flex items-baseline justify-between">
            <span>94.8%</span>
            <span className="text-xs font-mono text-cyan-400">NAV: {confidence.nav}%</span>
          </div>
          <div className="text-xs text-slate-400 mt-2">Vision: {confidence.vision}% | Weather: {confidence.weather}%</div>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 backdrop-blur-md">
          <div className="text-xs font-mono uppercase text-slate-400">Sensor Trust Matrix</div>
          <div className="text-3xl font-bold text-emerald-400 mt-1 flex items-baseline justify-between">
            <span>{sensorTrust.gps}%</span>
            <span className="text-xs font-mono text-slate-400">VIO: {sensorTrust.vio}%</span>
          </div>
          <div className="text-xs text-slate-400 mt-2">Baro: {sensorTrust.baro}% | IMU: {sensorTrust.imu}%</div>
        </div>

        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 backdrop-blur-md">
          <div className="text-xs font-mono uppercase text-slate-400">Autonomous Memory Lake</div>
          <div className="text-3xl font-bold text-purple-400 mt-1 flex items-baseline justify-between">
            <span>1,420 Experiences</span>
            <span className="text-xs font-mono text-purple-400">OFFLINE SYNC</span>
          </div>
          <div className="text-xs text-slate-400 mt-2">Validated offline model v2.4 active</div>
        </div>
      </div>

      {/* Main Grid: Left Column (Live Topology & Running Missions) | Right Column (Incidents & Approvals) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        
        {/* Left Column: 2 Spans */}
        <div className="lg:col-span-2 space-y-6">
          {/* Live System Architecture Topology Card */}
          <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-ping" />
                <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-200">
                  Live System Architecture & Runtime Topology
                </h3>
              </div>
              <span className="text-xs font-mono text-emerald-400">ALL PIPELINES GREEN</span>
            </div>

            {/* Pipeline Flow Diagram */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
              <div className="p-3 rounded-lg bg-slate-950/80 border border-emerald-500/30">
                <div className="text-[10px] font-mono text-slate-500">HARDWARE LAYER</div>
                <div className="text-xs font-bold text-emerald-400 mt-1">PX4 / MAVSDK</div>
                <div className="text-[10px] text-slate-400 mt-1">UDP:14540 • 200ms</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/80 border border-emerald-500/30">
                <div className="text-[10px] font-mono text-slate-500">STATE FUSION</div>
                <div className="text-xs font-bold text-emerald-400 mt-1">20D EKF Buffer</div>
                <div className="text-[10px] text-slate-400 mt-1">Rollback • 20 Steps</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/80 border border-emerald-500/30">
                <div className="text-[10px] font-mono text-slate-500">COGNITION KERNEL</div>
                <div className="text-xs font-bold text-cyan-400 mt-1">4-Quadrant Risk</div>
                <div className="text-[10px] text-slate-400 mt-1">MPC Controller N=5</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-950/80 border border-purple-500/30">
                <div className="text-[10px] font-mono text-slate-500">DECISION & UI</div>
                <div className="text-xs font-bold text-purple-400 mt-1">WebSocket Stream</div>
                <div className="text-[10px] text-slate-400 mt-1">12Hz RxJS Throttled</div>
              </div>
            </div>
          </div>

          {/* Running Missions Center */}
          <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-200">
                Active Operational Missions
              </h3>
              <button 
                onClick={() => setWorkspaceMode('command_globe')}
                className="text-xs font-mono text-cyan-400 hover:underline"
              >
                View on Globe &rarr;
              </button>
            </div>

            <div className="space-y-3">
              {runningMissions.map((msn) => (
                <div key={msn.id} className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 hover:border-slate-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs text-cyan-400 font-bold">{msn.id}</span>
                      <span className="text-sm font-semibold text-white">{msn.name}</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-1 flex items-center space-x-4">
                      <span>UAV: {msn.drone}</span>
                      <span>Battery: {msn.battery}%</span>
                      <span>Risk: <strong className="text-emerald-400">{msn.risk}</strong></span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full md:w-48">
                    <div className="flex justify-between text-xs font-mono text-slate-400 mb-1">
                      <span>PROGRESS</span>
                      <span>{msn.progress}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-full" style={{ width: `${msn.progress}%` }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: 1 Span (Incidents & Approvals) */}
        <div className="space-y-6">
          {/* Incident Management Widget */}
          <div className="rounded-xl border border-rose-500/20 bg-slate-900/60 p-5 backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <span className="h-2 w-2 rounded-full bg-rose-500 animate-pulse" />
                <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-rose-300">
                  Incident Management
                </h3>
              </div>
              <button 
                onClick={() => setActiveIncidentModal(true)}
                className="text-xs font-mono text-rose-400 hover:underline"
              >
                Inspect All &rarr;
              </button>
            </div>

            <div className="space-y-3">
              {recentIncidents.map((inc) => (
                <div 
                  key={inc.id} 
                  onClick={() => setActiveIncidentModal(true)}
                  className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 hover:border-rose-500/40 cursor-pointer transition-all"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-rose-400 font-bold">{inc.id} ({inc.msn})</span>
                    <span className="text-[10px] font-mono text-slate-400">{inc.time}</span>
                  </div>
                  <div className="text-xs font-medium text-slate-200 mt-1">{inc.type}</div>
                  <div className="text-[10px] font-mono text-emerald-400 mt-1">STATUS: {inc.status}</div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Mission Debrief Quick Trigger */}
          <div className="rounded-xl border border-purple-500/20 bg-slate-900/60 p-5 backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
              <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-purple-300">
                Post-Flight AI Debrief
              </h3>
              <span className="text-xs font-mono text-purple-400">LAST MISSION</span>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Review post-flight score card, battery efficiency, safety rating, and AI intervention suggestions.
            </p>
            <button
              onClick={() => setDebriefModal(true)}
              className="w-full py-2.5 rounded-lg bg-purple-600/20 border border-purple-500/40 text-purple-200 text-xs font-mono font-semibold hover:bg-purple-600/30 transition-all flex items-center justify-center space-x-2"
            >
              <span>View Mission 901 Debrief Score Card</span>
            </button>
          </div>

          {/* Pending Approval Pipeline */}
          <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-md">
            <h3 className="text-sm font-mono font-bold uppercase tracking-wider text-slate-200 border-b border-slate-800 pb-3 mb-4">
              Enterprise Approval Pipeline
            </h3>
            <div className="space-y-3">
              {pendingApprovals.map((app) => (
                <div key={app.id} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                  <div>
                    <div className="text-xs font-semibold text-slate-200">{app.name}</div>
                    <div className="text-[10px] font-mono text-slate-400 mt-0.5">Pilot: {app.pilot} | Risk: {app.riskScore}</div>
                  </div>
                  <button className="text-[10px] font-mono px-2 py-1 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/20">
                    APPROVE
                  </button>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
