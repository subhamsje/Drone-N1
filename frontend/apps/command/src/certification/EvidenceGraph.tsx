import { memo, useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { useCognitionStore } from '../stores/cognitionStore';

export const EvidenceGraph = memo(function EvidenceGraph() {
  const envelope = useCognitionStore((s) => s.envelope);
  const chain = envelope?.cognition?.reasoning_chain ?? [];

  const option = useMemo(() => {
    const nodes = [
      { name: 'PERCEPTION', x: 0, y: 0, itemStyle: { color: '#38bdf8' } },
      { name: 'DECISION', x: 200, y: 0, itemStyle: { color: '#a78bfa' } },
      { name: 'RECOVERY', x: 400, y: 0, itemStyle: { color: '#f43f5e' } },
      { name: 'TRUST', x: 200, y: 100, itemStyle: { color: '#10b981' } },
    ];

    const links = [
      { source: 'PERCEPTION', target: 'DECISION' },
      { source: 'DECISION', target: 'RECOVERY' },
      { source: 'DECISION', target: 'TRUST' },
    ];

    // Map reasoning chain to dynamic nodes
    chain.forEach((msg, i) => {
      nodes.push({
        name: msg.slice(0, 15) + '...',
        x: 100 + i * 50,
        y: 50 + (i % 2) * 30,
        itemStyle: { color: '#64748b' },
      });
      links.push({ source: 'DECISION', target: msg.slice(0, 15) + '...' });
    });

    return {
      backgroundColor: 'transparent',
      tooltip: {},
      animationDurationUpdate: 1500,
      animationEasingUpdate: 'quinticInOut',
      series: [
        {
          type: 'graph',
          layout: 'none',
          symbolSize: 20,
          roam: true,
          label: { show: true, fontSize: 8, color: '#94a3b8' },
          edgeSymbol: ['circle', 'arrow'],
          edgeSymbolSize: [4, 8],
          data: nodes,
          links: links,
          lineStyle: { opacity: 0.8, width: 1, curveness: 0, color: '#334155' },
        },
      ],
    };
  }, [chain]);

  return (
    <div className="h-60 w-full">
      <ReactECharts option={option} style={{ height: '100%', width: '100%' }} />
    </div>
  );
});
