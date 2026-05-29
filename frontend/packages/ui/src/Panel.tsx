import type { ReactNode } from 'react';
import { cn } from './cn';

export function Panel({
  title,
  children,
  className,
  accent,
}: {
  title: string;
  children: ReactNode;
  className?: string;
  accent?: 'survival' | 'cognition' | 'adversarial' | 'trust' | 'airspace';
}) {
  const border =
    accent === 'survival'
      ? 'border-amber-500/40'
      : accent === 'adversarial'
        ? 'border-red-500/40'
        : accent === 'trust'
          ? 'border-cyan-500/40'
          : accent === 'airspace'
            ? 'border-violet-500/40'
            : 'border-slate-600/50';

  return (
    <section
      className={cn(
        'rounded border bg-slate-950/80 backdrop-blur-sm',
        border,
        className,
      )}
    >
      <header className="border-b border-slate-800/80 px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
        {title}
      </header>
      <div className="p-3">{children}</div>
    </section>
  );
}
