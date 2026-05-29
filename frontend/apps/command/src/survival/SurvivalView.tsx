import { Panel, CognitionChip } from '@altaria/ui';
import { useCognitionStore } from '../stores/cognitionStore';

export function SurvivalView() {
  const e = useCognitionStore((s) => s.envelope);
  const s = e?.survival as Record<string, unknown> | undefined;
  const trust = e?.trust as Record<string, unknown> | undefined;

  return (
    <Panel title="Survival Intelligence" accent="survival">
      <div className="space-y-2 text-xs">
        <div className="flex gap-2">
          <CognitionChip variant={s?.urgency === 'IMMEDIATE' ? 'alert' : 'survival'}>
            {(s?.urgency as string) ?? 'NORMAL'}
          </CognitionChip>
          <CognitionChip variant="survival">{(s?.strategy as string) ?? '—'}</CognitionChip>
        </div>
        <p className="text-slate-400">{String(trust?.survival_escalation_reason ?? 'No escalation')}</p>
        <p className="font-mono text-[10px] text-slate-500">
          Landing: {JSON.stringify((s?.landing_zone as { total_score?: number })?.total_score ?? '—')}
        </p>
        <p className="text-[10px] text-amber-200/80">{String(trust?.survivability_explanation ?? '')}</p>
      </div>
    </Panel>
  );
}
