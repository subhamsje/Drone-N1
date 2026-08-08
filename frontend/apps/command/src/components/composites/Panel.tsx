import React from 'react';

export interface PanelProps {
  title?: string;
  badge?: string;
  badgeVariant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  actions?: React.ReactNode[];
  children: React.ReactNode;
  className?: string;
  variant?: 'solid' | 'glass';
}

export const Panel: React.FC<PanelProps> = ({
  title,
  badge,
  badgeVariant = 'neutral',
  actions = [],
  children,
  className = '',
  variant = 'solid',
}) => {
  const bg = variant === 'glass'
    ? 'bg-[#0d131f]/85 backdrop-blur-xl border border-slate-800/80 shadow-2xl'
    : 'bg-[#0d131f] border border-slate-800/80 shadow-xl';

  return (
    <div className={`rounded-xl flex flex-col font-mono text-xs overflow-hidden select-none ${bg} ${className}`}>
      {title && (
        <div className="h-10 px-4 bg-[#111827]/80 border-b border-slate-800/80 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-2.5">
            <span className="font-bold text-slate-200 text-xs tracking-tight">{title}</span>
            {badge && (
              <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                badgeVariant === 'success' ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' :
                badgeVariant === 'danger' ? 'bg-rose-500/15 text-rose-300 border-rose-500/30' :
                badgeVariant === 'warning' ? 'bg-amber-500/15 text-amber-300 border-amber-500/30' :
                'bg-sky-500/15 text-sky-300 border-sky-500/30'
              }`}>
                {badge}
              </span>
            )}
          </div>

          {actions.length > 0 && (
            <div className="flex items-center space-x-2">
              {actions.map((act, i) => (
                <React.Fragment key={i}>{act}</React.Fragment>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="flex-1 p-4 overflow-y-auto">{children}</div>
    </div>
  );
};
