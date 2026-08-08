import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Sphere } from '@react-three/drei';
import { Network, Users, Sliders, ShieldCheck, Play, Sparkles, Clock, Compass, Zap } from 'lucide-react';
import { tacticalAudio } from '../audio/tacticalAudio';

export const SwarmFormationBuilder: React.FC = () => {
  const [formationType, setFormationType] = useState<'v_formation' | 'diamond' | 'echelon' | 'trail' | 'ring'>('v_formation');
  const [separationDistM, setSeparationDistM] = useState(18.0); // meters
  const [formationHeadingDeg, setFormationHeadingDeg] = useState(45);
  const [stotSyncSeconds, setStotSyncSeconds] = useState(42.0); // Simultaneous Time-on-Target in seconds
  const [deploying, setDeploying] = useState(false);

  // Compute 3D Coordinates for each UAV based on formation pattern
  const computeSwarmPositions = (): { id: string; role: string; pos: [number, number, number]; speed: number }[] => {
    const d = separationDistM * 0.15; // Scale for canvas
    if (formationType === 'v_formation') {
      return [
        { id: 'UAV-01', role: 'LEADER', pos: [0, 1.5, -d], speed: 12.0 },
        { id: 'UAV-02', role: 'LEFT_WING', pos: [-d, 1.5, 0], speed: 12.4 },
        { id: 'UAV-03', role: 'RIGHT_WING', pos: [d, 1.5, 0], speed: 12.4 },
        { id: 'UAV-04', role: 'LEFT_TRAIL', pos: [-d * 2, 1.5, d], speed: 13.1 },
        { id: 'UAV-05', role: 'RIGHT_TRAIL', pos: [d * 2, 1.5, d], speed: 13.1 },
      ];
    } else if (formationType === 'diamond') {
      return [
        { id: 'UAV-01', role: 'LEADER', pos: [0, 1.5, -d], speed: 12.0 },
        { id: 'UAV-02', role: 'LEFT_FLANK', pos: [-d, 1.5, 0], speed: 12.2 },
        { id: 'UAV-03', role: 'RIGHT_FLANK', pos: [d, 1.5, 0], speed: 12.2 },
        { id: 'UAV-04', role: 'TAIL_GUARD', pos: [0, 1.5, d], speed: 12.0 },
        { id: 'UAV-05', role: 'RECON_CENTER', pos: [0, 2.2, 0], speed: 11.8 },
      ];
    } else if (formationType === 'echelon') {
      return [
        { id: 'UAV-01', role: 'LEADER', pos: [-d * 2, 1.5, -d * 2], speed: 12.0 },
        { id: 'UAV-02', role: 'SLOT_2', pos: [-d, 1.5, -d], speed: 12.2 },
        { id: 'UAV-03', role: 'SLOT_3', pos: [0, 1.5, 0], speed: 12.5 },
        { id: 'UAV-04', role: 'SLOT_4', pos: [d, 1.5, d], speed: 12.8 },
        { id: 'UAV-05', role: 'SLOT_5', pos: [d * 2, 1.5, d * 2], speed: 13.0 },
      ];
    } else if (formationType === 'ring') {
      const count = 5;
      return Array.from({ length: count }, (_, i) => {
        const angle = (i / count) * Math.PI * 2;
        return {
          id: `UAV-0${i + 1}`,
          role: i === 0 ? 'LEADER' : `ORBIT_${i}`,
          pos: [Math.cos(angle) * d * 1.5, 1.5, Math.sin(angle) * d * 1.5],
          speed: 12.0 + i * 0.2
        };
      });
    } else {
      // Trail
      return [
        { id: 'UAV-01', role: 'LEADER', pos: [0, 1.5, -d * 2], speed: 12.0 },
        { id: 'UAV-02', role: 'TRAIL_1', pos: [0, 1.5, -d], speed: 12.1 },
        { id: 'UAV-03', role: 'TRAIL_2', pos: [0, 1.5, 0], speed: 12.2 },
        { id: 'UAV-04', role: 'TRAIL_3', pos: [0, 1.5, d], speed: 12.3 },
        { id: 'UAV-05', role: 'TRAIL_4', pos: [0, 1.5, d * 2], speed: 12.4 },
      ];
    }
  };

  const swarm = computeSwarmPositions();

  const handleDeploySwarm = () => {
    setDeploying(true);
    tacticalAudio.playChirp(1080, 90);
    tacticalAudio.speak(`Coordinated ${formationType.replace('_', ' ')} deployed. Simultaneous time on target synced across 5 units at ${stotSyncSeconds} seconds.`);
    setTimeout(() => setDeploying(false), 1200);
  };

  return (
    <div className="h-full w-full bg-[#010409] text-slate-200 p-6 flex flex-col font-sans overflow-hidden select-none">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
        <div className="flex items-center space-x-3">
          <span className="px-2.5 py-1 rounded bg-sky-500/10 text-sky-400 border border-sky-500/30 text-xs font-mono font-bold">
            SWARM FORMATION IDE v4.0
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Multi-Vehicle Coordinated Swarm & STOT Synchronizer
          </h2>
          <span className="text-xs font-mono text-slate-500">5 UAV P2P Mesh</span>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-500/10 border border-sky-500/30 text-xs font-mono text-sky-300">
            <Clock className="w-3.5 h-3.5 text-sky-400" />
            <span>STOT ETA: T-{stotSyncSeconds.toFixed(0)}s SYNCED</span>
          </div>

          <button
            onClick={handleDeploySwarm}
            disabled={deploying}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-xs font-mono font-semibold text-white shadow-lg shadow-sky-600/20 transition-all disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            <span>{deploying ? 'Broadcasting Mesh...' : 'Deploy Swarm Formation'}</span>
          </button>
        </div>
      </div>

      {/* Main Split: 3D Swarm Viewport + Formation Controls */}
      <div className="flex-1 flex gap-4 overflow-hidden">
        {/* 3D WebGL Swarm Viewport */}
        <div className="flex-1 rounded-xl border border-slate-800 bg-[#020617] relative overflow-hidden">
          <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur-md p-3.5 rounded-xl border border-slate-800 font-mono text-xs space-y-1 shadow-xl">
            <div className="text-sky-400 font-bold flex items-center gap-1.5">
              <Network className="w-4 h-4 text-sky-400" />
              <span>COORDINATED P2P SWARM</span>
            </div>
            <div className="text-slate-300 text-[11px]">
              Formation: <strong className="text-white uppercase">{formationType.replace('_', ' ')}</strong> • Separation: <strong className="text-white">{separationDistM}m</strong>
            </div>
            <div className="text-slate-400 text-[10px]">
              Collision Avoidance Margin: <strong className="text-emerald-400">18.4m Certified Safe</strong>
            </div>
          </div>

          <Canvas camera={{ position: [0, 8, 8], fov: 45 }}>
            <ambientLight intensity={0.8} />
            <directionalLight position={[5, 10, 5]} intensity={1.2} />
            <pointLight position={[-5, 5, -5]} intensity={0.6} color="#38bdf8" />
            
            <Grid position={[0, -0.2, 0]} args={[16, 16]} cellColor="#1e293b" sectionColor="#38bdf8" fadeDistance={25} />

            {/* Render Synchronized UAV Nodes */}
            {swarm.map((uav, idx) => {
              const isLeader = idx === 0;
              return (
                <group key={uav.id} position={uav.pos}>
                  {/* UAV Fuselage */}
                  <mesh>
                    <boxGeometry args={[0.6, 0.12, 0.6]} />
                    <meshStandardMaterial 
                      color={isLeader ? "#0284c7" : "#0f172a"} 
                      roughness={0.2} 
                      metalness={0.9} 
                    />
                  </mesh>

                  {/* Beacon Light */}
                  <mesh position={[0, 0.1, 0]}>
                    <sphereGeometry args={[0.08, 12, 12]} />
                    <meshStandardMaterial 
                      color={isLeader ? "#38bdf8" : "#10b981"} 
                      emissive={isLeader ? "#38bdf8" : "#10b981"} 
                      emissiveIntensity={1.0} 
                    />
                  </mesh>

                  {/* Collision Buffer Halo */}
                  <Sphere args={[0.7, 16, 16]}>
                    <meshStandardMaterial 
                      color="#38bdf8" 
                      transparent 
                      opacity={0.12} 
                      wireframe={true} 
                    />
                  </Sphere>
                </group>
              );
            })}

            <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
          </Canvas>
        </div>

        {/* Formation Sidebar Controls */}
        <div className="w-84 rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md flex flex-col justify-between overflow-y-auto space-y-6">
          <div className="space-y-5">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <Users className="w-4 h-4 text-sky-400" />
                Formation Geometry & STOT
              </h3>
              <p className="text-[11px] text-slate-400 mt-1">Select swarm shape and throttle speed synchronization.</p>
            </div>

            {/* Formation Mode Grid */}
            <div className="space-y-2">
              <span className="text-xs font-mono text-slate-300 block">Formation Geometry</span>
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                {[
                  { id: 'v_formation', label: 'V-Formation' },
                  { id: 'diamond', label: 'Diamond Escort' },
                  { id: 'echelon', label: 'Echelon Line' },
                  { id: 'ring', label: 'Ring Perimeter' },
                ].map((f) => (
                  <button
                    key={f.id}
                    onClick={() => {
                      setFormationType(f.id as any);
                      tacticalAudio.playChirp(880, 30);
                    }}
                    className={`p-2.5 rounded-lg border text-center transition-all ${
                      formationType === f.id
                        ? 'bg-sky-500/20 text-sky-300 border-sky-500/40 font-bold'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Slider 1: Separation Distance */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Inter-UAV Spacing</span>
                <span className="text-sky-400 font-bold">{separationDistM} meters</span>
              </div>
              <input
                type="range"
                min="5"
                max="40"
                step="1"
                value={separationDistM}
                onChange={(e) => setSeparationDistM(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
              <span className="text-[10px] text-slate-500 font-mono block">STANAG 4586 minimum safety margin: 8.0m.</span>
            </div>

            {/* Slider 2: STOT Countdown Sync */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">STOT Synchronized Arrival</span>
                <span className="text-emerald-400 font-bold">T-{stotSyncSeconds}s</span>
              </div>
              <input
                type="range"
                min="15"
                max="90"
                step="1"
                value={stotSyncSeconds}
                onChange={(e) => setStotSyncSeconds(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
              <span className="text-[10px] text-slate-500 font-mono block">Dynamic speed throttle adjusts individual UAVs.</span>
            </div>
          </div>

          {/* Swarm Telemetry Sync Card */}
          <div className="p-3.5 rounded-xl bg-sky-950/40 border border-sky-500/30 text-xs font-mono space-y-1.5">
            <div className="flex items-center gap-1.5 text-sky-400 font-bold">
              <ShieldCheck className="w-4 h-4 text-sky-400" />
              <span>P2P MESH CONSENSUS</span>
            </div>
            <p className="text-[11px] text-slate-300">
              5 vehicles locked in Byzantine fault-tolerant mesh. Leader election latency: <strong>3.8ms</strong>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
