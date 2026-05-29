import { useRef, useMemo, type MutableRefObject } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';
import { survivabilityColor } from '@altaria/cognition-sdk';
import { cognitionEngine } from '../../config/runtime';
import {
  advanceCognitionClock,
  cognitionBreath,
  cognitionPulse,
  cognitionTime,
} from '../../runtime/cognitionClock';

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

/** Breathing survivability halo — cognition under uncertainty */
export function SurvivabilityHalo() {
  const mesh = useRef<THREE.Mesh>(null);
  const scale = useRef(1.2);
  const mat = useRef<THREE.MeshBasicMaterial>(null);

  useFrame((_, delta) => {
    advanceCognitionClock(delta);
    const t = cognitionEngine().renderState.twin;
    const breath = cognitionBreath(0.4);
    const target = 1.1 + (1 - t.survivability) * 0.5 + breath * 0.08;
    scale.current = lerp(scale.current, target, Math.min(1, delta * 3));
    if (mesh.current) mesh.current.scale.setScalar(scale.current);
    if (mat.current) {
      const c = survivabilityColor(t.survivability);
      mat.current.color.set(c);
      mat.current.opacity = 0.08 + cognitionPulse(0.9) * 0.06;
    }
  });

  return (
    <mesh ref={mesh} rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}>
      <ringGeometry args={[1.4, 2.2, 64]} />
      <meshBasicMaterial ref={mat} transparent depthWrite={false} color="#22d3a8" />
    </mesh>
  );
}

/** Uncertainty field — subtle volumetric points */
export function UncertaintyBreathingField() {
  const pts = useMemo(() => {
    const a: THREE.Vector3[] = [];
    for (let i = 0; i < 24; i++) {
      a.push(new THREE.Vector3((Math.random() - 0.5) * 5, Math.random() * 2, (Math.random() - 0.5) * 5));
    }
    return a;
  }, []);
  const group = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    const unc = cognitionEngine().renderState.twin.uncertainty;
    const t = cognitionTime();
    if (!group.current) return;
    group.current.visible = unc > 0.12;
    group.current.children.forEach((child, i) => {
      const m = child as THREE.Mesh;
      const base = pts[i];
      m.position.set(
        base.x + Math.sin(t * 0.7 + i) * unc * 0.3,
        base.y + Math.cos(t * 0.5 + i * 0.3) * unc * 0.2,
        base.z + Math.cos(t * 0.6 + i) * unc * 0.3,
      );
      const mat = m.material as THREE.MeshBasicMaterial;
      mat.opacity = 0.06 + unc * 0.2 + cognitionBreath() * 0.04;
    });
  });

  return (
    <group ref={group}>
      {pts.map((p, i) => (
        <mesh key={i} position={p}>
          <sphereGeometry args={[0.04, 6, 6]} />
          <meshBasicMaterial color="#38bdf8" transparent opacity={0.12} />
        </mesh>
      ))}
    </group>
  );
}

/** @deprecated Branches rendered in WorldFuturesEngine */
export function MissionBranchFutures() {
  return null;
}

/** Threat propagation volume */
export function ThreatVolume() {
  const mesh = useRef<THREE.Mesh>(null);
  const level = useRef(0);

  useFrame((_, delta) => {
    const target = cognitionEngine().renderState.twin.threatLevel;
    level.current = lerp(level.current, target, Math.min(1, delta * 4));
    if (mesh.current) {
      mesh.current.visible = level.current > 0.08;
      mesh.current.scale.setScalar(2.5 + level.current * 2);
      const mat = mesh.current.material as THREE.MeshBasicMaterial;
      mat.opacity = level.current * 0.12;
    }
  });

  return (
    <mesh ref={mesh} position={[2.2, 0.8, -1.5]}>
      <sphereGeometry args={[1, 16, 16]} />
      <meshBasicMaterial color="#f97316" transparent opacity={0.1} depthWrite={false} />
    </mesh>
  );
}

/** RF-denied zone */
export function RfDeniedVolume() {
  const mesh = useRef<THREE.Mesh>(null);
  const level = useRef(0);

  useFrame((_, delta) => {
    const target = cognitionEngine().renderState.twin.rfDenied;
    level.current = lerp(level.current, target, Math.min(1, delta * 4));
    if (mesh.current) {
      mesh.current.visible = level.current > 0.05;
      const mat = mesh.current.material as THREE.MeshBasicMaterial;
      mat.opacity = 0.04 + level.current * 0.1;
    }
  });

  return (
    <mesh ref={mesh} position={[-2, 0.1, 1.8]} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[4, 4, 8, 8]} />
      <meshBasicMaterial color="#eab308" wireframe transparent opacity={0.08} />
    </mesh>
  );
}

