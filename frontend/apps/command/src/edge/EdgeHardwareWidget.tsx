import React, { useState, useEffect } from 'react';
import { Cpu, Zap, Activity, Thermometer } from 'lucide-react';

export const EdgeHardwareWidget: React.FC = () => {
  const [metrics, setMetrics] = useState({
    device: 'NVIDIA Jetson Orin AGX 64GB',
    cpu: 34.2,
    gpu: 68.5,
    temp: 48.5,
    fps: 60.0,
    latency: 4.2
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        ...prev,
        cpu: +(30 + Math.random() * 8).toFixed(1),
        gpu: +(65 + Math.random() * 10).toFixed(1),
        temp: +(48 + Math.random() * 2).toFixed(1),
        latency: +(4.0 + Math.random() * 0.4).toFixed(1)
      }));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900/85 border border-slate-800/80 rounded-xl p-3.5 backdrop-blur-md shadow-xl text-slate-200 font-mono text-xs w-64 space-y-2.5">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
        <div className="flex items-center gap-2 text-emerald-400 font-bold">
          <Cpu className="w-4 h-4 text-emerald-400" />
          <span className="truncate">Jetson Orin AGX</span>
        </div>
        <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-[10px]">
          {metrics.fps} FPS
        </span>
      </div>

      <div className="space-y-1.5">
        <div className="flex justify-between items-center text-[11px]">
          <span className="text-slate-400">GPU Utilization</span>
          <span className="text-emerald-400 font-bold">{metrics.gpu}%</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div className="bg-emerald-400 h-full rounded-full transition-all" style={{ width: `${metrics.gpu}%` }} />
        </div>

        <div className="flex justify-between items-center text-[11px]">
          <span className="text-slate-400">CPU Load</span>
          <span className="text-sky-400">{metrics.cpu}%</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div className="bg-sky-400 h-full rounded-full transition-all" style={{ width: `${metrics.cpu}%` }} />
        </div>
      </div>

      <div className="flex items-center justify-between pt-1 border-t border-slate-800/60 text-[10px] text-slate-400">
        <span className="flex items-center gap-1">
          <Thermometer className="w-3 h-3 text-amber-400" /> {metrics.temp}°C
        </span>
        <span className="flex items-center gap-1">
          <Zap className="w-3 h-3 text-emerald-400" /> TensorRT: {metrics.latency}ms
        </span>
      </div>
    </div>
  );
};
