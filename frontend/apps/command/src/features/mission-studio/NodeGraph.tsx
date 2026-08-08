import React from 'react';
import { useMissionStore, MissionNode } from '../../global/missionState';
import { Button } from '../../components/primitives/Button';
import { Badge } from '../../components/primitives/Badge';
import { Plus, Play, CheckCircle2, Cpu } from 'lucide-react';

export const NodeGraph: React.FC = () => {
  const { nodes, selectedNodeId, addNode, updateNode, setSelectedNodeId, compileGraph, compiling, compiledResult } = useMissionStore();

  const selectedNode = nodes.find(n => n.id === selectedNodeId) || nodes[0];

  return (
    <div className="h-full w-full bg-[#080c14] text-slate-200 p-6 flex flex-col font-sans overflow-hidden select-none">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-4">
        <div className="flex items-center space-x-3">
          <Badge variant="info">MAVSDK 2.0</Badge>
          <h2 className="text-lg font-bold text-slate-100 tracking-tight">Interactive Mission Graph & DAG Visualizer</h2>
        </div>

        <div className="flex items-center space-x-2">
          <Button size="sm" variant="secondary" icon={<Plus className="w-3.5 h-3.5" />} onClick={() => addNode('INSPECT')}>
            Inspect Node
          </Button>
          <Button size="sm" variant="secondary" icon={<Plus className="w-3.5 h-3.5" />} onClick={() => addNode('DETECT')}>
            Detect Node
          </Button>
          <Button
            size="sm"
            variant="primary"
            loading={compiling}
            icon={<Play className="w-3.5 h-3.5" />}
            onClick={compileGraph}
          >
            {compiling ? 'Compiling...' : 'Compile MAVSDK'}
          </Button>
        </div>
      </div>

      {/* Main Canvas & Parameter Inspector Split */}
      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Canvas Area */}
        <div className="flex-1 rounded-xl border border-slate-800/80 bg-[#0d121f] relative overflow-hidden bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px]">
          {/* SVG Connection Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none stroke-sky-500/30 fill-none stroke-[2]">
            {nodes.slice(0, -1).map((n, i) => {
              const next = nodes[i + 1];
              return (
                <path
                  key={i}
                  d={`M ${n.x + 190} ${n.y + 35} C ${n.x + 230} ${n.y + 35}, ${next.x - 30} ${next.y + 35}, ${next.x} ${next.y + 35}`}
                />
              );
            })}
          </svg>

          {/* Render Nodes */}
          {nodes.map((n) => {
            const isSelected = selectedNode?.id === n.id;
            return (
              <div
                key={n.id}
                onClick={() => setSelectedNodeId(n.id)}
                style={{ left: n.x, top: n.y }}
                className={`absolute w-52 p-3.5 rounded-xl border backdrop-blur-md cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-slate-900 border-sky-500/80 shadow-lg shadow-sky-500/10 ring-1 ring-sky-500/40'
                    : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 mb-2">
                  <span className="text-[10px] font-mono font-semibold uppercase text-sky-400">{n.type}</span>
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                </div>
                <div className="text-xs font-semibold text-slate-100">{n.label}</div>
                <div className="text-[10px] font-mono text-slate-400 mt-1">{n.params}</div>
              </div>
            );
          })}
        </div>

        {/* Parameter Inspector Sidebar */}
        <div className="w-80 rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-md flex flex-col justify-between font-mono text-xs">
          <div className="space-y-4">
            <h3 className="font-semibold uppercase tracking-wider text-slate-300 border-b border-slate-800 pb-2">
              Waypoint Parameters
            </h3>

            {selectedNode && (
              <div className="space-y-3">
                <div>
                  <div className="text-[10px] text-slate-500 uppercase">Node ID</div>
                  <div className="font-bold text-sky-400">{selectedNode.id} ({selectedNode.type})</div>
                </div>

                <div>
                  <div className="text-[10px] text-slate-500 uppercase">Label</div>
                  <input
                    type="text"
                    value={selectedNode.label}
                    onChange={(e) => updateNode(selectedNode.id, { label: e.target.value })}
                    className="w-full bg-[#050811] border border-slate-800 rounded px-2.5 py-1.5 text-xs text-white mt-1 focus:border-sky-500/60 focus:outline-none"
                  />
                </div>

                <div>
                  <div className="text-[10px] text-slate-500 uppercase">Parameters</div>
                  <textarea
                    value={selectedNode.params}
                    onChange={(e) => updateNode(selectedNode.id, { params: e.target.value })}
                    className="w-full h-24 bg-[#050811] border border-slate-800 rounded p-2 text-xs text-slate-200 mt-1 focus:border-sky-500/60 focus:outline-none"
                  />
                </div>
              </div>
            )}
          </div>

          <Button variant="primary" size="md" className="w-full" onClick={compileGraph} icon={<Cpu className="w-3.5 h-3.5" />}>
            Upload to Pixhawk FMU
          </Button>
        </div>
      </div>
    </div>
  );
};
