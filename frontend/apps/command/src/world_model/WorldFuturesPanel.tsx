import { memo, useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { Panel } from '@altaria/ui';
import { useCognitionStore } from '../stores/cognitionStore';

export const WorldFuturesPanel = memo(function WorldFuturesPanel() {
  const uiVersion = useCognitionStore((s) => s.uiVersion);
  const e = useCognitionStore((s) => s.envelope);

  const chartOption = useMemo(() => {
    const nodes =
      (e?.world_model?.forecast as {
        nodes?: Array<{ horizon_s: number; state_key: string; probability: number; severity: number }>;
      })?.nodes ?? [];
    return {
      backgroundColor: 'transparent',
      grid: { left: 40, right: 12, top: 24, bottom: 28 },
      xAxis: {
        type: 'category',
        data: nodes.map((n) => `${n.horizon_s}s`),
        axisLabel: { color: '#64748b', fontSize: 9 },
      },
      yAxis: { type: 'value', max: 1, axisLabel: { color: '#64748b', fontSize: 9 } },
      series: [
        {
          type: 'bar',
          data: nodes.map((n) => n.probability * n.severity),
          itemStyle: { color: '#38bdf8' },
        },
      ],
    };
  }, [uiVersion, e?.world_model?.forecast]);

  const foundation = e?.world_model?.foundation as
    | { generative_survivability?: number; preemptive_recommendation?: string }
    | undefined;
  const unc = e?.world_model?.uncertainty as { composite_uncertainty?: number } | undefined;

  if (!e) {
    return (
      <Panel title="Gazebo Counterfactual Futures" accent="cognition">
        <p className="text-[10px] text-slate-500">Awaiting ROS2 Gazebo physics bridge…</p>
      </Panel>
    );
  }

  return (
    <Panel title="Gazebo Counterfactual Futures" accent="cognition">
      <div className="mb-2 flex justify-between font-mono text-[10px]">
        <span className="text-cyan-400">GEN SURV {(foundation?.generative_survivability ?? 0).toFixed(2)}</span>
        <span className="text-slate-500">UNC {(unc?.composite_uncertainty ?? 0).toFixed(2)}</span>
      </div>
      {foundation?.preemptive_recommendation && (
        <p className="mb-2 text-[10px] text-amber-300">PREEMPT: {foundation.preemptive_recommendation}</p>
      )}
      <ReactECharts
        key={uiVersion}
        option={chartOption}
        style={{ height: 140 }}
        opts={{ renderer: 'canvas' }}
        notMerge
        lazyUpdate
      />
      <div className="mt-2 flex items-center gap-2 border-t border-slate-800/80 pt-2">
        <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-cyan-500" />
        <p className="font-mono text-[8px] tracking-widest text-slate-500 uppercase">
          LIVE ROS2 DDS · GAZEBO HEADLESS EVALUATION
        </p>
      </div>
    </Panel>
  );
});
