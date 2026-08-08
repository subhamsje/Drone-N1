import React from 'react';

export interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  trend?: string;
  trendDirection?: 'up' | 'down' | 'neutral';
  statusColor?: 'emerald' | 'sky' | 'amber' | 'rose';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  trend,
  statusColor = 'sky',
  className = '',
}) => {
  const colorMap = {
    emerald: 'text-emerald-400',
    sky: 'text-sky-400',
    amber: 'text-amber-400',
    rose: 'text-rose-400',
  }[statusColor];

  return (
    <div className={`p-4 rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md font-mono select-none flex flex-col justify-between ${className}`}>
      <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">{label}</div>
      <div className="my-2 flex items-baseline justify-between">
        <div className="text-2xl font-extrabold text-white tracking-tight flex items-baseline gap-1">
          <span>{value}</span>
          {unit && <span className="text-xs font-normal text-slate-400">{unit}</span>}
        </div>
        {trend && <span className={`text-xs font-bold ${colorMap}`}>{trend}</span>}
      </div>
    </div>
  );
};
