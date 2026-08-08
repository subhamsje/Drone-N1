import React, { useState } from 'react';
import { Panel } from '../../components/composites/Panel';
import { MetricCard } from '../../components/composites/MetricCard';
import { Button } from '../../components/primitives/Button';
import { Badge } from '../../components/primitives/Badge';
import { useFleetStore } from '../../global/fleetState';
import { useTelemetryStore } from '../../global/telemetryState';
import { useUiStore } from '../../global/uiState';
import { Activity, ShieldCheck, Zap, AlertTriangle, Play, RefreshCw, CheckCircle2 } from 'lucide-react';

export const OpsDashboard: React.FC = () => {
  const { fleetUnits, focusedUavId, setFocusedUavId } = useFleetStore();
  const { batteryPct, gpsSats, rssiDbm, latencyMs } = useTelemetryStore();
  const { setWorkspaceMode, setIntelModalOpen } = useUiStore();

  const [queue, setQueue] = useState([
    { id: 'MSN-902', name: 'Grid Alpha Thermal Patrol', drone: 'Altaria-Alpha', status: 'EXECUTING', battery: 94, risk: 'LOW' },
    { id: 'MSN-903', name: 'Perimeter ISR Scan', drone: 'UAV-101', status: 'IN_TRANSIT', battery: 91, risk: 'NOMINAL' },
    { id: 'MSN-904', name: 'Coastal Wind Corridor', drone: 'UAV-102', status: 'RECOVERY_EVAL', battery: 89, risk: 'MEDIUM' },
  ]);

  const [approvals, setApprovals] = useState([
    { id: 'APP-104', name: 'Industrial Solar Array Mesh', pilot: 'Capt. Vance', risk: '12%', approved: false },
    { id: 'APP-105', name: 'Nighttime Port Patrol', pilot: 'Lt. Chen', risk: '24%', approved: false },
  ]);

  const toggleApproval = (id: string) => {
    setApprovals(approvals.map(a => a.id === id ? { ...a, approved: !a.approved } : a));
  };

  return (
    <div className="h-full w-full bg-[#080c14] text-slate-200 p-6 flex flex-col font-sans overflow-y-auto space-y-6 select-none">
      {/* Top Header Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 shrink-0">
        <MetricCard
          label="Active Fleet Readiness"
          value={fleetUnits.length}
          unit="UAV Units"
          trend="100% OPERATIONAL"
          statusColor="emerald"
        />
        <MetricCard
          label="RTK GNSS Constellation"
          value={gpsSats}
          unit="Satellites"
          trend="3D FIX NOMINAL"
          statusColor="sky"
        />
        <MetricCard
          label="5G Private Telemetry"
          value={rssiDbm}
          unit="dBm"
          trend={`${latencyMs}ms RTT`}
          statusColor="emerald"
        />
        <MetricCard
          label="Fleet Power Capacity"
          value={batteryPct}
          unit="%"
          trend="15.8V 4S LiPo"
          statusColor="emerald"
        />
      </div>

      {/* Main Grid: Mission Queue & Fleet Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        {/* Left 2 Columns: Mission Queue & Approvals */}
        <div className="lg:col-span-2 space-y-6 flex flex-col">
          <Panel
            title="Active Cognitive Operations Queue"
            badge="LIVE EKF"
            badgeVariant="info"
            actions={[
              <Button key="studio" size="sm" variant="secondary" onClick={() => setWorkspaceMode('mission_studio')}>
                Mission Studio &rarr;
              </Button>
            ]}
          >
            <div className="space-y-3">
              {queue.map((m) => (
                <div
                  key={m.id}
                  className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 flex items-center justify-between font-mono text-xs hover:border-slate-700 transition-colors"
                >
                  <div className="space-y-0.5">
                    <div className="font-bold text-slate-100 flex items-center gap-2">
                      <span>{m.name}</span>
                      <span className="text-[10px] text-slate-500 font-normal">[{m.id}]</span>
                    </div>
                    <div className="text-[11px] text-slate-400">Assigned: <strong className="text-sky-400">{m.drone}</strong> • Battery: {m.battery}%</div>
                  </div>

                  <div className="flex items-center gap-3">
                    <Badge variant={m.risk === 'LOW' || m.risk === 'NOMINAL' ? 'success' : 'warning'}>
                      {m.risk} RISK
                    </Badge>
                    <Badge variant="info" pulse>
                      {m.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          {/* Enterprise Approval Pipeline */}
          <Panel title="Enterprise Operational Approvals" badge="STANAG 4586" badgeVariant="neutral">
            <div className="space-y-3">
              {approvals.map((app) => (
                <div
                  key={app.id}
                  className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 flex items-center justify-between font-mono text-xs"
                >
                  <div>
                    <div className="font-bold text-slate-200">{app.name}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">Operator: {app.pilot} • Threat Profile: {app.risk}</div>
                  </div>

                  <Button
                    size="sm"
                    variant={app.approved ? 'secondary' : 'primary'}
                    onClick={() => toggleApproval(app.id)}
                    className={app.approved ? 'text-emerald-400 border-emerald-500/40' : ''}
                  >
                    {app.approved ? 'APPROVED ✓' : 'APPROVE MISSION'}
                  </Button>
                </div>
              ))}
            </div>
          </Panel>
        </div>

        {/* Right Column: Fleet Status & AI Copilot */}
        <div className="space-y-6 flex flex-col">
          <Panel title="Multi-Vehicle Fleet Units" badge="4 UNITS READY" badgeVariant="success">
            <div className="space-y-2.5">
              {fleetUnits.map((uav) => {
                const isSelected = focusedUavId === uav.id;
                return (
                  <div
                    key={uav.id}
                    onClick={() => setFocusedUavId(uav.id)}
                    className={`p-3 rounded-xl border cursor-pointer transition-all font-mono text-xs ${
                      isSelected
                        ? 'bg-slate-900 border-sky-500/80 shadow-md shadow-sky-500/10'
                        : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-100">{uav.id}</span>
                      <span className="text-[10px] text-emerald-400 font-bold">{uav.battery}% SOC</span>
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1 flex justify-between">
                      <span>Role: {uav.role}</span>
                      <span>{uav.voltage}V</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </Panel>

          {/* AI Copilot Card */}
          <Panel title="Planetary Copilot Intelligence" badge="1,420 EXP" badgeVariant="info">
            <p className="text-slate-400 text-xs mb-4 leading-relaxed font-mono">
              Natural language retrieval graph querying 1,420+ historical multi-agent flight experiences.
            </p>
            <Button
              variant="cyber"
              size="md"
              className="w-full"
              onClick={() => setIntelModalOpen(true)}
            >
              Open AI Copilot Query &rarr;
            </Button>
          </Panel>
        </div>
      </div>
    </div>
  );
};
