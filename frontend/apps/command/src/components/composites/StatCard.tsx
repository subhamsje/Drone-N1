import React from 'react';
import { Badge } from '../primitives/Badge';

export interface StatCardProps {
  title: string;
  value: string | number;
  unit?: string;
  badgeText?: string;
  badgeVariant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  subtitle?: string;
  icon?: React.ReactNode;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  unit,
  badgeText,
  badgeVariant = 'neutral',
  subtitle,
  icon,
  className = '',
}) => {
  return (
    <div className={`p-4 rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-md font-mono select-none flex flex-col justify-between ${className}`}>
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span className="text-[10px] uppercase tracking-wider font-semibold">{title}</span>
        {badgeText && <Badge variant={badgeVariant}>{badgeText}</Badge>}
      </div>

      <div className="my-2 flex items-baseline justify-between">
        <div className="text-2xl font-extrabold text-white tracking-tight flex items-baseline gap-1">
          <span>{value}</span>
          {unit && <span className="text-xs font-normal text-slate-400">{unit}</span>}
        </div>
        {icon && <div className="text-slate-500">{icon}</div>}
      </div>

      {subtitle && <div className="text-[10px] text-slate-400 truncate">{subtitle}</div>}
    </div>
  );
};
