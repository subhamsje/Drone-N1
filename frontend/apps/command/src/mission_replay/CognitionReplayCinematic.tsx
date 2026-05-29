import { memo, useMemo, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { useCognitionStore } from '../stores/cognitionStore';
import { cognitionEngine } from '../config/runtime';

const PHASES = ['Perceive', 'Predict', 'Simulate', 'Evaluate', 'Adapt', 'Survive', 'Recover', 'Learn'];

export const ReplayTimeline = memo(function ReplayTimeline() {
  const frames = useCognitionStore((s) => s.replayFrames);
  const uiVersion = useCognitionStore((s) => s.uiVersion);
  const envelope = useCognitionStore((s) => s.envelope);
  const [scrub, setScrub] = useState(100);

  const t = cognitionEngine().renderState.twin;
  const projected = t.futureSurvivability;

  const markers = useMemo(() => {
    const out: Array<{ idx: number; label: string; type: string }> = [];
    frames.forEach((f, i) => {
      if (f.action && f.action !== 'NONE' && (i === 0 || frames[i - 1]?.action !== f.action)) {
        out.push({ idx: i, label: f.action, type: 'action' });
      }
      if (f.surv < 0.45) out.push({ idx: i, label: 'SURV↓', type: 'surv' });
      if (f.surv < 0.25) out.push({ idx: i, label: 'COLLAPSE', type: 'collapse' });
    });
    return out.slice(-10);
  }, [frames, uiVersion]);

  const option = useMemo(() => {
    const len = Math.max(frames.length, 2);
    const futureX = [len, len + 1, len + 2];
    return {
      backgroundColor: 'transparent',
      grid: { left: 44, right: 16, top: 14, bottom: 32 },
      xAxis: { show: false, max: len + 2 },
      yAxis: { min: 0, max: 1, splitLine: { lineStyle: { color: '#1e293b' } }, axisLabel: { color: '#64748b', fontSize: 9 } },
      series: [
        {
          name: 'memory',
          type: 'line',
          data: frames.map((f, i) => [i, f.surv]),
          smooth: true,
          symbol: 'none',
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(34, 211, 168, 0.3)' },
                { offset: 1, color: 'rgba(34, 211, 168, 0)' },
              ],
            },
          },
          lineStyle: { color: '#22d3a8', width: 2 },
        },
        {
          name: 'futures',
          type: 'line',
          data: [
            [len - 1, frames[frames.length - 1]?.surv ?? t.survivability],
            ...projected.map((v, i) => [futureX[i], v]),
          ],
          smooth: true,
          symbol: 'circle',
          symbolSize: 4,
          lineStyle: { color: '#38bdf8', width: 1.5, type: 'dashed' },
          itemStyle: { color: '#38bdf8' },
        },
      ],
    };
  }, [frames, uiVersion, projected, t.survivability]);

  const phaseIdx = (envelope?.cycle ?? 0) % PHASES.length;
  const scrubIdx = Math.floor((scrub / 100) * Math.max(0, frames.length - 1));
  const scrubFrame = frames[scrubIdx];

  return (
    <div className="ops-panel ops-panel-accent flex h-full flex-col px-3 py-2">
      <div className="mb-1 flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-widest text-slate-500">
          Operational memory · futures projection
        </span>
        <span className="font-mono text-[9px] text-cyan-500">{PHASES[phaseIdx]}</span>
      </div>
      <div className="mb-1 flex justify-between gap-0.5">
        {PHASES.map((p, i) => (
          <span
            key={p}
            className={`flex-1 text-center font-mono text-[7px] uppercase ${
              i === phaseIdx ? 'text-cyan-400' : 'text-slate-700'
            }`}
          >
            {p.slice(0, 3)}
          </span>
        ))}
      </div>
      <ReactECharts key={uiVersion} option={option} style={{ height: 64 }} opts={{ renderer: 'canvas' }} lazyUpdate />
      <input
        type="range"
        min={0}
        max={100}
        value={scrub}
        onChange={(e) => setScrub(Number(e.target.value))}
        className="mt-1 h-1 w-full cursor-pointer accent-cyan-600"
      />
      <div className="mt-1 flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap gap-1">
          {markers.map((m) => (
            <span
              key={`${m.idx}-${m.label}`}
              className={`rounded px-1.5 py-0.5 font-mono text-[8px] ${
                m.type === 'surv'
                  ? 'bg-orange-950/60 text-orange-300'
                  : m.type === 'collapse'
                    ? 'bg-red-950/70 text-red-300'
                    : 'bg-slate-900 text-slate-400'
              }`}
            >
              {m.label}
            </span>
          ))}
        </div>
        {scrubFrame && (
          <span className="font-mono text-[8px] text-slate-500">
            t−{frames.length - scrubIdx} · {scrubFrame.action} · surv {(scrubFrame.surv * 100).toFixed(0)}%
          </span>
        )}
      </div>
    </div>
  );
});
