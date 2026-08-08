import React, { useState } from 'react';
import { Volume2, VolumeX, Radio } from 'lucide-react';
import { tacticalAudio } from './tacticalAudio';

export const AudioVisualizerWidget: React.FC = () => {
  const [muted, setMuted] = useState(false);

  const toggleMute = () => {
    const next = !muted;
    setMuted(next);
    tacticalAudio.playChirp(next ? 440 : 880, 50);
    if (!next) {
      tacticalAudio.speak("Tactical voice synthesizer active.");
    }
  };

  return (
    <div className="hidden lg:flex items-center space-x-2 bg-slate-900/90 border border-slate-800 px-3 py-1 rounded-xl text-xs font-mono text-slate-300">
      <button
        onClick={toggleMute}
        className="text-cyan-400 hover:text-cyan-300 transition-colors"
      >
        {muted ? <VolumeX className="w-3.5 h-3.5 text-rose-400" /> : <Volume2 className="w-3.5 h-3.5 text-cyan-400" />}
      </button>

      {/* Simulated Audio Frequency Waveform */}
      <div className="flex items-center gap-0.5 h-3">
        {[4, 10, 6, 12, 8, 14, 5, 11].map((h, i) => (
          <span
            key={i}
            style={{ height: muted ? 2 : `${h}px` }}
            className={`w-0.5 rounded-full transition-all ${
              muted ? 'bg-slate-700' : 'bg-cyan-400 animate-pulse'
            }`}
          />
        ))}
      </div>

      <span className="text-[10px] text-slate-500 font-mono">TAC-VOICE</span>
    </div>
  );
};
