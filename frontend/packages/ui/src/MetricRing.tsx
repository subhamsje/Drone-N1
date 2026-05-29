export function MetricRing({
  label,
  value,
  color,
  max = 1,
}: {
  label: string;
  value: number;
  color: string;
  max?: number;
}) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const r = 28;
  const c = 2 * Math.PI * r;
  const offset = c - (pct / 100) * c;

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width="72" height="72" className="-rotate-90">
        <circle cx="36" cy="36" r={r} fill="none" stroke="#1e293b" strokeWidth="6" />
        <circle
          cx="36"
          cy="36"
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <span className="text-lg font-mono font-semibold text-slate-100">
        {(value * (max <= 1 ? 100 : 1)).toFixed(max <= 1 ? 0 : 1)}
        {max <= 1 ? '%' : ''}
      </span>
      <span className="text-[9px] uppercase tracking-wider text-slate-500">{label}</span>
    </div>
  );
}
