import React, { useState, useEffect } from 'react';
import { Play, Pause, FastForward, RotateCcw, Bookmark, AlertCircle } from 'lucide-react';
import { tacticalAudio } from '../audio/tacticalAudio';

export const MissionReplayScrubber: React.FC = () => {
  const [playing, setPlaying] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(42);
  const [totalFrames] = useState(120);
  const [speed, setSpeed] = useState<'1x' | '2x' | '5x'>('1x');

  useEffect(() => {
    let timer: any = null;
    if (playing) {
      const intervalMs = speed === '1x' ? 100 : speed === '2x' ? 50 : 20;
      timer = setInterval(() => {
        setCurrentFrame((f) => (f >= totalFrames ? 0 : f + 1));
      }, intervalMs);
    }
    return () => clearInterval(timer);
  }, [playing, speed, totalFrames]);

  const togglePlay = () => {
    const next = !playing;
    setPlaying(next);
    tacticalAudio.playChirp(next ? 880 : 660, 40);
  };

  const jumpToIncident = () => {
    setCurrentFrame(88); // Incident #INC-882 marker
    tacticalAudio.playChirp(1100, 80);
    tacticalAudio.speak("Scrubbed to incident 882: GPS multipath spike.");
  };

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 w-full max-w-2xl bg-slate-950/85 border border-slate-800/90 rounded-2xl p-3.5 backdrop-blur-xl shadow-2xl text-slate-200 font-mono text-xs select-none">
      <div className="flex items-center justify-between gap-4">
        {/* Play / Pause / Reset Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={togglePlay}
            className="p-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-600/20 transition-all"
          >
            {playing ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
          </button>
          <button
            onClick={() => setCurrentFrame(0)}
            className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 transition-all"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Timeline Slider with Incident Marker */}
        <div className="relative flex-1 flex flex-col justify-center">
          <div className="flex justify-between text-[10px] text-slate-400 mb-1">
            <span>T+{(currentFrame * 0.1).toFixed(1)}s</span>
            <button onClick={jumpToIncident} className="text-amber-400 hover:underline flex items-center gap-1">
              <AlertCircle className="w-3 h-3 text-amber-400" /> INC-882 (T+8.8s)
            </button>
            <span>T+{(totalFrames * 0.1).toFixed(1)}s</span>
          </div>

          <input
            type="range"
            min="0"
            max={totalFrames}
            value={currentFrame}
            onChange={(e) => setCurrentFrame(parseInt(e.target.value))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
          />
        </div>

        {/* Speed Selector */}
        <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-xl border border-slate-800 text-[11px]">
          {(['1x', '2x', '5x'] as const).map((s) => (
            <button
              key={s}
              onClick={() => { setSpeed(s); tacticalAudio.playChirp(750, 30); }}
              className={`px-2 py-0.5 rounded-lg font-bold transition-all ${
                speed === s ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
