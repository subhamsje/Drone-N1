import React, { useEffect, useState } from 'react';
import { useCognitionStore } from '../stores/cognitionStore';

export function CommandPaletteModal() {
  const ctrlKOpen = useCognitionStore((s) => s.ctrlKOpen);
  const setCtrlKOpen = useCognitionStore((s) => s.setCtrlKOpen);
  const setWorkspaceMode = useCognitionStore((s) => s.setWorkspaceMode);
  const setOpticMode = useCognitionStore((s) => s.setOpticMode);
  const setActiveIncidentModal = useCognitionStore((s) => s.setActiveIncidentModal);
  const setDebriefModal = useCognitionStore((s) => s.setDebriefModal);

  const [query, setQuery] = useState('');

  // Keyboard Event Listener for Ctrl+K / Cmd+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCtrlKOpen(!ctrlKOpen);
      }
      if (e.key === 'Escape' && ctrlKOpen) {
        setCtrlKOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [ctrlKOpen, setCtrlKOpen]);

  if (!ctrlKOpen) return null;

  const actions = [
    { title: 'Launch Operations Center Homepage', cat: 'WORKSPACE', action: () => { setWorkspaceMode('ops_center'); setCtrlKOpen(false); } },
    { title: 'Switch to 3D Planetary Command Globe', cat: 'WORKSPACE', action: () => { setWorkspaceMode('command_globe'); setCtrlKOpen(false); } },
    { title: 'Open Node-Based Mission Studio Graph', cat: 'WORKSPACE', action: () => { setWorkspaceMode('mission_studio'); setCtrlKOpen(false); } },
    { title: 'Inspect 20D Digital Twin Workbench', cat: 'WORKSPACE', action: () => { setWorkspaceMode('twin_workbench'); setCtrlKOpen(false); } },
    { title: 'Set Optic Shader: Thermal / FLIR', cat: 'SHADERS', action: () => { setOpticMode('thermal'); setCtrlKOpen(false); } },
    { title: 'Set Optic Shader: Night Vision', cat: 'SHADERS', action: () => { setOpticMode('nightvision'); setCtrlKOpen(false); } },
    { title: 'Set Optic Shader: Wireframe / SAR', cat: 'SHADERS', action: () => { setOpticMode('wireframe'); setCtrlKOpen(false); } },
    { title: 'Inspect Active Incidents (#INC-882)', cat: 'INCIDENTS', action: () => { setActiveIncidentModal(true); setCtrlKOpen(false); } },
    { title: 'Open Post-Flight AI Mission Debrief', cat: 'ANALYTICS', action: () => { setDebriefModal(true); setCtrlKOpen(false); } },
  ];

  const filtered = actions.filter((a) =>
    a.title.toLowerCase().includes(query.toLowerCase()) || a.cat.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/70 backdrop-blur-md p-4">
      <div className="w-full max-w-xl rounded-xl border border-cyan-500/40 bg-[#050914] text-slate-200 shadow-2xl overflow-hidden font-sans">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3 border-b border-slate-800">
          <svg className="w-5 h-5 text-cyan-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            autoFocus
            placeholder="Type a command or search workspace (e.g., 'ops', 'thermal', 'incident')..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none font-mono"
          />
          <span className="text-[10px] font-mono text-slate-500 border border-slate-800 px-2 py-0.5 rounded">ESC</span>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length > 0 ? (
            filtered.map((item, idx) => (
              <div
                key={idx}
                onClick={item.action}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-cyan-500/10 hover:border-cyan-500/30 border border-transparent cursor-pointer transition-all"
              >
                <span className="text-xs font-semibold text-slate-200">{item.title}</span>
                <span className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                  {item.cat}
                </span>
              </div>
            ))
          ) : (
            <div className="p-4 text-xs font-mono text-slate-500 text-center">No matching command found.</div>
          )}
        </div>
      </div>
    </div>
  );
}
