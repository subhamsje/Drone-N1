import React, { useState } from 'react';
import { Video, Crosshair, Lock, Activity } from 'lucide-react';
import { Badge } from '../../components/primitives/Badge';
import { Button } from '../../components/primitives/Button';

export const FpvFeed: React.FC = () => {
  const [locked, setLocked] = useState(true);

  return (
    <div className="h-full w-full bg-black relative overflow-hidden flex flex-col font-mono text-xs select-none">
      {/* Top Video Telemetry Stream Header */}
      <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-auto">
        <div className="flex items-center gap-2 bg-slate-950/80 backdrop-blur-md px-3 py-1 rounded-lg border border-slate-800">
          <span className="h-2 w-2 rounded-full bg-rose-500 animate-pulse" />
          <span className="font-bold text-slate-200 text-[11px]">H.264 / NVENC 1080p@60FPS</span>
          <span className="text-[10px] text-slate-500">Bitrate: 4.8 Mbps</span>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="success" pulse>
            VIO OPTICAL FLOW: 142 TRACKED
          </Badge>
          <Button
            size="sm"
            variant={locked ? 'primary' : 'secondary'}
            icon={<Lock className="w-3 h-3" />}
            onClick={() => setLocked(!locked)}
          >
            {locked ? 'AI TARGET LOCKED' : 'FREE TRACK'}
          </Button>
        </div>
      </div>

      {/* Simulated Video Canvas with Bounding Box & Target Lock */}
      <div className="flex-1 relative flex items-center justify-center">
        {/* Optical Crosshair */}
        <div className="w-72 h-72 rounded-full border border-sky-500/20 flex items-center justify-center pointer-events-none">
          <div className="w-48 h-48 rounded-full border border-sky-500/30 flex items-center justify-center">
            <Crosshair className="w-8 h-8 text-sky-400/80 animate-pulse" />
          </div>
        </div>

        {/* AI Bounding Box Overlay */}
        {locked && (
          <div className="absolute top-1/3 left-1/3 w-40 h-28 border-2 border-emerald-400/90 rounded-lg p-1 flex flex-col justify-between text-[9px] text-emerald-400 font-mono shadow-lg shadow-emerald-500/10">
            <div className="flex justify-between font-bold bg-emerald-950/60 px-1 rounded">
              <span>TARGET #42</span>
              <span>96.4%</span>
            </div>
            <div className="text-right text-[8px] text-slate-400">DIST: 184.2m</div>
          </div>
        )}
      </div>

      {/* Bottom Telemetry HUD Bar */}
      <div className="h-10 bg-slate-950/90 border-t border-slate-800/80 px-4 flex items-center justify-between text-[10px] text-slate-400 z-20">
        <span>GIMBAL: -30.0° PITCH • 045° YAW</span>
        <span className="text-emerald-400 font-bold">GLASS-TO-GLASS LATENCY: 18.2ms</span>
        <span>LAT: 30.2672° N • LON: -97.7431° W</span>
      </div>
    </div>
  );
};
