import React from 'react';
import { useCognitionStore } from '../stores/cognitionStore';
import { tacticalAudio } from '../audio/tacticalAudio';
import { Eye, Flame, Moon, Box, CloudRain, Globe } from 'lucide-react';

export const OpticShaderToolbar: React.FC = () => {
  const opticMode = useCognitionStore((s) => s.opticMode);
  const setOpticMode = useCognitionStore((s) => s.setOpticMode);

  const optics = [
    { id: 'satellite', label: 'Satellite HD', icon: Globe },
    { id: 'tactical', label: 'Tactical AR', icon: Eye },
    { id: 'thermal', label: 'FLIR Thermal', icon: Flame },
    { id: 'nightvision', label: 'Night Vision', icon: Moon },
    { id: 'wireframe', label: 'SAR Wireframe', icon: Box },
  ] as const;

  const handleSelect = (id: 'satellite' | 'tactical' | 'thermal' | 'nightvision' | 'wireframe') => {
    setOpticMode(id);
    tacticalAudio.playChirp(920, 40);
    tacticalAudio.speak(`Optic shader switched to ${id} mode.`);
  };

  return (
    <div className="absolute top-4 right-4 z-20 flex items-center gap-1.5 bg-slate-950/85 border border-slate-800/90 rounded-2xl p-1.5 backdrop-blur-xl shadow-2xl font-mono text-xs select-none">
      {optics.map((opt) => {
        const Icon = opt.icon;
        const active = opticMode === opt.id;
        return (
          <button
            key={opt.id}
            onClick={() => handleSelect(opt.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl font-medium transition-all ${
              active
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
            }`}
          >
            <Icon className={`w-3.5 h-3.5 ${active ? 'text-cyan-400' : 'text-slate-400'}`} />
            <span>{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
};
