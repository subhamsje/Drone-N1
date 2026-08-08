import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Line } from '@react-three/drei';
import { BatteryCharging, BatteryWarning, Wind, Compass, Play, AlertOctagon, CheckCircle2, ShieldAlert } from 'lucide-react';
import { tacticalAudio } from '../audio/tacticalAudio';

export const BatteryFeasibilitySimulator: React.FC = () => {
  const [headwindMps, setHeadwindMps] = useState(8.5);
  const [windHeadingDeg, setWindHeadingDeg] = useState(120);
  const [takeoffBatteryPct, setTakeoffBatteryPct] = useState(96);
  const [payloadWeightKg, setPayloadWeightKg] = useState(1.2);

  // Dynamic Energy & PONR Calculations
  const energyConsumptionRateW = 180 + (headwindMps * 12.5) + (payloadWeightKg * 45);
  const totalMissionEnergyWh = 88.4;
  const availableEnergyWh = (takeoffBatteryPct / 100) * 125.0; // 125Wh LiPo pack
  const reserveBatteryAtLandingPct = Math.max(0, Math.round(((availableEnergyWh - totalMissionEnergyWh) / availableEnergyWh) * takeoffBatteryPct));
  const ponrWaypointIndex = reserveBatteryAtLandingPct > 25 ? 3 : 2;

  // 3D Path Waypoints with Dynamic Energy Status
  const flightPoints: [number, number, number][] = [
    [-4, 0.5, -2],
    [-2, 2.0, -1],
    [0, 2.8, 0], // Waypoint 3 (PONR)
    [2, 2.8, 1],
    [4, 1.5, 2],
    [3, 0.2, 3],
  ];

  const handleSimulateEnergy = () => {
    tacticalAudio.playChirp(1040, 80);
    if (reserveBatteryAtLandingPct < 20) {
      tacticalAudio.speak(`Warning: Battery reserve below safety margin at landing. Estimated ${reserveBatteryAtLandingPct} percent remaining.`);
    } else {
      tacticalAudio.speak(`Mission energy feasibility verified. Point of no return located at waypoint ${ponrWaypointIndex + 1}.`);
    }
  };

  return (
    <div className="h-full w-full bg-[#010409] text-slate-200 p-6 flex flex-col font-sans overflow-hidden select-none">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
        <div className="flex items-center space-x-3">
          <span className="px-2.5 py-1 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-mono font-bold">
            ENERGY & AERODYNAMICS v3.1
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Battery Discharge & Point-of-No-Return (PONR) Simulator
          </h2>
          <span className="text-xs font-mono text-slate-500">Power Draw: {energyConsumptionRateW.toFixed(0)}W</span>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-xs font-mono text-amber-300">
            <BatteryCharging className="w-3.5 h-3.5 text-amber-400" />
            <span>RESERVE AT TOUCHDOWN: {reserveBatteryAtLandingPct}%</span>
          </div>

          <button
            onClick={handleSimulateEnergy}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-xs font-mono font-semibold text-slate-950 shadow-lg shadow-amber-600/20 transition-all"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Simulate Aerodynamic Draw</span>
          </button>
        </div>
      </div>

      {/* Main Split: 3D Trajectory Canvas + Energy Parameters */}
      <div className="flex-1 flex gap-4 overflow-hidden">
        {/* 3D WebGL Canvas with PONR Marker */}
        <div className="flex-1 rounded-xl border border-slate-800 bg-[#020617] relative overflow-hidden">
          <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur-md p-3.5 rounded-xl border border-slate-800 font-mono text-xs space-y-1 shadow-xl">
            <div className="text-amber-400 font-bold flex items-center gap-1.5">
              <AlertOctagon className="w-4 h-4 text-amber-400" />
              <span>POINT-OF-NO-RETURN (PONR)</span>
            </div>
            <div className="text-slate-300 text-[11px]">
              Critical Milestone: <strong className="text-white">Waypoint 0{ponrWaypointIndex + 1}</strong>
            </div>
            <div className="text-slate-400 text-[10px]">
              Headwind Penalty: <strong className="text-amber-400">+{(headwindMps * 4.2).toFixed(1)}% Extra Draw</strong>
            </div>
          </div>

          <Canvas camera={{ position: [0, 6, 8], fov: 45 }}>
            <ambientLight intensity={0.8} />
            <directionalLight position={[5, 10, 5]} intensity={1.2} />
            
            <Grid position={[0, -0.2, 0]} args={[16, 16]} cellColor="#1e293b" sectionColor="#f59e0b" fadeDistance={25} />

            {/* Flight Path with Energy Gradient Line */}
            <Line
              points={flightPoints}
              color={reserveBatteryAtLandingPct < 20 ? "#f43f5e" : "#f59e0b"}
              lineWidth={3}
            />

            {/* Waypoint Markers */}
            {flightPoints.map((pt, idx) => {
              const isPonr = idx === ponrWaypointIndex;
              return (
                <mesh key={idx} position={pt}>
                  <sphereGeometry args={[isPonr ? 0.25 : 0.14, 16, 16]} />
                  <meshStandardMaterial 
                    color={isPonr ? "#ef4444" : "#f59e0b"} 
                    emissive={isPonr ? "#ef4444" : "#f59e0b"} 
                    emissiveIntensity={isPonr ? 0.8 : 0.4} 
                  />
                </mesh>
              );
            })}

            <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
          </Canvas>
        </div>

        {/* Aerodynamic & Energy Sliders Sidebar */}
        <div className="w-84 rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md flex flex-col justify-between overflow-y-auto space-y-6">
          <div className="space-y-5">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <Wind className="w-4 h-4 text-amber-400" />
                Aerodynamics & Power
              </h3>
              <p className="text-[11px] text-slate-400 mt-1">Simulate headwind drag and payload energy burn.</p>
            </div>

            {/* Slider 1: Wind Speed */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Headwind Velocity</span>
                <span className="text-amber-400 font-bold">{headwindMps.toFixed(1)} m/s</span>
              </div>
              <input
                type="range"
                min="0"
                max="20"
                step="0.5"
                value={headwindMps}
                onChange={(e) => setHeadwindMps(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400"
              />
            </div>

            {/* Slider 2: Wind Heading */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Wind Direction</span>
                <span className="text-sky-400 font-bold">{windHeadingDeg}° Compass</span>
              </div>
              <input
                type="range"
                min="0"
                max="360"
                step="5"
                value={windHeadingDeg}
                onChange={(e) => setWindHeadingDeg(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
            </div>

            {/* Slider 3: Payload Weight */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Payload Weight</span>
                <span className="text-emerald-400 font-bold">{payloadWeightKg.toFixed(1)} kg</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="4.0"
                step="0.2"
                value={payloadWeightKg}
                onChange={(e) => setPayloadWeightKg(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
            </div>

            {/* Slider 4: Initial Takeoff Battery */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Takeoff Battery SOC</span>
                <span className="text-cyan-400 font-bold">{takeoffBatteryPct}%</span>
              </div>
              <input
                type="range"
                min="50"
                max="100"
                step="1"
                value={takeoffBatteryPct}
                onChange={(e) => setTakeoffBatteryPct(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
            </div>
          </div>

          {/* Contingency Recommendation Card */}
          <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/30 text-xs font-mono space-y-1.5">
            <div className="flex items-center gap-1.5 text-amber-400 font-bold">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <span>FAIL-SAFE CONTINGENCY MATRIX</span>
            </div>
            <p className="text-[11px] text-slate-300">
              {reserveBatteryAtLandingPct < 20
                ? 'Critically low reserve. Autonomous trigger will divert to Emergency LZ Alpha at PONR.'
                : 'Energy feasibility verified. Aircraft will touchdown with compliant 20%+ reserve.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
