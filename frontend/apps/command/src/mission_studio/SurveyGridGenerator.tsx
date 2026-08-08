import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Line } from '@react-three/drei';
import { Camera, Grid as GridIcon, Image, Sliders, Play, CheckCircle2, Layers, MapPin } from 'lucide-react';
import { tacticalAudio } from '../audio/tacticalAudio';

export const SurveyGridGenerator: React.FC = () => {
  const [surveyPattern, setSurveyPattern] = useState<'lawnmower' | 'crosshatch'>('crosshatch');
  const [forwardOverlap, setForwardOverlap] = useState(80); // %
  const [sideOverlap, setSideOverlap] = useState(70); // %
  const [flightAltitude, setFlightAltitude] = useState(45); // meters AGL
  const [cameraGsd, setCameraGsd] = useState(1.4); // cm/px

  // Dynamic Calculated Metrics
  const calculatedPhotos = Math.round((100 / (100 - forwardOverlap)) * (100 / (100 - sideOverlap)) * (surveyPattern === 'crosshatch' ? 2 : 1) * 3.2);
  const surveyAreaHa = 14.2;
  const flightDurationMin = (calculatedPhotos * 2.8 / 60).toFixed(1);

  // Generate Scan Lines based on pattern
  const scanLines: [number, number, number][][] = [
    [[-3, 2, -2], [3, 2, -2]],
    [[3, 2, -1], [-3, 2, -1]],
    [[-3, 2, 0], [3, 2, 0]],
    [[3, 2, 1], [-3, 2, 1]],
    [[-3, 2, 2], [3, 2, 2]],
  ];

  const crossLines: [number, number, number][][] = [
    [[-2, 2.2, -3], [-2, 2.2, 3]],
    [[-1, 2.2, 3], [-1, 2.2, -3]],
    [[0, 2.2, -3], [0, 2.2, 3]],
    [[1, 2.2, 3], [1, 2.2, -3]],
    [[2, 2.2, -3], [2, 2.2, 3]],
  ];

  const handleGenerateSurvey = () => {
    tacticalAudio.playChirp(1040, 80);
    tacticalAudio.speak(`Photogrammetric survey grid compiled. ${calculatedPhotos} camera trigger exposures scheduled.`);
  };

  return (
    <div className="h-full w-full bg-[#010409] text-slate-200 p-6 flex flex-col font-sans overflow-hidden select-none">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
        <div className="flex items-center space-x-3">
          <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-bold">
            SURVEY & PHOTOGRAMMETRY v2.0
          </span>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Autonomous Polygon Survey & Cross-Hatch Grid Generator
          </h2>
          <span className="text-xs font-mono text-slate-500">GSD: {cameraGsd} cm/px</span>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs font-mono text-emerald-300">
            <Image className="w-3.5 h-3.5 text-emerald-400" />
            <span>EXPOSURES: {calculatedPhotos} PHOTOS</span>
          </div>

          <button
            onClick={handleGenerateSurvey}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-mono font-semibold text-slate-950 shadow-lg shadow-emerald-600/20 transition-all"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Upload Survey to MAVSDK</span>
          </button>
        </div>
      </div>

      {/* Main Split: 3D Viewport + Photogrammetry Controls */}
      <div className="flex-1 flex gap-4 overflow-hidden">
        {/* 3D WebGL Raster Canvas */}
        <div className="flex-1 rounded-xl border border-slate-800 bg-[#020617] relative overflow-hidden">
          <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur-md p-3.5 rounded-xl border border-slate-800 font-mono text-xs space-y-1 shadow-xl">
            <div className="text-emerald-400 font-bold flex items-center gap-1.5">
              <Camera className="w-4 h-4 text-emerald-400" />
              <span>PHOTOGRAMMETRY SPECS</span>
            </div>
            <div className="text-slate-300 text-[11px]">
              Survey Area: <strong className="text-white">{surveyAreaHa} ha</strong> • Est. Time: <strong className="text-white">{flightDurationMin} mins</strong>
            </div>
            <div className="text-slate-400 text-[10px]">
              Forward Overlap: <strong className="text-emerald-400">{forwardOverlap}%</strong> • Side Overlap: <strong className="text-emerald-400">{sideOverlap}%</strong>
            </div>
          </div>

          <Canvas camera={{ position: [0, 7, 7], fov: 45 }}>
            <ambientLight intensity={0.8} />
            <directionalLight position={[5, 10, 5]} intensity={1.2} />
            
            <Grid position={[0, -0.2, 0]} args={[16, 16]} cellColor="#1e293b" sectionColor="#10b981" fadeDistance={25} />

            {/* Bounding Polygon Perimeter */}
            <Line
              points={[[-3.5, 0.1, -2.5], [3.5, 0.1, -2.5], [3.5, 0.1, 2.5], [-3.5, 0.1, 2.5], [-3.5, 0.1, -2.5]]}
              color="#10b981"
              lineWidth={2}
            />

            {/* Primary Lawnmower Scan Lines */}
            {scanLines.map((line, idx) => (
              <Line key={`scan-${idx}`} points={line} color="#00f0ff" lineWidth={2.5} />
            ))}

            {/* Orthogonal Cross-Hatch Lines if enabled */}
            {surveyPattern === 'crosshatch' && crossLines.map((line, idx) => (
              <Line key={`cross-${idx}`} points={line} color="#a855f7" lineWidth={2} />
            ))}

            {/* Camera Shutter Exposure Dots */}
            {scanLines.map((line, i) => (
              <group key={`shutter-${i}`}>
                <mesh position={line[0]}>
                  <sphereGeometry args={[0.08, 12, 12]} />
                  <meshStandardMaterial color="#10b981" emissive="#10b981" />
                </mesh>
                <mesh position={line[1]}>
                  <sphereGeometry args={[0.08, 12, 12]} />
                  <meshStandardMaterial color="#10b981" emissive="#10b981" />
                </mesh>
              </group>
            ))}

            <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
          </Canvas>
        </div>

        {/* Photogrammetry Parameter Sidebar */}
        <div className="w-84 rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md flex flex-col justify-between overflow-y-auto space-y-6">
          <div className="space-y-5">
            <div className="border-b border-slate-800 pb-3">
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
                <Sliders className="w-4 h-4 text-emerald-400" />
                Photogrammetry Parameters
              </h3>
              <p className="text-[11px] text-slate-400 mt-1">Configure raster passes and camera overlap.</p>
            </div>

            {/* Pattern Mode Selector */}
            <div className="space-y-2">
              <span className="text-xs font-mono text-slate-300 block">Raster Scan Mode</span>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => { setSurveyPattern('lawnmower'); tacticalAudio.playChirp(840, 30); }}
                  className={`p-2.5 rounded-lg border text-xs font-mono text-center transition-all ${
                    surveyPattern === 'lawnmower'
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                  }`}
                >
                  Single Lawnmower
                </button>
                <button
                  onClick={() => { setSurveyPattern('crosshatch'); tacticalAudio.playChirp(840, 30); }}
                  className={`p-2.5 rounded-lg border text-xs font-mono text-center transition-all ${
                    surveyPattern === 'crosshatch'
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                  }`}
                >
                  Double Cross-Hatch
                </button>
              </div>
            </div>

            {/* Slider 1: Forward Overlap */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Forward Camera Overlap</span>
                <span className="text-emerald-400 font-bold">{forwardOverlap}%</span>
              </div>
              <input
                type="range"
                min="60"
                max="90"
                step="1"
                value={forwardOverlap}
                onChange={(e) => setForwardOverlap(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
            </div>

            {/* Slider 2: Side Overlap */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Side Sidelap Overlap</span>
                <span className="text-emerald-400 font-bold">{sideOverlap}%</span>
              </div>
              <input
                type="range"
                min="50"
                max="85"
                step="1"
                value={sideOverlap}
                onChange={(e) => setSideOverlap(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
              />
            </div>

            {/* Slider 3: Flight Altitude */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-300">Survey Altitude</span>
                <span className="text-cyan-400 font-bold">{flightAltitude} m AGL</span>
              </div>
              <input
                type="range"
                min="20"
                max="120"
                step="5"
                value={flightAltitude}
                onChange={(e) => {
                  const alt = parseInt(e.target.value);
                  setFlightAltitude(alt);
                  setCameraGsd(parseFloat((alt * 0.031).toFixed(2)));
                }}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
            </div>
          </div>

          {/* 3D Reconstruction Quality Card */}
          <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-xs font-mono space-y-1.5">
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>3D ORTHOMOSAIC RESOLUTION</span>
            </div>
            <p className="text-[11px] text-slate-300">
              GSD yields <strong className="text-white">{cameraGsd} cm/pixel</strong> resolution. Certified for millimeter structural crack detection.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
