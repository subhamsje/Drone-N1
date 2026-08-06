import { motion, AnimatePresence } from 'framer-motion';
import { useOperatingStore } from '../stores/operatingStore';

export function SystemDetailDrawer() {
  const active = useOperatingStore((s) => s.activeDrawer);
  const setActive = useOperatingStore((s) => s.setActiveDrawer);
  const op = useOperatingStore((s) => s.operating);
  const platform = useOperatingStore((s) => s.platform);

  if (!active) return null;

  const content: Record<string, { title: string, stats: Record<string, any>, logs: string[] }> = {
    ros2: {
      title: 'ROS2 Node Topology',
      stats: {
        status: (platform.edge as any)?.status ?? 'CONNECTED',
        bridge: 'Altaria_DDS_Bridge_v1',
        nodes: ['/cognition_kernel', '/telemetry_ingest', '/gazebo_bridge'],
        topics: ['/fmu/out/vehicle_gps_position', '/fmu/out/sensor_combined']
      },
      logs: ['[ROS2] Subscribed to GPS topic', '[ROS2] Heartbeat established']
    },
    gazebo: {
      title: 'Gazebo Physics Runtime',
      stats: {
        status: (platform.edge as any)?.gazebo_running ? 'RUNNING' : 'OFFLINE',
        world: 'Altaria_Planetary_Simulation',
        realtime_factor: '0.98x',
        instances: 1
      },
      logs: ['[GZ] Physics engine stable', '[GZ] SITL bridge active']
    },
    px4: {
      title: 'PX4 Autopilot Link',
      stats: {
        status: (op as any)?.flight_stack?.connected ? 'LINKED' : 'DISCONNECTED',
        stack: (op as any)?.flight_stack?.stack ?? 'PX4 v1.14',
        transport: 'UDP :14540',
        armed: (op as any)?.aircraft?.armed ? 'YES' : 'NO'
      },
      logs: ['[PX4] MAVLink handshake complete', '[PX4] Version verified']
    },
    mavsdk: {
      title: 'MAVSDK Command Authority',
      stats: {
        status: (op as any)?.flight_stack?.mode ? 'ACTIVE' : 'INACTIVE',
        version: 'v3.15.0',
        commands: ['ARM', 'DISARM', 'TAKEOFF', 'LAND', 'RTL', 'HOLD', 'GOTO'],
      },
      logs: ['[MAVSDK] Authority acquired', '[MAVSDK] GOTO command validated']
    },
    lake: {
      title: 'Telemetry Lake (ClickHouse)',
      stats: {
        status: (op as any)?.analytics?.connected ? 'STREAMING' : 'OFFLINE',
        engine: 'MergeTree',
        retention: '365 Days',
        buffer: '50,000 Records'
      },
      logs: ['[LAKE] Flushing telemetry batch...', '[LAKE] SQL Aggregation succeeded']
    }
  };

  const data = content[active];
  if (!data) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 20 }}
        className="absolute top-0 right-0 z-50 h-full w-80 bg-slate-950/95 border-l border-slate-800 shadow-2xl backdrop-blur-xl p-4 flex flex-col gap-4 pointer-events-auto"
      >
        <header className="flex items-center justify-between border-b border-slate-800 pb-2">
          <h2 className="font-mono text-xs font-bold text-cyan-400 uppercase tracking-widest">{data.title}</h2>
          <button onClick={() => setActive(null)} className="text-slate-500 hover:text-white font-mono text-[10px]">[✕]</button>
        </header>

        <div className="flex flex-col gap-4 overflow-y-auto pr-1">
          <section className="flex flex-col gap-2">
            <p className="font-mono text-[8px] uppercase tracking-widest text-slate-500 font-bold">Parameters</p>
            <div className="grid grid-cols-1 gap-1.5">
              {Object.entries(data.stats).map(([k, v]) => (
                <div key={k} className="flex justify-between items-center bg-white/5 px-2 py-1 rounded">
                  <span className="font-mono text-[8px] uppercase text-slate-400">{k.replace(/_/g, ' ')}</span>
                  <span className="font-mono text-[9px] text-white font-bold">{Array.isArray(v) ? v.length : String(v)}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="flex flex-col gap-2">
            <p className="font-mono text-[8px] uppercase tracking-widest text-slate-500 font-bold">Operational Logs</p>
            <div className="flex flex-col gap-1 bg-black/40 p-2 rounded border border-slate-900 h-48 overflow-y-auto">
              {data.logs.map((log, i) => (
                <div key={i} className="font-mono text-[8px] text-cyan-600/80 leading-tight">
                  <span className="text-slate-700 mr-2">[{new Date().toLocaleTimeString()}]</span>
                  {log}
                </div>
              ))}
            </div>
          </section>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
