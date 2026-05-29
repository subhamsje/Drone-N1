import { useRef } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { cognitionEngine } from '../../config/runtime';
import { cognitionBreath, cognitionPulse } from '../../runtime/cognitionClock';

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

/** Probabilistic cognition fog — sensor/world uncertainty volume */
export function UncertaintyFog() {
  const outer = useRef<THREE.Mesh>(null);
  const inner = useRef<THREE.Mesh>(null);
  const scale = useRef(1);

  useFrame((_, delta) => {
    const t = cognitionEngine().renderState.twin;
    const unc = Math.min(1, t.uncertainty + t.gpsUncertainty * 0.4 + t.visionUncertainty * 0.3);
    const breath = cognitionBreath(0.25);
    const target = 3.5 + unc * 4 + breath * 0.3;
    scale.current = lerp(scale.current, target, delta * 2);

    if (outer.current) {
      outer.current.scale.setScalar(scale.current);
      const mat = outer.current.material as THREE.MeshBasicMaterial;
      mat.opacity = lerp(mat.opacity, 0.02 + unc * 0.07 + cognitionPulse(0.5) * 0.02, delta * 4);
    }
    if (inner.current) {
      inner.current.scale.setScalar(scale.current * 0.65);
      const mat = inner.current.material as THREE.MeshBasicMaterial;
      mat.opacity = lerp(mat.opacity, 0.04 + unc * 0.1, delta * 4);
    }
  });

  return (
    <group position={[0, 1, 0]}>
      <mesh ref={outer}>
        <icosahedronGeometry args={[1, 2]} />
        <meshBasicMaterial color="#38bdf8" transparent depthWrite={false} wireframe />
      </mesh>
      <mesh ref={inner}>
        <icosahedronGeometry args={[1, 1]} />
        <meshBasicMaterial color="#6366f1" transparent depthWrite={false} opacity={0.05} />
      </mesh>
    </group>
  );
}
