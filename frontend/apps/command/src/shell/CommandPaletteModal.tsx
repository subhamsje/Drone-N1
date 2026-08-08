import React, { useEffect, useState } from 'react';
import { useUiStore } from '../global/uiState';
import { commandRegistry, CommandItem } from '../services/commandRegistry';
import { Search, Terminal, ArrowRight } from 'lucide-react';

export function CommandPaletteModal() {
  const { commandPaletteOpen, setCommandPaletteOpen } = useUiStore();
  const [query, setQuery] = useState('');
  const [commands, setCommands] = useState<CommandItem[]>([]);

  useEffect(() => {
    setCommands(commandRegistry.getAll());
  }, [commandPaletteOpen]);

  // Keyboard shortcut listener for Cmd+K / Ctrl+K and Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
      if (e.key === 'Escape' && commandPaletteOpen) {
        setCommandPaletteOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [commandPaletteOpen, setCommandPaletteOpen]);

  if (!commandPaletteOpen) return null;

  const filtered = commands.filter(
    (cmd) =>
      cmd.title.toLowerCase().includes(query.toLowerCase()) ||
      cmd.category.toLowerCase().includes(query.toLowerCase()) ||
      (cmd.description && cmd.description.toLowerCase().includes(query.toLowerCase()))
  );

  const handleSelect = async (cmd: CommandItem) => {
    setCommandPaletteOpen(false);
    await cmd.execute();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/80 backdrop-blur-md p-4 animate-fadeIn select-none font-mono text-xs">
      <div className="w-full max-w-xl rounded-2xl border border-slate-800 bg-[#0d131f] text-slate-200 shadow-2xl shadow-black/90 overflow-hidden flex flex-col">
        {/* Search Header */}
        <div className="flex items-center px-4 py-3.5 border-b border-slate-800/80 bg-[#111827]">
          <Search className="w-4 h-4 text-sky-400 mr-3 shrink-0" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a command or search action (e.g. 'RTL', 'FPV', 'Preset')..."
            className="w-full bg-transparent text-sm text-white placeholder-slate-500 focus:outline-none"
          />
          <kbd className="bg-slate-950 px-2 py-0.5 rounded border border-slate-800 text-[10px] text-slate-400">
            ESC
          </kbd>
        </div>

        {/* Command List Viewport */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filtered.length === 0 ? (
            <div className="p-6 text-center text-slate-500 text-xs">No matching system commands found.</div>
          ) : (
            filtered.map((cmd) => (
              <button
                key={cmd.id}
                onClick={() => handleSelect(cmd)}
                className="w-full p-3 rounded-xl hover:bg-slate-800/80 flex items-center justify-between text-left transition-colors group cursor-pointer"
              >
                <div className="space-y-0.5 truncate">
                  <div className="font-semibold text-slate-100 group-hover:text-sky-300 flex items-center gap-2 truncate">
                    <span>{cmd.title}</span>
                  </div>
                  {cmd.description && (
                    <div className="text-[10px] text-slate-400 truncate">{cmd.description}</div>
                  )}
                </div>

                <div className="flex items-center space-x-2 shrink-0 ml-3">
                  {cmd.shortcut && (
                    <kbd className="bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800 text-[10px] text-slate-400">
                      {cmd.shortcut}
                    </kbd>
                  )}
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800">
                    {cmd.category}
                  </span>
                </div>
              </button>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="h-8 bg-[#0a0e17] border-t border-slate-800/80 px-4 flex items-center justify-between text-[10px] text-slate-500">
          <span>Unified Command Engine</span>
          <span>Press Enter ↵ to Execute</span>
        </div>
      </div>
    </div>
  );
}
