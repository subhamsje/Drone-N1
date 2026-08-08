import React, { useState, useEffect } from 'react';
import { 
  Radio, 
  BatteryCharging, 
  Compass, 
  Activity, 
  Layers, 
  Globe, 
  Camera, 
  Sliders, 
  Play, 
  Square, 
  RotateCcw, 
  ShieldAlert, 
  Terminal as TerminalIcon, 
  Wifi, 
  Crosshair, 
  Zap, 
  ArrowUpRight, 
  CheckCircle2,
  AlertTriangle,
  Lock,
  Cpu,
  Video
} from 'lucide-react';
import { tacticalAudio } from '../audio/tacticalAudio';
import { useCognitionStore } from '../stores/cognitionStore';

export const EnterpriseCommandDeck: React.FC = () => {
  const [flightMode, setFlightMode] = useState<'OFFBOARD' | 'HOLD' | 'POSCTL' | 'RTL' | 'EMERGENCY'>('OFFBOARD');
  const [armed, setArmed] = useState(true);
  const [activeTab, setActiveTab] = useState<'tactical_map' | 'fpv_feed' | 'telemetry_stream' | 'safety_rules'>('tactical_map');
  const [gimbalPitch, setGimbalPitch] = useState(-30);
  const [telemetryLogs, setTelemetryLogs] = useState<string[]>([
    '[00:00:01.042] [MAVLINK] HEARTBEAT received from System 1 Component 1 (Type: QUADROTOR, Autopilot: PX4)',
    '[00:00:01.084] [EKF2] Fused: RTK-GPS (19 Sats) + ORB-SLAM3 VIO. Position variance: 0.004m²',
    '[00:00:01.120] [OFFBOARD] Receiving setpoints at 50Hz. Trajectory spline #04 validated clean.',
    '[00:00:01.168] [SECURITY] ECDSA signature validated (SHA256: 4fb2d7e58e70...85fc). Replay counter: 1420',
  ]);

  // Live periodic telemetry ticker
  useEffect(() => {
    const interval = setInterval(() => {
      const msgs = [
        `[${new Date().toISOString().slice(11, 23)}] [TELEMETRY] Motor RPM: M1: 5820 | M2: 5815 | M3: 5840 | M4: 5810 (Harmonics: 0.012 m/s²)`,
        `[${new Date().toISOString().slice(11, 23)}] [RADIO] RSSI: -44 dBm | Link Quality: 99.8% | Bandwidth: 4.8 Mbps (5G PRIVATE)`,
        `[${new Date().toISOString().slice(11, 23)}] [SOVEREIGN_KERNEL] MPC Horizon N=5 solved in 2.1ms. Cost: 0.042 (Safety margin: 18.2m)`,
      ];
      const randomMsg = msgs[Math.floor(Math.random() * msgs.length)];
      setTelemetryLogs(prev => [randomMsg, ...prev.slice(0, 15)]);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const handleFlightModeChange = (mode: typeof flightMode) => {
    setFlightMode(mode);
    tacticalAudio.playChirp(mode === 'EMERGENCY' ? 1200 : 920, 60);
    tacticalAudio.speak(`Flight mode changed to ${mode}.`);
  };

  const toggleArm = () => {
    const next = !armed;
    setArmed(next);
    tacticalAudio.playChirp(next ? 1040 : 660, 80);
    tacticalAudio.speak(next ? "Vehicle armed and ready for takeoff." : "Vehicle disarmed.");
  };

  return (
    <div className="h-full w-full bg-[#0b0f19] text-slate-200 flex flex-col font-sans overflow-hidden select-none">
      {/* 1. TOP DEFENSE AEROSPACE HUD BAR */}
      <div className="h-11 bg-[#111827] border-b border-slate-800 px-4 flex items-center justify-between text-xs font-mono shrink-0">
        {/* Left: Vehicle Callout & State */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-bold text-slate-100 text-sm">ALTARIA-ALPHA-01</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 border border-slate-700">
              PX4 FMUv6X
            </span>
          </div>

          <div className="h-4 w-px bg-slate-800" />

          {/* Armed / Disarmed Badge */}
          <button
            onClick={toggleArm}
            className={`px-2.5 py-0.5 rounded text-[11px] font-bold tracking-wider transition-all ${
              armed
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                : 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
            }`}
          >
            {armed ? '● ARMED' : '○ DISARMED'}
          </button>

          {/* Flight Mode Dropdown */}
          <div className="flex items-center space-x-1 bg-slate-900 border border-slate-800 rounded px-2 py-0.5">
            <span className="text-slate-500 text-[10px]">MODE:</span>
            <select
              value={flightMode}
              onChange={(e) => handleFlightModeChange(e.target.value as any)}
              className="bg-transparent text-cyan-400 font-bold focus:outline-none cursor-pointer"
            >
              <option value="OFFBOARD">OFFBOARD (AI AUTONOMOUS)</option>
              <option value="HOLD">HOLD (LOITER)</option>
              <option value="POSCTL">POSITION CONTROL</option>
              <option value="RTL">RETURN TO LAUNCH (RTL)</option>
              <option value="EMERGENCY">EMERGENCY LAND</option>
            </select>
          </div>
        </div>

        {/* Right: Telemetry Vital Indicators */}
        <div className="flex items-center space-x-6 text-[11px]">
          {/* RTK GPS */}
          <div className="flex items-center space-x-1.5 text-slate-300">
            <Compass className="w-3.5 h-3.5 text-sky-400" />
            <span>RTK 3D FIX (19 SATS)</span>
          </div>

          {/* 5G Radio Signal */}
          <div className="flex items-center space-x-1.5 text-slate-300">
            <Wifi className="w-3.5 h-3.5 text-emerald-400" />
            <span>-44 dBm (5G SA)</span>
          </div>

          {/* Battery */}
          <div className="flex items-center space-x-1.5 text-slate-300">
            <BatteryCharging className="w-3.5 h-3.5 text-emerald-400" />
            <span>15.8V (94%)</span>
          </div>

          {/* Link Latency */}
          <div className="flex items-center space-x-1.5 text-slate-300">
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>12.4ms RTT</span>
          </div>
        </div>
      </div>

      {/* 2. MAIN COCKPIT VIEWPORT SPLIT */}
      <div className="flex-1 flex overflow-hidden">
        {/* CENTER VIEWPORT (Tactical Map / FPV Stream / Telemetry) */}
        <div className="flex-1 flex flex-col overflow-hidden bg-[#0d121f] border-r border-slate-800/80 relative">
          {/* Sub-tab switcher */}
          <div className="h-9 bg-[#111827]/80 border-b border-slate-800/80 px-4 flex items-center justify-between text-xs font-mono">
            <div className="flex items-center space-x-1">
              {[
                { id: 'tactical_map', label: 'Tactical 3D Map', icon: Globe },
                { id: 'fpv_feed', label: 'H.264 WebRTC FPV', icon: Video },
                { id: 'telemetry_stream', label: '50Hz MAVLink Console', icon: TerminalIcon },
              ].map((tab) => {
                const Icon = tab.icon;
                const active = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center space-x-1.5 px-3 py-1 rounded text-[11px] font-medium transition-all ${
                      active
                        ? 'bg-slate-800 text-white font-semibold border border-slate-700'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5 text-sky-400" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>

            <div className="text-[10px] text-slate-500 font-mono">
              LAT: 30.2672° N • LON: -97.7431° W • ALT: 45.2m AGL
            </div>
          </div>

          {/* Interactive Center Screen */}
          <div className="flex-1 relative overflow-hidden bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] flex items-center justify-center p-6">
            {activeTab === 'tactical_map' && (
              <div className="w-full h-full rounded-xl border border-slate-800 bg-[#090d16] p-6 relative overflow-hidden flex flex-col justify-between">
                {/* 3D Map Overlays */}
                <div className="flex justify-between items-start z-10 font-mono text-xs">
                  <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-lg space-y-1">
                    <div className="text-sky-400 font-bold">FLIGHT CORRIDOR ALPHA</div>
                    <div className="text-slate-400 text-[11px]">Speed: 12.0 m/s • Pitch: -2.4° • Yaw: 045°</div>
                    <div className="text-emerald-400 text-[10px]">VIO Optical Flow: 142 Features Tracked</div>
                  </div>

                  <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-lg space-y-1 text-right">
                    <div className="text-slate-200 font-bold">NEXT WAYPOINT: WP-03</div>
                    <div className="text-slate-400 text-[11px]">Distance: 184 meters • ETE: 15.3s</div>
                    <div className="text-cyan-400 text-[10px]">Geofence Margin: 6.0m Lateral</div>
                  </div>
                </div>

                {/* Simulated Radar Reticle */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-20">
                  <div className="w-96 h-96 rounded-full border border-sky-500 flex items-center justify-center">
                    <div className="w-64 h-64 rounded-full border border-sky-500/50 flex items-center justify-center">
                      <div className="w-32 h-32 rounded-full border border-sky-500/30" />
                    </div>
                  </div>
                </div>

                {/* Bottom Quick Flight Actions */}
                <div className="flex items-center justify-between z-10 pt-4 border-t border-slate-800 font-mono text-xs">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleFlightModeChange('HOLD')}
                      className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold transition-all"
                    >
                      HOLD / LOITER
                    </button>
                    <button
                      onClick={() => handleFlightModeChange('RTL')}
                      className="px-3 py-1.5 rounded bg-sky-600 hover:bg-sky-500 text-white font-semibold transition-all shadow-md shadow-sky-600/20"
                    >
                      RETURN TO BASE (RTL)
                    </button>
                  </div>

                  <button
                    onClick={() => handleFlightModeChange('EMERGENCY')}
                    className="px-3 py-1.5 rounded bg-rose-600/30 border border-rose-500/40 text-rose-300 font-bold hover:bg-rose-600/50 transition-all"
                  >
                    ⚠ EMERGENCY LAND
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'fpv_feed' && (
              <div className="w-full h-full rounded-xl border border-slate-800 bg-black relative overflow-hidden flex items-center justify-center font-mono">
                {/* Simulated Video HUD */}
                <div className="text-center space-y-2">
                  <Video className="w-8 h-8 text-sky-400 mx-auto animate-pulse" />
                  <div className="text-xs text-slate-400 font-mono">H.264 / NVENC LOW-LATENCY STREAM (1080p@60FPS)</div>
                  <div className="text-[10px] text-emerald-400 font-mono">Bitrate: 4.8 Mbps • Glass-to-Glass Latency: 18.2ms</div>
                </div>

                {/* AI Bounding Box Reticle */}
                <div className="absolute top-1/4 left-1/3 w-32 h-24 border-2 border-emerald-400/80 rounded flex flex-col justify-between p-1 text-[9px] text-emerald-400 font-mono">
                  <span>TARGET: VEHICLE #42</span>
                  <span className="text-right">CONF: 96.4%</span>
                </div>
              </div>
            )}

            {activeTab === 'telemetry_stream' && (
              <div className="w-full h-full rounded-xl border border-slate-800 bg-[#050811] p-4 font-mono text-xs text-slate-300 overflow-y-auto space-y-1.5">
                <div className="text-slate-500 text-[10px] pb-2 border-b border-slate-800 uppercase tracking-wider">
                  Live 50Hz MAVLink Telemetry Console & Raw Socket Packets
                </div>
                {telemetryLogs.map((log, i) => (
                  <div key={i} className="leading-relaxed hover:text-white font-mono text-[11px] truncate">
                    {log}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Bottom Live Telemetry Stream Ticker */}
          <div className="h-28 bg-[#090d16] border-t border-slate-800 p-3 font-mono text-xs overflow-hidden flex flex-col justify-between">
            <div className="flex items-center justify-between text-[10px] text-slate-400 uppercase tracking-wider pb-1 border-b border-slate-800/60">
              <span className="flex items-center gap-1.5 text-sky-400">
                <Activity className="w-3 h-3" /> REALTIME HARDWARE ACTUATOR SPECTRUM
              </span>
              <span>120Hz EKF2 STATE FUSION</span>
            </div>
            <div className="grid grid-cols-4 gap-4 pt-1 text-[11px]">
              <div className="p-2 rounded bg-slate-900 border border-slate-800">
                <div className="text-slate-500 text-[10px]">MOTOR 1 (RPM)</div>
                <div className="text-slate-200 font-bold text-sm">5,820 <span className="text-[10px] text-emerald-400 font-normal">NOMINAL</span></div>
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800">
                <div className="text-slate-500 text-[10px]">MOTOR 2 (RPM)</div>
                <div className="text-slate-200 font-bold text-sm">5,815 <span className="text-[10px] text-emerald-400 font-normal">NOMINAL</span></div>
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800">
                <div className="text-slate-500 text-[10px]">MOTOR 3 (RPM)</div>
                <div className="text-slate-200 font-bold text-sm">5,840 <span className="text-[10px] text-emerald-400 font-normal">NOMINAL</span></div>
              </div>
              <div className="p-2 rounded bg-slate-900 border border-slate-800">
                <div className="text-slate-500 text-[10px]">MOTOR 4 (RPM)</div>
                <div className="text-slate-200 font-bold text-sm">5,810 <span className="text-[10px] text-emerald-400 font-normal">NOMINAL</span></div>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT CONTROL DRAWER (Gimbal Joystick & Mission Controls) */}
        <div className="w-80 bg-[#111827] p-4 flex flex-col justify-between text-xs font-mono overflow-y-auto space-y-6">
          <div className="space-y-5">
            {/* Header */}
            <div className="border-b border-slate-800 pb-3">
              <h3 className="font-bold text-sm text-slate-100 uppercase tracking-tight flex items-center gap-1.5">
                <Crosshair className="w-4 h-4 text-sky-400" />
                Payload & Gimbal Control
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">3-Axis EO/IR Stabilized Optical Pod</p>
            </div>

            {/* Gimbal Pitch Slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-400">Gimbal Pitch</span>
                <span className="text-sky-400 font-bold">{gimbalPitch}°</span>
              </div>
              <input
                type="range"
                min="-90"
                max="20"
                value={gimbalPitch}
                onChange={(e) => {
                  setGimbalPitch(parseInt(e.target.value));
                  tacticalAudio.playChirp(720, 20);
                }}
                className="w-full h-1.5 bg-slate-800 rounded appearance-none cursor-pointer accent-sky-400"
              />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>Nadir (-90°)</span>
                <span>Horizon (0°)</span>
                <span>Climb (+20°)</span>
              </div>
            </div>

            {/* Zero-Trust Compliance Badge */}
            <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-[10px] uppercase">Cryptographic Command Signer</span>
                <Lock className="w-3.5 h-3.5 text-emerald-400" />
              </div>
              <div className="text-emerald-400 font-bold text-xs">ECDSA NIST256p ACTIVE</div>
              <div className="text-slate-500 text-[10px]">STANAG 4586 Level 4 Verified</div>
            </div>
          </div>

          {/* Action Button */}
          <div className="border-t border-slate-800 pt-3">
            <button
              onClick={() => {
                tacticalAudio.playChirp(1040, 80);
                tacticalAudio.speak("Autonomous waypoint corridor uploaded to flight controller.");
              }}
              className="w-full py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-semibold shadow-md shadow-sky-600/20 transition-all text-xs"
            >
              Upload Mission to Vehicle
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
