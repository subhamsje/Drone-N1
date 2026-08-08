import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Trash2, Filter } from 'lucide-react';
import { Button } from '../primitives/Button';

export interface LogEntry {
  timestamp: string;
  source: 'MAVLINK' | 'EKF2' | 'COGNITION' | 'SECURITY' | 'ROS2';
  message: string;
  level: 'INFO' | 'WARN' | 'CRIT';
}

export const LogConsole: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([
    { timestamp: '00:00:01.042', source: 'MAVLINK', message: 'HEARTBEAT received from PX4 FMU (Autopilot: PX4)', level: 'INFO' },
    { timestamp: '00:00:01.084', source: 'EKF2', message: 'Fused RTK-GPS (19 Sats) + ORB-SLAM3 VIO. Variance: 0.004m²', level: 'INFO' },
    { timestamp: '00:00:01.120', source: 'COGNITION', message: 'Offboard setpoints active at 50Hz. Spline #04 validated clean.', level: 'INFO' },
    { timestamp: '00:00:01.168', source: 'SECURITY', message: 'ECDSA signature validated (SHA256: 4fb2...85fc). Replay counter: 1420', level: 'INFO' },
  ]);

  const [filter, setFilter] = useState<string>('ALL');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      const sources: LogEntry['source'][] = ['MAVLINK', 'EKF2', 'COGNITION', 'ROS2'];
      const src = sources[Math.floor(Math.random() * sources.length)];
      const newLog: LogEntry = {
        timestamp: new Date().toISOString().slice(11, 23),
        source: src,
        message: src === 'MAVLINK'
          ? `Motor RPM: M1: 5820 | M2: 5815 | M3: 5840 | M4: 5810 (Harmonics: 0.012 m/s²)`
          : src === 'EKF2'
          ? `State estimator innovation nominal. Roll: 4.5° | Pitch: -3.2°`
          : `MPC trajectory horizon N=5 computed in 2.1ms (Cost: 0.042)`,
        level: 'INFO',
      };
      setLogs((prev) => [newLog, ...prev.slice(0, 40)]);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const clearLogs = () => setLogs([]);

  const filteredLogs = filter === 'ALL' ? logs : logs.filter((l) => l.source === filter);

  return (
    <div className="h-full w-full bg-[#050811] rounded-xl border border-slate-800/80 flex flex-col font-mono text-xs overflow-hidden select-none">
      {/* Console Header */}
      <div className="h-9 bg-[#0d131f] border-b border-slate-800/80 px-3 flex items-center justify-between text-slate-400">
        <div className="flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-sky-400" />
          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-300">Live 50Hz MAVLink Telemetry Console</span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded px-1.5 py-0.5 text-[10px]">
            {['ALL', 'MAVLINK', 'EKF2', 'COGNITION'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-1.5 py-0.5 rounded transition-all ${
                  filter === f ? 'bg-sky-600/30 text-sky-300 font-bold' : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          <Button variant="ghost" size="sm" onClick={clearLogs} icon={<Trash2 className="w-3 h-3" />}>
            Clear
          </Button>
        </div>
      </div>

      {/* Log Feed Viewport */}
      <div className="flex-1 p-3 overflow-y-auto space-y-1 text-[11px]">
        {filteredLogs.map((log, index) => (
          <div key={index} className="flex items-baseline space-x-2 text-slate-300 hover:text-white leading-relaxed truncate">
            <span className="text-slate-500 text-[10px]">[{log.timestamp}]</span>
            <span
              className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
                log.source === 'MAVLINK'
                  ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                  : log.source === 'EKF2'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
              }`}
            >
              {log.source}
            </span>
            <span className="text-slate-300 truncate">{log.message}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
