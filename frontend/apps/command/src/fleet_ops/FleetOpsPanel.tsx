import { Panel } from '@altaria/ui';
import { useCognitionStore } from '../stores/cognitionStore';

export function FleetOpsPanel() {
  const ops = useCognitionStore((s) => s.envelope?.fleet_ops) as Record<string, unknown> | undefined;
  const econ = useCognitionStore((s) => s.envelope?.economics) as Record<string, unknown> | undefined;

  return (
    <Panel title="Planetary Fleet Operations">
      <div className="space-y-2 font-mono text-[10px] text-slate-400">
        <p>Rebalance: {String((ops as { rebalance_recommended?: boolean })?.rebalance_recommended ?? false)}</p>
        <p>Throughput: {JSON.stringify((ops as { airspace_throughput?: object })?.airspace_throughput ?? {})}</p>
        <p className="text-cyan-300/90">
          Leverage: {Number((econ as { operational_leverage_score?: number })?.operational_leverage_score ?? 0).toFixed(2)}
        </p>
        <p>Maint forecast: {JSON.stringify((ops as { maintenance_forecast?: object })?.maintenance_forecast ?? {})}</p>
      </div>
    </Panel>
  );
}
