import { memo, useCallback } from 'react';
import { Canvas } from '@react-three/fiber';
import type { WebGLRenderer } from 'three';
import { CognitiveTwinScene } from './CognitiveTwinScene';
import { SpatialHUD } from './SpatialHUD';
import { cognitionEngine } from '../config/runtime';
import { attachGpuLifecycle } from '../runtime/gpuLifecycle';
import { isRenderDegraded } from '../runtime/renderScheduler';
import { useCognitionStore } from '../stores/cognitionStore';

export const CognitiveTwin = memo(function CognitiveTwin() {
  const uavId = useCognitionStore((s) => s.envelope?.uav_id);
  const os = useCognitionStore((s) => s.envelope?.os_version);
  const degraded = useCognitionStore((s) => s.degraded) || isRenderDegraded();
  const onCreated = useCallback(({ gl }: { gl: WebGLRenderer }) => {
    attachGpuLifecycle(gl.domElement, () => useCognitionStore.getState().setDegraded(true));
  }, []);

  return (
    <div className="relative h-full w-full bg-[#010409]">
      <div className="ops-radar-sweep absolute inset-0 opacity-30" />
      <SpatialHUD />
      <Canvas
        camera={{ position: [4, 3, 4], fov: 50 }}
        dpr={degraded ? [1, 1] : [1, 1.5]}
        frameloop="always"
        gl={{ powerPreference: 'high-performance', antialias: !degraded }}
        onCreated={onCreated}
      >
        <CognitiveTwinScene />
      </Canvas>
      <div className="pointer-events-none absolute bottom-3 left-3 font-mono text-[10px] text-slate-500">
        COGNITIVE TWIN · {cognitionEngine().renderState.twin.uavId || uavId || '—'} · OS{' '}
        {cognitionEngine().renderState.twin.osVersion || os || '—'}
        {degraded ? ' · DEGRADED' : ''}
      </div>
    </div>
  );
});
