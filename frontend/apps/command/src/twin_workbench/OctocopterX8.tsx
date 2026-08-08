import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export interface OctoProps {
  windMps: number;
  motorDegradationPct: number;
  uncertaintyRadius: number;
  riskStatus: 'NOMINAL' | 'WARNING' | 'CRITICAL';
}

export const OctocopterX8: React.FC<OctoProps> = ({
  windMps,
  motorDegradationPct,
  uncertaintyRadius,
  riskStatus,
}) => {
  const octoRef = useRef<THREE.Group>(null);
  const topPropsRef = useRef<(THREE.Group | null)[]>([]);
  const botPropsRef = useRef<(THREE.Group | null)[]>([]);

  useFrame((state, delta) => {
    const baseSpeed = 50;
    topPropsRef.current.forEach((p) => {
      if (p) p.rotation.y += baseSpeed * delta;
    });
    botPropsRef.current.forEach((p) => {
      if (p) p.rotation.y -= (baseSpeed * (1 - motorDegradationPct / 140)) * delta;
    });

    if (octoRef.current) {
      const t = state.clock.getElapsedTime();
      const turbulence = (windMps / 25) * 0.04;
      octoRef.current.position.y = 0.5 + Math.sin(t * 1.6) * (0.02 + turbulence);
      octoRef.current.rotation.z = Math.sin(t * 1.2) * (0.01 + turbulence);
    }
  });

  const carbonMaterial = new THREE.MeshStandardMaterial({
    color: '#080c14',
    roughness: 0.2,
    metalness: 0.9,
  });

  const rotorMaterial = new THREE.MeshStandardMaterial({
    color: '#38bdf8',
    roughness: 0.15,
    metalness: 0.8,
    transparent: true,
    opacity: 0.7,
  });

  const corners = [
    { x: 0.7, z: 0.7 },
    { x: -0.7, z: 0.7 },
    { x: 0.7, z: -0.7 },
    { x: -0.7, z: -0.7 },
  ];

  return (
    <group ref={octoRef}>
      {/* Central Monocoque Body */}
      <mesh material={carbonMaterial} position={[0, 0, 0]}>
        <boxGeometry args={[0.65, 0.2, 0.65]} />
      </mesh>

      {/* 4 Carbon Arms extending to 4 Coaxial Motor Mounts (8 Motors Total) */}
      {corners.map((c, idx) => (
        <group key={idx}>
          {/* Carbon Arm */}
          <mesh
            position={[c.x / 2, 0.02, c.z / 2]}
            rotation={[0, idx === 0 || idx === 3 ? -Math.PI / 4 : Math.PI / 4, 0]}
            material={carbonMaterial}
          >
            <boxGeometry args={[0.08, 0.04, 0.95]} />
          </mesh>

          {/* Coaxial Motor Mount (Top & Bottom Motors) */}
          <group position={[c.x, 0.02, c.z]}>
            {/* Top Motor */}
            <mesh position={[0, 0.08, 0]}>
              <cylinderGeometry args={[0.07, 0.07, 0.08, 16]} />
              <meshStandardMaterial color="#0284c7" metalness={0.95} roughness={0.1} />
            </mesh>
            <group
              ref={(el) => {
                topPropsRef.current[idx] = el;
              }}
              position={[0, 0.13, 0]}
            >
              <mesh material={rotorMaterial}>
                <boxGeometry args={[0.82, 0.01, 0.06]} />
              </mesh>
            </group>

            {/* Bottom Motor (Inverted) */}
            <mesh position={[0, -0.08, 0]}>
              <cylinderGeometry args={[0.07, 0.07, 0.08, 16]} />
              <meshStandardMaterial color="#0284c7" metalness={0.95} roughness={0.1} />
            </mesh>
            <group
              ref={(el) => {
                botPropsRef.current[idx] = el;
              }}
              position={[0, -0.13, 0]}
            >
              <mesh material={rotorMaterial}>
                <boxGeometry args={[0.82, 0.01, 0.06]} />
              </mesh>
            </group>
          </group>
        </group>
      ))}

      {/* Uncertainty Spatial Ellipsoid */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[uncertaintyRadius * 1.2, 32, 32]} />
        <meshStandardMaterial
          color={riskStatus === 'CRITICAL' ? '#f43f5e' : riskStatus === 'WARNING' ? '#f59e0b' : '#38bdf8'}
          transparent
          opacity={0.12}
          wireframe={riskStatus !== 'NOMINAL'}
        />
      </mesh>
    </group>
  );
};
