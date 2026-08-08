import React from 'react';

export interface StatusIndicatorProps {
  label: string;
  value?: string | number;
  status: 'nominal' | 'caution' | 'warning' | 'critical';
  pulse?: boolean;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  label,
  value,
  status,
  pulse = true,
}) => {
  const dotColor = {
    nominal: 'bg-emerald-400',
    caution: 'bg-amber-400',
    warning: 'bg-amber-500',
    critical: 'bg-rose-400',
  }[status];

  return (
    <div className="flex items-center space-x-2 font-mono text-xs">
      <span className={`h-2 w-2 rounded-full ${dotColor} ${pulse ? 'animate-pulse' : ''}`} />
      <span className="text-slate-400 text-[11px]">{label}</span>
      {value && <span className="font-bold text-slate-200">{value}</span>}
    </div>
  );
};
