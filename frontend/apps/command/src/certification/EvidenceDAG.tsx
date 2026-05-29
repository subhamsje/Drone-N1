import { Panel } from '@altaria/ui';
import { useOperatingStore } from '../stores/operatingStore';

export function EvidenceDAG({ evidence }: { evidence?: unknown }) {
  const fromStore = useOperatingStore((s) => s.operating?.cognition?.certification?.evidence_dag);
  const dag = (evidence ?? fromStore) as {
    nodes?: Array<{ node_type: string; state_hash: string; bounded: boolean }>;
    edges?: Array<{ from: string; to: string }>;
  } | undefined;

  return (
    <Panel title="Certification Evidence DAG">
      <div className="flex flex-col gap-1">
        {(dag?.nodes ?? []).map((n, i) => (
          <div key={i} className="flex items-center gap-2 text-[10px]">
            <span className={`h-2 w-2 rounded-full ${n.bounded ? 'bg-cyan-500' : 'bg-slate-600'}`} />
            <span className="font-mono text-slate-400">{n.node_type}</span>
            <span className="truncate text-slate-600">{n.state_hash}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}
