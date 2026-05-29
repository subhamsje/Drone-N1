import type { ReactNode } from 'react';

export function CognitionChip({ children, variant = 'default' }: { children: ReactNode; variant?: 'default' | 'alert' | 'survival' }) {
  const styles =
    variant === 'survival'
      ? 'bg-amber-950/60 text-amber-200 border-amber-700/50'
      : variant === 'alert'
        ? 'bg-red-950/50 text-red-200 border-red-800/50'
        : 'bg-slate-900/80 text-slate-300 border-slate-700/50';

  return (
    <span className={`inline-block rounded border px-2 py-0.5 font-mono text-[10px] ${styles}`}>
      {children}
    </span>
  );
}
