import { Panel, MetricRing } from '@altaria/ui';
import { useCognitionStore } from '../stores/cognitionStore';

export function TrustLayer() {
  const t = useCognitionStore((s) => s.envelope?.trust) as Record<string, unknown> | undefined;
  const cert = useCognitionStore((s) => s.envelope?.certification?.operational) as { certification_ready?: boolean } | undefined;
  const action = useCognitionStore((s) => s.envelope?.cognition?.action) ?? 'NOMINAL_FLIGHT';

  // AI Decision Lineage / Causality DAG representation
  const lineage = [
    { step: 'PERCEIVE', active: true, state: 'FUSED' },
    { step: 'PREDICT', active: true, state: t?.trust_score && (t.trust_score as number) < 0.8 ? 'DEGRADED' : 'NOMINAL' },
    { step: 'SIMULATE', active: true, state: 'FUTURES' },
    { step: 'EVALUATE', active: true, state: 'SURVIVAL' },
    { step: 'ADAPT', active: action !== 'NOMINAL_FLIGHT' && action !== 'NONE', state: action },
  ];

  return (
    <Panel title="Explainable AI & Trust" accent="trust">
      <div className="flex justify-around mb-4">
        <MetricRing label="Cert Confidence" value={Number(t?.trust_score ?? 0)} color="#38bdf8" />
        <MetricRing label="Mission Risk" value={Number(t?.mission_risk_score ?? 0)} color="#f43f5e" />
      </div>
      
      <div className="border-t border-slate-800/80 pt-3 mb-2">
        <p className="font-mono text-[9px] text-teal-500/80 mb-2 uppercase tracking-widest">Decision Lineage (Causality DAG)</p>
        <div className="flex flex-col gap-1.5 relative before:absolute before:left-1 before:top-2 before:bottom-2 before:w-px before:bg-slate-800">
          {lineage.map((node, i) => (
            <div key={node.step} className={`flex items-center gap-3 relative z-10 ${!node.active ? 'opacity-40' : ''}`}>
              <div className={`w-2 h-2 rounded-full ring-2 ring-offset-1 ring-offset-[#050a12] ${
                node.state === 'DEGRADED' || node.state.includes('LAND') ? 'bg-rose-500 ring-rose-500/50' : 
                node.active ? 'bg-teal-500 ring-teal-500/50' : 'bg-slate-700 ring-transparent'
              }`} />
              <div className="flex flex-col">
                <span className="font-mono text-[9px] font-bold text-slate-300 tracking-wider">{node.step}</span>
                <span className={`font-mono text-[8px] ${
                  node.state === 'DEGRADED' || node.state.includes('LAND') ? 'text-rose-400' : 'text-slate-500'
                }`}>{node.state}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-3 flex justify-between items-end border-t border-slate-800/80 pt-2">
        <div className="flex flex-col">
          <p className="text-[9px] font-mono text-slate-500 tracking-wider">Trend: {String(t?.confidence_trend ?? 'STABLE')}</p>
          <p className="text-[9px] font-mono text-slate-500 tracking-wider">Alert: {String(t?.operator_alert_level ?? 'NONE')}</p>
        </div>
        <p className={`font-mono text-[10px] tracking-widest px-2 py-0.5 rounded border ${
          cert?.certification_ready 
            ? 'border-teal-500/30 text-teal-400 bg-teal-500/10' 
            : 'border-amber-500/30 text-amber-400 bg-amber-500/10'
        }`}>
          CERT: {cert?.certification_ready ? 'READY' : 'PENDING'}
        </p>
      </div>
    </Panel>
  );
}
