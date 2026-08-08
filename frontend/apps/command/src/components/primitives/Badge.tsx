import React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  pulse?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  pulse = false,
  className = '',
}) => {
  const variantStyles = {
    success: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    warning: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
    danger: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
    info: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
    neutral: 'bg-slate-800/80 text-slate-300 border-slate-700/60',
  }[variant];

  const dotColors = {
    success: 'bg-emerald-400',
    warning: 'bg-amber-400',
    danger: 'bg-rose-400',
    info: 'bg-sky-400',
    neutral: 'bg-slate-400',
  }[variant];

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-[10px] font-mono font-semibold tracking-wider ${variantStyles} ${className}`}>
      {pulse && <span className={`h-1.5 w-1.5 rounded-full ${dotColors} animate-pulse`} />}
      <span>{children}</span>
    </span>
  );
};