/** Motor stress heat — embodied self-awareness */
export function HardwareStressOverlay() {
  const motors = useRef([0.1, 0.1, 0.1, 0.1]);
  const positions: [number, number, number][] = [
    [0.5, -0.05, 0.5],
    [-0.5, -0.05, 0.5],
    [0.5, -0.05, -0.5],
    [-0.5, -0.05, -0.5],
  ];

  useFrame((_, delta) => {
    const stress = cognitionEngine().renderState.twin.motorStress;
    for (let i = 0; i < 4; i++) {
      motors.current[i] = lerp(motors.current[i], stress[i], Math.min(1, delta * 5));
    }
  });

  return (
    <>
      {positions.map((p, i) => (
        <MotorStressRing key={i} position={p} index={i} stressRef={motors} />
      ))}
    </>
  );
}

function MotorStressRing({
  position,
  index,
  stressRef,
}: {
  position: [number, number, number];
  index: number;
  stressRef: MutableRefObject<number[]>;
}) {
  const mesh = useRef<THREE.Mesh>(null);
  useFrame(() => {
    const s = stressRef.current[index];
    if (mesh.current) {
      mesh.current.visible = s > 0.12;
      const mat = mesh.current.material as THREE.MeshBasicMaterial;
      mat.color.setHSL(0.08 - s * 0.08, 0.9, 0.45);
      mat.opacity = 0.15 + s * 0.5;
    }
  });
  return (
    <mesh ref={mesh} position={position} rotation={[-Math.PI / 2, 0, 0]}>
      <ringGeometry args={[0.12, 0.22, 16]} />
      <meshBasicMaterial transparent color="#f59e0b" />
    </mesh>
  );
}

/** Swarm coupling arcs — collective cognition */
export function SwarmCouplingArcs() {
  const coupling = useRef(0);
  const group = useRef<THREE.Group>(null);
  const nodes = useMemo(
    () =>
      [0, 1, 2, 3].map((i) => {
        const a = (i / 4) * Math.PI * 2;
        return [Math.cos(a) * 3.2, 0.4, Math.sin(a) * 3.2] as [number, number, number];
      }),
    [],
  );

  useFrame((_, delta) => {
    coupling.current = lerp(
      coupling.current,
      cognitionEngine().renderState.twin.swarmCoupling,
      Math.min(1, delta * 3),
    );
    if (group.current) group.current.visible = coupling.current > 0.02;
  });

  return (
    <group ref={group}>
      {nodes.map((from, i) => {
        const to = nodes[(i + 1) % nodes.length];
        const wave = Math.sin(cognitionTime() * 2 + i) * 0.15;
        const mid: [number, number, number] = [
          (from[0] + to[0]) / 2,
          0.6 + wave + coupling.current * 0.5,
          (from[2] + to[2]) / 2,
        ];
        return (
          <Line
            key={i}
            points={[from, mid, to]}
            color="#22d3ee"
            lineWidth={1}
            transparent
            opacity={0.15 + coupling.current * 0.35}
            dashed
          />
        );
      })}
      {nodes.map((p, i) => (
        <mesh key={`n-${i}`} position={p}>
          <sphereGeometry args={[0.06, 8, 8]} />
          <meshBasicMaterial color="#22d3ee" transparent opacity={0.25 + coupling.current * 0.3} />
        </mesh>
      ))}
    </group>
  );
}

/** Animated turbulence — environmental futures */
export function AnimatedTurbulence() {
  const positions = useMemo(() => {
    const arr: THREE.Vector3[] = [];
    for (let i = 0; i < 36; i++) {
      arr.push(new THREE.Vector3((Math.random() - 0.5) * 9, Math.random() * 3.5, (Math.random() - 0.5) * 9));
    }
    return arr;
  }, []);
  const group = useRef<THREE.Group>(null);
  const intensity = useRef(0);

  useFrame((_, delta) => {
    const target = cognitionEngine().renderState.twin.turbulence;
    intensity.current = lerp(intensity.current, target, Math.min(1, delta * 4));
    const t = cognitionTime();
    if (!group.current) return;
    group.current.visible = intensity.current >= 0.15;
    group.current.children.forEach((child, i) => {
      const m = child as THREE.Mesh;
      const base = positions[i];
      m.position.set(
        base.x + Math.sin(t + i * 0.4) * intensity.current,
        base.y + Math.sin(t * 1.3 + i) * 0.3,
        base.z + Math.cos(t * 0.9 + i) * intensity.current,
      );
    });
  });

  return (
    <group ref={group}>
      {positions.map((p, i) => (
        <mesh key={i} position={p}>
          <sphereGeometry args={[0.05, 5, 5]} />
          <meshBasicMaterial color="#f59e0b" transparent opacity={0.18} />
        </mesh>
      ))}
    </group>
  );
}
