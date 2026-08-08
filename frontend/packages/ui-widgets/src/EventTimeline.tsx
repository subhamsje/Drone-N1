import React from 'react';

export interface TimelineEvent {
  id: string;
  time: string;
  title: string;
  description?: string;
  severity: 'INFO' | 'WARN' | 'CRIT';
}

export interface EventTimelineProps {
  events: TimelineEvent[];
  className?: string;
}

export const EventTimeline: React.FC<EventTimelineProps> = ({ events, className = '' }) => {
  return (
    <div className={`space-y-3 font-mono text-xs ${className}`}>
      {events.map((evt) => (
        <div
          key={evt.id}
          className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 flex items-start justify-between gap-3 hover:border-slate-700 transition-colors"
        >
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-500 font-bold">[{evt.time}]</span>
              <span className="font-semibold text-slate-200">{evt.title}</span>
            </div>
            {evt.description && <div className="text-[11px] text-slate-400">{evt.description}</div>}
          </div>

          <span
            className={`px-2 py-0.5 rounded text-[9px] font-bold shrink-0 border ${
              evt.severity === 'CRIT'
                ? 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                : evt.severity === 'WARN'
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                : 'bg-sky-500/20 text-sky-300 border-sky-500/30'
            }`}
          >
            {evt.severity}
          </span>
        </div>
      ))}
    </div>
  );
};
