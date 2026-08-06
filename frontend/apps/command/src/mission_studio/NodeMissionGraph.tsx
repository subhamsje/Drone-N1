import React, { useState } from 'react';
import { useCognitionStore } from '../stores/cognitionStore';

interface MissionNode {
  id: string;
  type: 'TAKEOFF' | 'SURVEY' | 'INSPECT' | 'DETECT' | 'DELIVER' | 'RTL';
  label: string;
  params: string;
  x: number;
  y: number;
}

export function NodeMissionGraph() {
  const setWorkspaceMode = useCognitionStore((s) => s.setWorkspaceMode);

  const [nodes, setNodes] = useState<MissionNode[]>([
    { id: 'n1', type: 'TAKEOFF', label: '01. Autonomous Takeoff', params: 'ALT: 50m • RATE: 2.5m/s', x: 50, y: 150 },
    { id: 'n2', type: 'SURVEY', label: '02. Grid Survey Pattern', params: 'CORRIDOR: Alpha • SPEED: 12m/s', x: 280, y: 150 },
    { id: 'n3', type: 'INSPECT', label: '03. Structural Thermal Scan', params: 'GIMBAL: -45° • DIST: 15m', x: 520, y: 100 },
    { id: 'n4', type: 'DETECT', label: '04. AI Target Classification', params: 'CONFIDENCE > 90% • LOCK_ON', x: 520, y: 220 },
    { id: 'n5', type: 'DELIVER', label: '05. Precision Payload Drop', params: 'WINCH: ENABLED • WINDBREAK', x: 760, y: 160 },
    { id: 'n6', type: 'RTL', label: '06. Return to Home Base', params: 'ALT: 60m • BATTERY > 25%', x: 990, y: 160 },
  ]);

  const [selectedNode, setSelectedNode] = useState<MissionNode | null>(nodes[1]);

  return (
    <div className="h-full w-full bg-[#010409] text-slate-200 p-6 flex flex-col font-sans overflow-hidden">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
        <div className="flex items-center space-x-3">
          <span className="px-2.5 py-1 rounded bg-purple-500/10 text-purple-400 border border-purple-500/30 text-xs font-mono font-bold">
            MISSION STUDIO IDE v2.1
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Node-Based Mission Graph Blueprint
          </h2>
          <span className="text-xs font-mono text-slate-500">v1.4.2 (GIT: main)</span>
        </div>

        <div className="flex items-center space-x-3">
          <button className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-300 border border-slate-700">
            Compare Missions
          </button>
          <button className="px-3 py-1.5 rounded bg-purple-600 hover:bg-purple-500 text-xs font-mono font-semibold text-white shadow-lg shadow-purple-600/20">
            Run Physics Simulation
          </button>
          <button 
            onClick={() => setWorkspaceMode('command_globe')}
            className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-xs font-mono font-semibold text-white"
          >
            Deploy to 3D Globe &rarr;
          </button>
        </div>
      </div>

      {/* Main Workspace split into Graph Canvas and Node Details Sidebar */}
      <div className="flex-1 flex gap-4 overflow-hidden">
        {/* Canvas Area */}
        <div className="flex-1 rounded-xl border border-slate-800 bg-[#050914] relative p-6 overflow-auto bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px]">
          
          <div className="absolute top-4 left-4 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-800 text-xs font-mono text-slate-400 flex items-center space-x-4">
            <span>ZOOM: 100%</span>
            <span>NODES: {nodes.length}</span>
            <span>RULE CHECK: PASSED</span>
          </div>

          {/* SVG Connection Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none stroke-cyan-500/50 fill-none stroke-[2]">
            <path d="M 220 185 C 250 185, 250 185, 280 185" />
            <path d="M 450 185 C 485 185, 485 135, 520 135" />
            <path d="M 450 185 C 485 185, 485 255, 520 255" />
            <path d="M 690 135 C 725 135, 725 195, 760 195" />
            <path d="M 690 255 C 725 255, 725 195, 760 195" />
            <path d="M 930 195 C 960 195, 960 195, 990 195" />
          </svg>

          {/* Render Nodes */}
          {nodes.map((n) => {
            const isSelected = selectedNode?.id === n.id;
            return (
              <div
                key={n.id}
                onClick={() => setSelectedNode(n)}
                style={{ left: n.x, top: n.y }}
                className={`absolute w-52 p-3 rounded-lg border backdrop-blur-md cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-cyan-950/90 border-cyan-400 shadow-lg shadow-cyan-500/20 ring-1 ring-cyan-400'
                    : 'bg-slate-900/90 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5 mb-2">
                  <span className="text-[10px] font-mono font-bold uppercase text-cyan-400">{n.type}</span>
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                </div>
                <div className="text-xs font-semibold text-white">{n.label}</div>
                <div className="text-[10px] font-mono text-slate-400 mt-1">{n.params}</div>
              </div>
            );
          })}
        </div>

        {/* Node Inspector Sidebar */}
        <div className="w-80 rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-md flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 border-b border-slate-800 pb-2 mb-4">
              Node Parameter Inspector
            </h3>

            {selectedNode ? (
              <div className="space-y-4">
                <div>
                  <label className="text-[10px] font-mono text-slate-400 uppercase">Node ID & Type</label>
                  <div className="text-xs font-mono font-bold text-cyan-400">{selectedNode.id} • {selectedNode.type}</div>
                </div>

                <div>
                  <label className="text-[10px] font-mono text-slate-400 uppercase">Label</label>
                  <input 
                    type="text"
                    value={selectedNode.label}
                    onChange={(e) => setSelectedNode({ ...selectedNode, label: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white mt-1"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-mono text-slate-400 uppercase">Parameters</label>
                  <textarea 
                    value={selectedNode.params}
                    onChange={(e) => setSelectedNode({ ...selectedNode, params: e.target.value })}
                    className="w-full h-20 bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono text-slate-200 mt-1"
                  />
                </div>

                <div className="p-3 rounded bg-slate-950 border border-slate-800 text-xs space-y-1">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">Estimated Node Economics</div>
                  <div className="flex justify-between font-mono text-slate-300">
                    <span>Node Energy:</span>
                    <span className="text-emerald-400">4.2 Wh</span>
                  </div>
                  <div className="flex justify-between font-mono text-slate-300">
                    <span>Node Risk:</span>
                    <span className="text-cyan-400">Low (2.1%)</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-xs text-slate-500 font-mono">Select a node on the canvas to edit parameters.</div>
            )}
          </div>

          <div className="border-t border-slate-800 pt-3">
            <button className="w-full py-2 rounded bg-purple-600/20 border border-purple-500/40 text-purple-300 font-mono text-xs font-bold hover:bg-purple-600/30">
              Save Mission Blueprint v1.4.3
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
