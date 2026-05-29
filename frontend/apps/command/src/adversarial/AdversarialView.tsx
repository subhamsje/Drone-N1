import { Panel, CognitionChip } from '@altaria/ui';
import { useCognitionStore } from '../stores/cognitionStore';
import { cognitionEngine } from '../config/runtime';

function ThreatBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="mb-0.5 flex justify-between font-mono text-[8px] text-slate-500">
        <span>{label}</span>
        <span>{(value * 100).toFixed(0)}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-slate-900">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.min(100, value * 100)}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

export function AdversarialView() {
  const adv = useCognitionStore((s) => s.envelope?.adversarial) as Record<string, unknown> | undefined;
  const adaptive = adv?.adaptive as Record<string, unknown> | undefined;
  const perc = adv?.perception as { robustness_verdict?: string; survival_mode?: string } | undefined;
  const t = cognitionEngine().renderState.twin;

  const gps = Number(adv?.gps_spoofing_index ?? t.threatLevel * 0.8);
  const rf = Number(adv?.rf_jamming_index ?? t.rfDenied);
  const poison = Number(adv?.telemetry_poisoning_index ?? t.threatLevel * 0.5);

  return (
    <Panel title="Contested Operations" accent="adversarial" className="ops-panel-accent">
      <CognitionChip variant="alert">{(adaptive?.adversarial_intent as string) ?? 'SCANNING'}</CognitionChip>
      <p className="mt-2 text-[10px] text-slate-500">{(adaptive?.contested_cognition_mode as string) ?? 'nominal'}</p>
      <div className="mt-3 space-y-2">
        <ThreatBar label="GPS spoofing" value={gps} color="#f97316" />
        <ThreatBar label="RF warfare" value={rf} color="#eab308" />
        <ThreatBar label="Telemetry poison" value={poison} color="#ef4444" />
      </div>
      <p className="mt-2 font-mono text-[9px] text-red-300/80">
        {(adaptive?.sabotage_indicators as string[] | undefined)?.slice(0, 2).join(' · ') || 'no active sabotage'}
      </p>
      <p className="text-[9px] text-slate-600">
        Perception {perc?.robustness_verdict} · {perc?.survival_mode}
      </p>
    </Panel>
  );
}
