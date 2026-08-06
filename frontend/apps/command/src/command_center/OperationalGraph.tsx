import { memo, useMemo } from 'react';
import ReactECharts from 'echarts-for-react';

export const OperationalGraph = memo(function OperationalGraph() {
  const option = useMemo(() => ({
    backgroundColor: 'transparent',
    series: [{
      type: 'graph',
      layout: 'force',
      symbolSize: 20,
      roam: true,
      label: { show: true, fontSize: 8, color: '#64748b' },
      force: { repulsion: 100, edgeLength: 40 },
      data: [
        { name: 'AIRCRAFT', itemStyle: { color: '#22d3a8' } },
        { name: 'MISSION', itemStyle: { color: '#a78bfa' } },
        { name: 'WEATHER', itemStyle: { color: '#38bdf8' } },
        { name: 'FAILURE', itemStyle: { color: '#f43f5e' } },
        { name: 'RECOVERY', itemStyle: { color: '#fb923c' } },
        { name: 'OPERATOR', itemStyle: { color: '#94a3b8' } },
      ],
      links: [
        { source: 'AIRCRAFT', target: 'MISSION' },
        { source: 'AIRCRAFT', target: 'WEATHER' },
        { source: 'MISSION', target: 'FAILURE' },
        { source: 'FAILURE', target: 'RECOVERY' },
        { source: 'RECOVERY', target: 'OPERATOR' },
      ],
      lineStyle: { color: '#1e293b', width: 1 }
    }]
  }), []);

  return <div className="h-40 w-full"><ReactECharts option={option} style={{ height: '100%' }} /></div>;
});
