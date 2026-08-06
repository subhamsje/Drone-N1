import React, { useState } from 'react';

export function FaultInjectionDrawer() {
  const [open, setOpen] = useState(false);
  const [activeFaults, setActiveFaults] = useState<string[]>([]);

  const toggleFault = (fault: string) => {
    if (activeFaults.includes(fault)) {
      setActiveFaults(activeFaults.filter((f) => f !== fault));
    } else {
      setActiveFaults([...activeFaults, fault]);
    }
  };

  return (
    <>
      {/* Floating Launch Trigger Button */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 left-6 z-40 px-3.5 py-2 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/40 text-rose-300 text-xs font-mono font-bold backdrop-blur-md shadow-2xl flex items-center space-x-2"
      >
        <span className="h-2 w-2 rounded-full bg-rose-500 animate-pulse" />
        <span>ADVERSARIAL FAULT INJECTOR</span>
        {activeFaults.length > 0 && (
          <span className="px-1.5 py-0.5 rounded bg-rose-500 text-white text-[10px]">
            {activeFaults.length} ACTIVE
          </span>
        )}
      </button>

      {/* Drawer Body */}
      {open && (
        <div className="fixed bottom-20 left-6 z-40 w-96 rounded-xl border border-rose-500/40 bg-[#050914]/95 backdrop-blur-xl p-4 text-slate-200 shadow-2xl font-sans">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
            <span className="text-xs font-mono font-bold text-rose-400 uppercase">
              Adversarial Fault Injector
            </span>
            <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-white text-xs">
              ✕
            </button>
          </div>

          <p className="text-[11px] text-slate-400 mb-3">
            Simulate real-time hardware, environmental, and RF failures to test the 20D EKF Rollback Buffer and MPC Recovery controller.
          </p>

          <div className="space-y-2">
            {[
              { id: 'motor0_ramp', name: 'Motor 0 Thermal Ramp', desc: 'Ramps motor wear by +0.04/s' },
              { id: 'gps_denial', name: 'GPS Jamming / Spoofing', desc: 'Drops satellite trust to 0%' },
              { id: 'wind_spike', name: '15 m/s Wind Turbulence', desc: 'Injects severe aerodynamic shear' },
              { id: 'battery_sag', name: 'Battery Cell Sag', desc: 'Simulates instantaneous 15% voltage drop' },
            ].map((f) => {
              const active = activeFaults.includes(f.id);
              return (
                <div
                  key={f.id}
                  onClick={() => toggleFault(f.id)}
                  className={`p-2.5 rounded-lg border cursor-pointer transition-all flex items-center justify-between ${
                    active
                      ? 'bg-rose-950/80 border-rose-500 text-white'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div>
                    <div className="text-xs font-semibold">{f.name}</div>
                    <div className="text-[10px] font-mono text-slate-400">{f.desc}</div>
                  </div>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                      active ? 'bg-rose-500 text-white font-bold' : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {active ? 'ENGAGED' : 'INJECT'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
}
