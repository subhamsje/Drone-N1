import React, { useState } from 'react';
import { Building2, Shield, Satellite, CheckCircle2, Lock } from 'lucide-react';
import { tacticalAudio } from '../audio/tacticalAudio';

export type EnterpriseTier = 'COMMERCIAL_ENTERPRISE' | 'DEFENSE_TACTICAL' | 'BVLOS_REGULATORY';

export const EnterpriseModeSelector: React.FC = () => {
  const [tier, setTier] = useState<EnterpriseTier>('DEFENSE_TACTICAL');

  const tiers = [
    {
      id: 'DEFENSE_TACTICAL',
      label: 'DEFENSE / TACTICAL',
      icon: Shield,
      compliance: 'STANAG 4586 • Zero-Trust ECDSA',
      badgeColor: 'text-sky-400 bg-sky-500/10 border-sky-500/30',
      description: 'Military-grade encryption, electronic warfare jamming fallback, and P2P swarm mesh.',
    },
    {
      id: 'COMMERCIAL_ENTERPRISE',
      label: 'COMMERCIAL ENTERPRISE',
      icon: Building2,
      compliance: 'SOC2 Type II • Multi-Tenant',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
      description: 'Fleet lifecycle tracking, photogrammetric orthomosaics, and itemized mission ROI.',
    },
    {
      id: 'BVLOS_REGULATORY',
      label: 'BVLOS REGULATORY',
      icon: Satellite,
      compliance: 'FAA Part 107 • EASA SORA Class 3',
      badgeColor: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
      description: 'Automated 1-click audit certificates, geofence containment, and airspace waiving.',
    },
  ] as const;

  const handleSelectTier = (t: EnterpriseTier) => {
    setTier(t);
    tacticalAudio.playChirp(980, 50);
  };

  return (
    <div className="flex items-center space-x-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800/80 font-mono text-xs select-none">
      {tiers.map((item) => {
        const Icon = item.icon;
        const active = tier === item.id;
        return (
          <button
            key={item.id}
            onClick={() => handleSelectTier(item.id as EnterpriseTier)}
            className={`flex items-center space-x-1.5 px-3 py-1 rounded-lg transition-all ${
              active
                ? 'bg-slate-800 text-white font-semibold shadow-sm border border-slate-700/60'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent'
            }`}
          >
            <Icon className={`w-3.5 h-3.5 ${active ? 'text-sky-400' : 'text-slate-500'}`} />
            <span className="text-[11px]">{item.label}</span>
          </button>
        );
      })}
    </div>
  );
};
