import { useMemo, useRef } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { cognitionEngine } from '../../config/runtime';
import { cognitionBreath, cognitionTime } from '../../runtime/cognitionClock';

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

const BUILDINGS: [number, number, number, number, number][] = [
  [-4, 0, -3, 0.8, 2.2],
  [-2, 0, -5, 1.2, 3.5],
  [3, 0, -4, 1, 2.8],
  [5, 0, 1, 0.6, 4],
  [-5, 0, 2, 1.1, 2],
  [2, 0, 4, 0.9, 3.2],
  [-1, 0, 6, 1.4, 2.5],
];

export function EnvironmentalWorld() {
  const clouds = useMemo(() => {
    return Array.from({ length: 10 }, (_, i) => ({
      x: (Math.random() - 0.5) * 14,
      y: 2.5 + Math.random() * 2,
      z: (Math.random() - 0.5) * 14,
      s: 0.4 + Math.random() * 0.6,
      phase: i * 0.7,
    }));
  }, []);
  const cloudGroup = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    const t = cognitionTime();
    const turb = cognitionEngine().renderState.twin.turbulence;
    if (cloudGroup.current) {
      cloudGroup.current.children.forEach((c, i) => {
        const data = clouds[i];
        if (!data) return;
        c.position.x = data.x + Math.sin(t * 0.15 + data.phase) * (0.5 + turb);
        c.position.z = data.z + Math.cos(t * 0.12 + data.phase) * (0.5 + turb);
      });
    }
  });

  const landing = cognitionEngine().renderState.twin.landingPoint;

  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.08, 0]} receiveShadow>
        <planeGeometry args={[40, 40]} />
        <meshStandardMaterial color="#0a1628" roughness={0.95} metalness={0.05} />
      </mesh>

      {BUILDINGS.map(([x, y, z, w, h], i) => (
        <mesh key={i} position={[x, h / 2 + y, z]} castShadow>
          <boxGeometry args={[w, h, w]} />
          <meshStandardMaterial color="#1e293b" roughness={0.85} metalness={0.1} />
        </mesh>
      ))}

      {/* Communication towers */}
      {[
        [-6, 0, -6],
        [6, 0, -5],
        [-7, 0, 4],
      ].map(([x, y, z], i) => (
        <group key={`tower-${i}`} position={[x, y, z]}>
          <mesh position={[0, 1.5, 0]}>
            <cylinderGeometry args={[0.04, 0.06, 3, 6]} />
            <meshStandardMaterial color="#475569" emissive="#1e3a5f" emissiveIntensity={0.2} />
          </mesh>
          <pointLight intensity={0.15} color="#38bdf8" distance={3} position={[0, 3, 0]} />
        </group>
      ))}

      {/* Primary landing zone */}
      <LandingZone position={landing} />

      {/* Mission continuity field */}
      <MissionContinuityZone />

      {/* Atmospheric clouds */}
      <group ref={cloudGroup}>
        {clouds.map((c, i) => (
          <mesh key={i} position={[c.x, c.y, c.z]}>
            <sphereGeometry args={[c.s, 8, 8]} />
            <meshBasicMaterial color="#94a3b8" transparent opacity={0.06} depthWrite={false} />
          </mesh>
        ))}
      </group>

      <CongestionHeatmap />
    </group>
  );
}

function LandingZone({ position }: { position: [number, number, number] }) {
  const group = useRef<THREE.Group>(null);
  const pulse = useRef(0);

  useFrame((_, delta) => {
    pulse.current = cognitionBreath(0.5);
    if (group.current) group.current.position.set(position[0], position[1], position[2]);
  });

  return (
    <group ref={group}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.5, 0.85, 32]} />
        <meshBasicMaterial color="#22d3a8" transparent opacity={0.25 + pulse.current * 0.15} />
      </mesh>
      <mesh position={[0, 0.02, 0]}>
        <boxGeometry args={[1.2, 0.04, 1.2]} />
        <meshStandardMaterial color="#334155" emissive="#14532d" emissiveIntensity={0.15} />
      </mesh>
    </group>
  );
}

function MissionContinuityZone() {
  const mesh = useRef<THREE.Mesh>(null);
  const scale = useRef(1);

  useFrame((_, delta) => {
    const surv = cognitionEngine().renderState.twin.survivability;
    scale.current = lerp(scale.current, 2.5 + (1 - surv) * 1.5, delta * 2);
    if (mesh.current) {
      mesh.current.scale.set(scale.current, 1, scale.current);
      const mat = mesh.current.material as THREE.MeshBasicMaterial;
      mat.opacity = 0.02 + surv * 0.04 + cognitionBreath() * 0.02;
    }
  });

  return (
    <mesh ref={mesh} position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <circleGeometry args={[1, 48]} />
      <meshBasicMaterial color="#22d3a8" transparent opacity={0.04} depthWrite={false} />
    </mesh>
  );
}

function CongestionHeatmap() {
  const mesh = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    const c = cognitionEngine().renderState.globe.congestion;
    if (mesh.current) {
      const mat = mesh.current.material as THREE.MeshBasicMaterial;
      mat.opacity = lerp(mat.opacity, 0.03 + c * 0.12, delta * 3);
      mat.color.setHSL(0.75 - c * 0.2, 0.7, 0.35);
    }
  });
  return (
    <mesh ref={mesh} rotation={[-Math.PI / 2, 0, 0]} position={[3, 0.03, 3]}>
      <planeGeometry args={[5, 5]} />
      <meshBasicMaterial transparent opacity={0.05} color="#8b5cf6" />
    </mesh>
  );
}
