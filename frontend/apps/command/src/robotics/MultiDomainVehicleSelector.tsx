import React, { useState } from 'react';
import { Plane, Truck, Compass, Anchor, Bot } from 'lucide-react';

export const MultiDomainVehicleSelector: React.FC = () => {
  const [selectedDomain, setSelectedDomain] = useState('UAV');

  const domains = [
    { id: 'UAV', label: 'UAV Multirotor', icon: Plane, status: 'FLIGHT_READY' },
    { id: 'VTOL', label: 'VTOL Fixed-Wing', icon: Compass, status: 'TRANSITION_READY' },
    { id: 'UGV', label: 'UGV Rover', icon: Truck, status: 'ROVER_CONNECTED' },
    { id: 'USV', label: 'USV Surface Boat', icon: Anchor, status: 'SONAR_ACTIVE' }
  ];

  return (
    <div className="flex items-center gap-1 bg-slate-900/90 border border-slate-800 rounded-xl p-1 backdrop-blur-md">
      {domains.map((d) => {
        const Icon = d.icon;
        const active = selectedDomain === d.id;
        return (
          <button
            key={d.id}
            onClick={() => setSelectedDomain(d.id)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
              active
                ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Icon className={`w-3.5 h-3.5 ${active ? 'text-sky-400' : 'text-slate-400'}`} />
            <span>{d.id}</span>
          </button>
        );
      })}
    </div>
  );
};
