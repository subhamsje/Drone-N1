import { useOperatingStore } from '../stores/operatingStore';

export function SystemStatusHud() {
  const op = useOperatingStore((s) => s.operating);
  const platform = useOperatingStore((s) => s.platform);
  const stream = useOperatingStore((s) => s.stream);
  
  const connected = stream.connection === 'connected';
  const fs = (op as Record<string, any>)?.flight_stack || {};
  const edge = (op as Record<string, any>)?.edge_status || platform.edge || {};
  const lake = (op as Record<string, any>)?.analytics;

  // Real status derivation from backend telemetry
  const isRos2 = edge.status === 'CONNECTED';
  const isGazebo = edge.gazebo_running === true; 
  const isPx4 = fs.connected === true;
  const hasMavsdk = fs.connected === true && Boolean(fs.mode);
  const hasLake = lake?.connected === true;

  const statusColor = (val: boolean | string | undefined) => {
    if (val === true || val === 'CONNECTED') return 'text-emerald-400';
    if (val === 'DEGRADED' || val === 'connecting' || val === 'reconnecting') return 'text-amber-500';
    if (val === 'error') return 'text-red-500';
    return 'text-slate-600';
  };

  return (
    <div className="absolute inset-x-0 top-0 z-30 flex items-center justify-between border-b border-slate-800 bg-[#010409]/95 px-4 py-1.5 backdrop-blur-sm">
      <div className="flex items-center gap-4 font-mono text-[9px] uppercase tracking-widest">
        <div className="flex items-center gap-1.5">
          <span className={statusColor(isRos2)}>●</span>
          <span className="text-slate-500">ROS2:</span>
          <span className={statusColor(isRos2)}>{isRos2 ? 'ACTIVE' : 'OFFLINE'}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={statusColor(isGazebo)}>●</span>
          <span className="text-slate-500">GAZEBO:</span>
          <span className={statusColor(isGazebo)}>{isGazebo ? 'RUNNING' : 'OFFLINE'}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={statusColor(isPx4)}>●</span>
          <span className="text-slate-500">PX4:</span>
          <span className={statusColor(isPx4)}>{isPx4 ? 'LINKED' : 'DISCONNECTED'}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={statusColor(hasMavsdk)}>●</span>
          <span className="text-slate-500">MAVSDK:</span>
          <span className={statusColor(hasMavsdk)}>{hasMavsdk ? fs.mode?.toUpperCase() : 'INACTIVE'}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={statusColor(hasLake)}>●</span>
          <span className="text-slate-500">LAKE:</span>
          <span className={statusColor(hasLake)}>{hasLake ? 'STREAMING' : 'OFFLINE'}</span>
        </div>
      </div>

      <div className="flex items-center gap-4 font-mono text-[9px] uppercase tracking-widest border-l border-slate-800 pl-4">
        <div className="flex items-center gap-2">
          <span className="text-slate-500 text-[8px]">LATENCY:</span>
          <span className={stream.latencyMs > 100 ? 'text-amber-500' : 'text-cyan-400'}>
            {stream.latencyMs.toFixed(0)}MS
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-500 text-[8px]">DROP:</span>
          <span className={stream.packetsDropped > 0 ? 'text-red-500' : 'text-slate-500'}>
            {stream.packetsDropped}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-slate-500 text-[8px]">WS:</span>
          <span className={statusColor(stream.connection)}>
            {stream.connection.toUpperCase()}
          </span>
          {!connected && (
            <button 
              onClick={() => window.location.reload()}
              className="px-2 py-0.5 rounded bg-slate-800 text-[7px] text-white hover:bg-slate-700"
            >
              RECONNECT
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
