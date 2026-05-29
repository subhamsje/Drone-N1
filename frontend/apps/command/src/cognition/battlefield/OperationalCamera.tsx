import { useRef } from 'react';
import * as THREE from 'three';
import { useFrame, useThree } from '@react-three/fiber';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { cognitionEngine } from '../../config/runtime';
import { cognitionTime } from '../../runtime/cognitionClock';

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

/**
 * Operationally intelligent camera — threat focus, recovery zoom, futures pull-back.
 * Works with OrbitControls (damped); never replaces operator pan/zoom entirely.
 */
export function OperationalCamera() {
  const { camera } = useThree();
  const controls = useThree((s) => s.controls) as OrbitControlsImpl | undefined;
  const dist = useRef(5.5);
  const targetY = useRef(0.12);

  useFrame((_, delta) => {
    const t = cognitionEngine().renderState.twin;
    const action = (t.action ?? '').toUpperCase();
    let wantDist = 5;
    let wantTargetY = 0.12;

    if (t.crashRisk > 0.35) {
      wantDist = 8 + t.crashRisk * 3;
      wantTargetY = 0.3;
    } else if (t.threatLevel > 0.3) {
      wantDist = 3.8 + (1 - t.threatLevel) * 2;
      wantTargetY = 0.25;
    } else if (action.includes('RECOVER') || action.includes('LAND') || action.includes('RTL')) {
      wantDist = 2.8;
      wantTargetY = 0.08;
    } else if (t.uncertainty > 0.4) {
      wantDist = 6.5;
      wantTargetY = 0.2;
    }

    const drift = Math.sin(cognitionTime() * 0.2) * 0.04;
    dist.current = lerp(dist.current, wantDist, Math.min(1, delta * 1.5));
    targetY.current = lerp(targetY.current, wantTargetY + drift, delta * 2);

    if (controls) {
      controls.target.lerp(new THREE.Vector3(0, targetY.current, 0), delta * 3);
      controls.update();
      const dir = camera.position.clone().sub(controls.target).normalize();
      const goal = controls.target.clone().add(dir.multiplyScalar(dist.current));
      camera.position.lerp(goal, Math.min(1, delta * 2.5));
    } else {
      camera.position.lerp(new THREE.Vector3(dist.current * 0.7, dist.current * 0.55, dist.current * 0.7), delta * 2);
      camera.lookAt(0, targetY.current, 0);
    }
  });

  return null;
}
