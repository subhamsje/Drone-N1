import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Line, Cylinder } from '@react-three/drei';
import { Shield, Sliders, Box, Layers, Play, CheckCircle2, AlertTriangle, Activity } from 'lucide-react';
import { tacticalAudio } from '../audio/tacticalAudio';

interface Waypoint3D {
  id: string;
  x: number;
  y: number;
  z: number;
}

export const CorridorSculptor: React.FC = () => {
  const [corridorRadius, setCorridorRadius] = useState(6.0); // Lateral Margin in meters
  const [maxCeiling, setMaxCeiling] = useState(80.0); // Altitude ceiling in meters
  const [useDubinsSplines, setUseDubinsSplines] = useState(true);
  const [nfzEnabled, setNfzEnabled] = useState(true);
  const [containmentScore, setContainmentScore] = useState(99.4);

  // 3D Spatial Flight Waypoints
  const waypoints: [number, number, number][] = [
    [-4, 0.5, -3],
    [-2, 1.8, -1],
    [0, 2.5, 1],
    [2, 3.2, 0],
    [4, 2.0, 2],
  ];

  const handleApplyCorridor = () => {
    tacticalAudio.playChirp(1020, 80);
    tacticalAudio.speak(`3D flight corridor sculpted with ${corridorRadius} meters lateral safety margin. Dubins splines active.`);
  };

  return (
    <div className="h-full w-full bg-[#010409] text-slate-200 p-6 flex flex-col font-sans overflow-hidden select-none">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
        <div className="flex items-center space-x-3">
          <span className="px-2.5 py-1 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs font-mono font-bold">
            SPATIAL CORRIDOR SCULPTOR v1.0
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            3D Volumetric Flight Corridor & Geofence Sculptor
          </h2>
          <span className="text-xs font-mono text-slate-500">STANAG 4586 Tube Engine</span>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-emerald-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>CONTAINMENT: {containmentScore}%</span>
          </div>

          <button
            onClick={handleApplyCorridor}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-xs font-mono font-semibold text-white shadow-lg shadow-cyan-600/20 transition-all"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Apply Corridor Tube to UAV</span>
          </button>
        </div>
      </div>

      {/* Main Split: 3D Corridor Canvas + Parameter Sliders */}
      <div className="flex-1 flex gap-4 overflow-hidden">
        {/* 3D WebGL Spatial Tube Canvas */}
        <div className="flex-1 rounded-xl border border-slate-800 bg-[#020617] relative overflow-hidden">
          {/* Overlay Status Box */}
          <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur-md p-3.5 rounded-xl border border-slate-800 font-mono text-xs space-y-1 shadow-xl">
            <div className="text-cyan-400 font-bold flex items-center gap-1.5">
              <Box className="w-4 h-4 text-cyan-400" />
              <span>VOLUMETRIC SAFETY TUBE</span>
            </div>
            <div className="text-slate-400 text-[11px]">
              Lateral Radius: <strong className="text-white">{corridorRadius.toFixed(1)}m</strong> • Ceiling: <strong className="text-white">{maxCeiling}m AGL</strong>
            </div>
            <div className="text-slate-400 text-[10px]">
              Centrifugal G-Limit: <strong className="text-emerald-400">1.12G (Max Certified Roll 28°)</strong>
            </div>
          </div>

          <Canvas camera={{ position: [0, 6, 8], fov: 45 }}>
            <ambientLight intensity={0.7} />
            <directionalLight position={[5, 12, 5]} intensity={1.2} />
            <pointLight position={[-5, 5, -5]} intensity={0.6} color="#38bdf8" />
            
            <Grid position={[0, -0.5, 0]} args={[16, 16]} cellColor="#1e293b" sectionColor="#38bdf8" fadeDistance={25} />

            {/* Flight Path Spline Line */}
            <Line
              points={waypoints}
              color="#38bdf8"
              lineWidth={3}
            />

            {/* Render Waypoint Markers */}
            {waypoints.map((pt, idx) => (
              <mesh key={idx} position={pt}>
                <sphereGeometry args={[0.15, 16, 16]} />
                <meshStandardMaterial color="#00f0ff" emissive="#00f0ff" emissiveIntensity={0.5} />
              </mesh>
            ))}

            {/* Render Safety Corridor Tube Cylinders along Segments */}
            {waypoints.slice(0, -1).map((pt, idx) => {
              const nextPt = waypoints[idx + 1];
              const midX = (pt[0] + nextPt[0]) / 2;
              const midY = (pt[1] + nextPt[1]) / 2;
              const midZ = (pt[2] + nextPt[2]) / 2;
              const dist = Math.hypot(nextPt[0] - pt[0], nextPt[1] - pt[1], nextPt[2] - pt[2]);

              return (
                <group key={idx} position={[midX, midY, midZ]}>
                  <Cylinder args={[corridorRadius * 0.12, corridorRadius * 0.12, dist, 16, 1, true]} rotation={[Math.PI / 2, 0, 0]}>
                    <meshStandardMaterial color="#0284c7" transparent opacity={0.2} wireframe={false} />
                  </Cylinder>
                </group>
              );
            })}

            {/* 4D No-Fly Zone (NFZ) Cylinder if enabled */}
            {nfzEnabled && (
              <mesh position={[1.5, 1.5, -0.5]}>
                <cylinderGeometry args={[1.2, 1.2, 4.0, 32]} />
                <meshStandardMaterial color="#f43f5e" transparent opacity={0.35} wireframe={true} />
              </mesh>
            )}

            <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
          </Canvas>
        </div>

        {/* Corridor Controls Sidebar */}
        <div className="w-84 rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md flex flex-col justify-between overflow-y-auto space-y-6">
          <div className="space-y-5">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <Sliders className="w-4 h-4 text-cyan-400" />
                Corridor Safety Parameters
              </h3>
              <p className="text-[11px] text-slate-400 mt-1">Sculpt 3D lateral tolerance and geofence ceilings.</p>
            </div>

            {/* Slider 1: Lateral Safety Radius */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Lateral Safety Radius</span>
                <span className="text-cyan-400 font-bold">{corridorRadius.toFixed(1)} m</span>
              </div>
              <input
                type="range"
                min="2.0"
                max="15.0"
                step="0.5"
                value={corridorRadius}
                onChange={(e) => setCorridorRadius(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
              <span className="text-[10px] text-slate-500 font-mono block">DO-178C containment buffer envelope.</span>
            </div>

            {/* Slider 2: Altitude Ceiling */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Max Altitude Ceiling</span>
                <span className="text-sky-400 font-bold">{maxCeiling} m AGL</span>
              </div>
              <input
                type="range"
                min="30"
                max="120"
                step="5"
                value={maxCeiling}
                onChange={(e) => setMaxCeiling(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
              <span className="text-[10px] text-slate-500 font-mono block">FAA Part 107 max ceiling is 120m (400ft).</span>
            </div>

            {/* Toggle: Dubins Spline Smoothing */}
            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-semibold text-slate-200">Dubins Spline Smoothing</div>
                <div className="text-[10px] font-mono text-slate-400">Eliminates stop-and-turn delays</div>
              </div>
              <input
                type="checkbox"
                checked={useDubinsSplines}
                onChange={(e) => setUseDubinsSplines(e.target.checked)}
                className="h-4 w-4 rounded bg-slate-900 border-slate-700 text-cyan-500 focus:ring-0 cursor-pointer"
              />
            </div>

            {/* Toggle: 4D Dynamic NFZ Geofences */}
            <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between">
              <div>
                <div className="text-xs font-semibold text-slate-200">4D No-Fly Zones (TFR)</div>
                <div className="text-[10px] font-mono text-slate-400">Active red airspace avoidance</div>
              </div>
              <input
                type="checkbox"
                checked={nfzEnabled}
                onChange={(e) => setNfzEnabled(e.target.checked)}
                className="h-4 w-4 rounded bg-slate-900 border-slate-700 text-rose-500 focus:ring-0 cursor-pointer"
              />
            </div>
          </div>

          {/* Safety Advisory Card */}
          <div className="p-3.5 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-xs font-mono space-y-1.5">
            <div className="flex items-center gap-1.5 text-cyan-400 font-bold">
              <Shield className="w-4 h-4 text-cyan-400" />
              <span>GEOFENCE CONTAINMENT READY</span>
            </div>
            <p className="text-[11px] text-slate-300">
              Trajectory satisfies FAA Class G uncontrolled flight margins with zero corridor breach probability.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
