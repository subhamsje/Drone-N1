import React, { useState } from 'react';
import { Network, ShieldCheck, X, Activity, Radio, Cpu } from 'lucide-react';
import { tacticalAudio } from '../audio/tacticalAudio';

interface SwarmTopologyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SwarmTopologyModal: React.FC<SwarmTopologyModalProps> = ({ isOpen, onClose }) => {
  const [selectedNode, setSelectedNode] = useState<string>('UAV-01 (Leader)');

  if (!isOpen) return null;

  const swarmNodes = [
    { id: 'UAV-01 (Leader)', role: 'LEADER', rssi: -42, battery: 94, threat_share: 'SYNCED', x: 200, y: 150 },
    { id: 'UAV-02', role: 'SCOUT', rssi: -48, battery: 88, threat_share: 'SYNCED', x: 100, y: 80 },
    { id: 'UAV-03', role: 'RELAY', rssi: -55, battery: 91, threat_share: 'SYNCED', x: 300, y: 80 },
    { id: 'UAV-04', role: 'INSPECTOR', rssi: -50, battery: 85, threat_share: 'SYNCED', x: 100, y: 220 },
    { id: 'UAV-05', role: 'CARRIER', rssi: -52, battery: 82, threat_share: 'SYNCED', x: 300, y: 220 },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4 select-none">
      <div className="relative w-full max-w-3xl bg-slate-900/95 border border-sky-500/30 rounded-2xl p-6 shadow-2xl text-slate-100 backdrop-blur-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-sky-500/10 border border-sky-500/30 text-sky-400">
              <Network className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                25-Node P2P Swarm Mesh Topology
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-sky-500/20 text-sky-300 font-mono border border-sky-500/30">
                  CONSENSUS: 3.8ms
                </span>
              </h2>
              <p className="text-xs text-slate-400">Distributed Byzantine-Fault-Tolerant Threat Vector Sharing</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mesh Topology Visual Area */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* SVG Force Mesh Diagram */}
          <div className="md:col-span-2 relative h-72 rounded-xl bg-slate-950/80 border border-slate-800 overflow-hidden flex items-center justify-center">
            {/* SVG Connecting Links */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none stroke-sky-500/40 stroke-[2] stroke-dasharray-[4]">
              <line x1="200" y1="150" x2="100" y2="80" />
              <line x1="200" y1="150" x2="300" y2="80" />
              <line x1="200" y1="150" x2="100" y2="220" />
              <line x1="200" y1="150" x2="300" y2="220" />
              <line x1="100" y1="80" x2="300" y2="80" />
              <line x1="100" y1="220" x2="300" y2="220" />
            </svg>

            {/* Interactive Nodes */}
            {swarmNodes.map((n) => {
              const active = selectedNode === n.id;
              return (
                <div
                  key={n.id}
                  onClick={() => {
                    setSelectedNode(n.id);
                    tacticalAudio.playChirp(980, 40);
                  }}
                  style={{ left: n.x, top: n.y }}
                  className={`absolute -translate-x-1/2 -translate-y-1/2 p-2.5 rounded-xl border font-mono text-[10px] cursor-pointer transition-all ${
                    active
                      ? 'bg-sky-950/90 border-sky-400 shadow-lg shadow-sky-500/30 ring-1 ring-sky-400'
                      : 'bg-slate-900/90 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="font-bold text-white flex items-center gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    {n.id}
                  </div>
                  <div className="text-slate-400 text-[9px] mt-0.5">{n.role} • {n.rssi}dBm</div>
                </div>
              );
            })}
          </div>

          {/* Node Inspector Panel */}
          <div className="rounded-xl bg-slate-950/60 border border-slate-800 p-4 font-mono text-xs space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 border-b border-slate-800 pb-2">
              Node Details
            </h3>
            <div>
              <span className="text-[10px] text-slate-500 uppercase block">Selected Unit</span>
              <span className="text-sky-400 font-bold text-sm">{selectedNode}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">P2P Latency:</span>
              <span className="text-emerald-400 font-semibold">2.4 ms</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">Threat Costmap:</span>
              <span className="text-sky-400">100% Synced</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
              <span className="text-slate-400">Collision Margin:</span>
              <span className="text-slate-200">18.4 meters</span>
            </div>
            <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-[10px] text-emerald-300 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Mesh Consensus Verified</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
