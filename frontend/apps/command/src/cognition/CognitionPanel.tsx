import { Panel, MetricRing, UncertaintyBar, CognitionChip } from '@altaria/ui';
import { survivabilityColor, uncertaintyColor } from '@altaria/cognition-sdk';
import { useCognitionStore } from '../stores/cognitionStore';

export function CognitionPanel() {
  const e = useCognitionStore((s) => s.envelope);
  const c = e?.cognition;
  if (!c) {
    return (
      <Panel title="Autonomous Cognition" accent="cognition">
        <p className="text-xs text-slate-500">Awaiting cognition stream…</p>
      </Panel>
    );
  }

  return (
    <Panel title="Autonomous Cognition" accent="cognition" className="space-y-3">
      <div className="flex justify-around">
        <MetricRing label="Survivability" value={c.composite_survivability} color={survivabilityColor(c.composite_survivability)} />
        <MetricRing label="Crash P" value={c.crash_probability} color={uncertaintyColor(c.crash_probability)} />
      </div>
      <UncertaintyBar label="Global uncertainty" value={c.global_uncertainty} />
      <UncertaintyBar label="GPS trust" value={1 - c.gps_trust} />
      <UncertaintyBar label="Vision trust" value={1 - c.vision_trust} />
      <div className="flex flex-wrap gap-1">
        <CognitionChip>{c.action ?? 'NONE'}</CognitionChip>
        {c.preempt && <CognitionChip variant="survival">{c.preempt}</CognitionChip>}
        <CognitionChip>trust {(c.ai_trust_score * 100).toFixed(0)}%</CognitionChip>
      </div>
      <ul className="max-h-24 space-y-1 overflow-y-auto text-[10px] text-slate-400">
        {c.reasoning_chain?.map((line, i) => (
          <li key={i}>→ {line}</li>
        ))}
      </ul>
    </Panel>
  );
}
