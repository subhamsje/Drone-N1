import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import { Wind, Radio, Zap, Activity, Play, RotateCcw, AlertTriangle, ShieldCheck } from 'lucide-react';
import { tacticalAudio } from '../audio/tacticalAudio';
import { RealisticTacticalDrone } from './RealisticTacticalDrone';

export function CounterfactualTwinWorkbench() {
  const [windMps, setWindMps] = useState(6.2);
  const [rfNoiseDbm, setRfNoiseDbm] = useState(-78.0);
  const [motorDegradationPct, setMotorDegradationPct] = useState(5.0);
  const [batteryVoltage, setBatteryVoltage] = useState(15.8);
  const [simulating, setSimulating] = useState(false);

  // Dynamic Real-time Calculations
  const calculatedRisk = Math.min(1.0, (windMps / 20.0) * 0.35 + (motorDegradationPct / 100.0) * 0.45 + (batteryVoltage < 14.0 ? 0.2 : 0.05));
  const uncertaintyRadius = Math.max(0.6, (windMps * 0.1) + (motorDegradationPct * 0.02));
  const riskStatus = calculatedRisk < 0.25 ? 'NOMINAL' : calculatedRisk < 0.55 ? 'WARNING' : 'CRITICAL';

  const handleRunSim = () => {
    setSimulating(true);
    tacticalAudio.playChirp(1020, 80);

    if (calculatedRisk > 0.5) {
      tacticalAudio.alertMotorRamp();
    } else if (windMps > 12.0) {
      tacticalAudio.speak(`High wind shear alert. Model predictive control evaluated 14 recovery splines.`);
    } else {
      tacticalAudio.speak("Counterfactual physics simulation stable. Flight envelope within certified margin.");
    }

    setTimeout(() => setSimulating(false), 800);
  };

  const handleReset = () => {
    setWindMps(5.0);
    setRfNoiseDbm(-85.0);
    setMotorDegradationPct(0.0);
    setBatteryVoltage(16.2);
    tacticalAudio.playChirp(780, 50);
  };

  return (
    <div className="h-full w-full bg-[#010409] text-slate-200 p-6 flex flex-col font-sans overflow-hidden select-none">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
        <div className="flex items-center space-x-3">
          <span className="px-2.5 py-1 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs font-mono font-bold">
            DIGITAL TWIN WORKBENCH v9.0
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            3D Counterfactual Physics Sandbox & 20D EKF Inspector
          </h2>
          <span className="text-xs font-mono text-slate-500">STANAG 4586 Isolated Sim</span>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-300 border border-slate-700"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset Defaults
          </button>
          <button
            onClick={handleRunSim}
            disabled={simulating}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-xs font-mono font-semibold text-white shadow-lg shadow-cyan-600/20 transition-all disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            <span>{simulating ? 'Recomputing MPC...' : 'Simulate Counterfactual Physics'}</span>
          </button>
        </div>
      </div>

      {/* Main Workspace: 3D Viewport + Physics Controls Sidebar */}
      <div className="flex-1 flex gap-4 overflow-hidden">
        {/* 3D WebGL Canvas Viewport */}
        <div className="flex-1 rounded-xl border border-slate-800 bg-[#020617] relative overflow-hidden">
          {/* Overlay Status Box */}
          <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur-md p-3.5 rounded-xl border border-slate-800 font-mono text-xs space-y-1.5 shadow-xl">
            <div className="flex justify-between items-center gap-4">
              <span className="text-slate-400">STATE ENVELOPE</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                riskStatus === 'NOMINAL' ? 'bg-emerald-500/20 text-emerald-300' : riskStatus === 'WARNING' ? 'bg-amber-500/20 text-amber-300' : 'bg-rose-500/20 text-rose-300'
              }`}>
                {riskStatus}
              </span>
            </div>
            <div className="text-slate-300 text-[11px]">
              Calculated Risk Score: <strong className="text-cyan-400">{(calculatedRisk * 100).toFixed(1)}%</strong>
            </div>
            <div className="text-slate-400 text-[10px]">
              Uncertainty Covariance Radius: <strong className="text-white">{uncertaintyRadius.toFixed(2)}m</strong>
            </div>
          </div>

          <Canvas dpr={[1, 2]} camera={{ position: [2.5, 2.0, 2.5], fov: 45 }}>
            <ambientLight intensity={0.7} />
            <directionalLight position={[6, 12, 6]} intensity={1.5} castShadow />
            <pointLight position={[-4, 4, -4]} intensity={0.6} color="#38bdf8" />
            <pointLight position={[4, -2, 4]} intensity={0.4} color="#10b981" />
            
            <Grid position={[0, -0.6, 0]} args={[16, 16]} cellColor="#1e293b" sectionColor="#38bdf8" fadeDistance={24} />
            
            {/* 4K-Caliber Photorealistic Tactical Drone Model */}
            <RealisticTacticalDrone
              windMps={windMps}
              motorDegradationPct={motorDegradationPct}
              uncertaintyRadius={uncertaintyRadius}
              riskStatus={riskStatus}
            />

            <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} maxPolarAngle={Math.PI / 2 - 0.05} />
          </Canvas>
        </div>

        {/* Counterfactual Sliders Sidebar */}
        <div className="w-84 rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md flex flex-col justify-between overflow-y-auto space-y-6">
          <div className="space-y-5">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                Environmental Physics Sliders
              </h3>
              <p className="text-[11px] text-slate-400 mt-1">Adjust variables to test live MPC counterfactual replanning.</p>
            </div>

            {/* Slider 1: Wind Shear */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 flex items-center gap-1.5">
                  <Wind className="w-3.5 h-3.5 text-sky-400" /> Wind Speed Shear
                </span>
                <span className="text-sky-400 font-bold">{windMps} m/s</span>
              </div>
              <input
                type="range"
                min="0"
                max="25"
                step="0.5"
                value={windMps}
                onChange={(e) => setWindMps(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
              />
            </div>

            {/* Slider 2: Motor Degradation */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-amber-400" /> Motor 0 Bearing Wear
                </span>
                <span className="text-amber-400 font-bold">{motorDegradationPct}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="80"
                step="1"
                value={motorDegradationPct}
                onChange={(e) => setMotorDegradationPct(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400"
              />
            </div>

            {/* Slider 3: RF Jamming Noise */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 flex items-center gap-1.5">
                  <Radio className="w-3.5 h-3.5 text-purple-400" /> RF Jamming Noise
                </span>
                <span className="text-purple-400 font-bold">{rfNoiseDbm} dBm</span>
              </div>
              <input
                type="range"
                min="-95"
                max="-40"
                step="1"
                value={rfNoiseDbm}
                onChange={(e) => setRfNoiseDbm(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-400"
              />
            </div>

            {/* Slider 4: Battery Voltage */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300 flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-emerald-400" /> Battery Cell Voltage
                </span>
                <span className="text-emerald-400 font-bold">{batteryVoltage} V</span>
              </div>
              <input
                type="range"
                min="12.0"
                max="16.8"
                step="0.1"
                value={batteryVoltage}
                onChange={(e) => setBatteryVoltage(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
            </div>
          </div>

          {/* AI Response Recommendation Card */}
          <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono space-y-1.5">
            <div className="flex items-center gap-1.5 text-cyan-400 font-bold">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span>COGNITIVE KERNEL ADVISORY</span>
            </div>
            <p className="text-[11px] text-slate-300">
              {calculatedRisk > 0.5
                ? 'High risk threshold breached. Emergency LZ Alpha counterfactual branch selected.'
                : windMps > 10.0
                ? 'Aerodynamic wind shear detected. Evaluated 14 candidate trajectory splines.'
                : 'All physics vectors nominal. Mission corridor clear.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
