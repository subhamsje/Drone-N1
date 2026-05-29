export function UncertaintyBar({ label, value }: { label: string; value: number }) {
  const pct = Math.min(100, value * 100);
  const hue = value < 0.35 ? 190 : value < 0.55 ? 38 : 0;

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[10px] text-slate-500">
        <span>{label}</span>
        <span className="font-mono text-slate-300">{pct.toFixed(0)}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full transition-all duration-300"
          style={{ width: `${pct}%`, backgroundColor: `hsl(${hue}, 70%, 50%)` }}
        />
      </div>
    </div>
  );
}
