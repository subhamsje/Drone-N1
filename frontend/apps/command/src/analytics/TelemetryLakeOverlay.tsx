import { useQuery } from '@tanstack/react-query';
import ReactECharts from 'echarts-for-react';
import { useOperatingStore } from '../stores/operatingStore';
import { getEnterpriseAnalytics, getTelemetryLakeHistory } from '../api/intelligenceApi';

export function TelemetryLakeOverlay() {
  const open = useOperatingStore((s) => s.analyticsOverlayOpen);
  const setOpen = useOperatingStore((s) => s.setAnalyticsOverlayOpen);
  const activeTenant = useOperatingStore((s) => s.activeTenant);

  const lakeQ = useQuery({
    queryKey: ['telemetryLake', activeTenant],
    queryFn: () => getTelemetryLakeHistory(activeTenant),
    retry: false,
  });

  const entQ = useQuery({
    queryKey: ['enterpriseAnalytics', activeTenant],
    queryFn: () => getEnterpriseAnalytics(activeTenant),
    retry: false,
  });

  if (!open) return null;

  const hoursData = (lakeQ.data as { hours?: number[] })?.hours ?? [];
  const survData = (entQ.data as { survivability?: number[] })?.survivability ?? [];
  const wearData = (entQ.data as { wear?: number[] })?.wear ?? [];

  const hasData = hoursData.length > 0 || survData.length > 0;

  if (!hasData && !lakeQ.isLoading && !entQ.isLoading) {
    return (
      <div className="absolute inset-0 z-40 flex items-center justify-center bg-[#010409]/95 p-8 backdrop-blur-xl">
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="absolute right-6 top-6 font-mono text-xs uppercase tracking-widest text-slate-500 hover:text-white"
        >
          [✕] Close Analytics
        </button>
        <div className="flex flex-col items-center gap-4">
          <h1 className="font-mono text-xl text-amber-500">NO OPERATIONAL DATA AVAILABLE</h1>
          <p className="font-mono text-xs text-slate-400">Context: {activeTenant} • Fly a mission to populate the Telemetry Lake.</p>
        </div>
      </div>
    );
  }

  const flightHoursOption = {
    backgroundColor: 'transparent',
    title: {
      text: 'Fleet Flight Hours (7d)',
      textStyle: { color: '#94a3b8', fontSize: 12, fontFamily: 'JetBrains Mono' },
    },
    tooltip: { trigger: 'axis', backgroundColor: '#0f172a', borderColor: '#334155', textStyle: { color: '#e2e8f0' } },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#1e293b' } } },
    series: [
      {
        data: hoursData.length ? hoursData : [0, 0, 0, 0, 0, 0, 0],
        type: 'bar',
        itemStyle: { color: '#38bdf8' },
      },
    ],
  };

  const survWearOption = {
    backgroundColor: 'transparent',
    title: {
      text: 'Survivability vs. Fleet Wear',
      textStyle: { color: '#94a3b8', fontSize: 12, fontFamily: 'JetBrains Mono' },
    },
    tooltip: { trigger: 'axis', backgroundColor: '#0f172a', borderColor: '#334155', textStyle: { color: '#e2e8f0' } },
    legend: { data: ['Mean Survivability', 'Avg Motor Wear'], textStyle: { color: '#94a3b8' }, right: 10 },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: [
      { type: 'value', min: 0.8, max: 1, splitLine: { lineStyle: { color: '#1e293b' } } },
      { type: 'value', min: 0, max: 0.5, splitLine: { show: false } },
    ],
    series: [
      {
        name: 'Mean Survivability',
        type: 'line',
        smooth: true,
        data: survData.length ? survData : [1, 1, 1, 1, 1, 1, 1],
        itemStyle: { color: '#22d3a8' },
      },
      {
        name: 'Avg Motor Wear',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        data: wearData.length ? wearData : [0, 0, 0, 0, 0, 0, 0],
        itemStyle: { color: '#f59e0b' },
      },
    ],
  };

  return (
    <div className="absolute inset-0 z-40 flex items-center justify-center bg-[#010409]/95 p-8 backdrop-blur-xl">
      <button
        type="button"
        onClick={() => setOpen(false)}
        className="absolute right-6 top-6 font-mono text-xs uppercase tracking-widest text-slate-500 hover:text-white"
      >
        [✕] Close Analytics
      </button>

      <div className="flex h-full w-full max-w-7xl flex-col gap-6">
        <header className="flex flex-col gap-1 border-b border-slate-800 pb-4">
          <h1 className="font-mono text-2xl uppercase tracking-widest text-cyan-500">Telemetry Lake Enterprise Analytics</h1>
          <p className="font-mono text-xs text-slate-400">Context: {activeTenant} • Multi-Tenant Partitioning Active</p>
        </header>

        <div className="grid flex-1 grid-cols-2 gap-6">
          <div className="flex flex-col gap-4 rounded border border-slate-800/80 bg-slate-900/50 p-4">
            <ReactECharts option={flightHoursOption} style={{ height: '100%', width: '100%' }} />
          </div>
          <div className="flex flex-col gap-4 rounded border border-slate-800/80 bg-slate-900/50 p-4">
            <ReactECharts option={survWearOption} style={{ height: '100%', width: '100%' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
