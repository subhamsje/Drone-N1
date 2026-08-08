import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export interface HexaProps {
  windMps: number;
  motorDegradationPct: number;
  uncertaintyRadius: number;
  riskStatus: 'NOMINAL' | 'WARNING' | 'CRITICAL';
}

export const HeavyHexacopter: React.FC<HexaProps> = ({
  windMps,
  motorDegradationPct,
  uncertaintyRadius,
  riskStatus,
}) => {
  const hexaGroupRef = useRef<THREE.Group>(null);
  const propsRef = useRef<(THREE.Group | null)[]>([]);

  useFrame((state, delta) => {
    const baseSpeed = 48;
    propsRef.current.forEach((p, i) => {
      if (p) {
        const dir = i % 2 === 0 ? 1 : -1;
        const degradation = i === 2 ? 1 - motorDegradationPct / 100 : 1;
        p.rotation.y += baseSpeed * dir * degradation * delta;
      }
    });

    if (hexaGroupRef.current) {
      const t = state.clock.getElapsedTime();
      const turbulence = (windMps / 25) * 0.05;
      hexaGroupRef.current.position.y = 0.5 + Math.sin(t * 1.5) * (0.02 + turbulence);
      hexaGroupRef.current.rotation.z = Math.sin(t * 1.0) * (0.01 + turbulence);
      hexaGroupRef.current.rotation.x = Math.cos(t * 0.9) * (0.01 + turbulence);
    }
  });

  const carbonMaterial = new THREE.MeshStandardMaterial({
    color: '#0a0d16',
    roughness: 0.2,
    metalness: 0.85,
  });

  const armMaterial = new THREE.MeshStandardMaterial({
    color: '#1e293b',
    roughness: 0.3,
    metalness: 0.9,
  });

  const motorBellMaterial = new THREE.MeshStandardMaterial({
    color: '#0284c7',
    metalness: 0.98,
    roughness: 0.12,
  });

  const rotorMaterial = new THREE.MeshStandardMaterial({
    color: '#38bdf8',
    roughness: 0.15,
    metalness: 0.75,
    transparent: true,
    opacity: 0.7,
  });

  // 6 Arm Angles (60 deg apart)
  const angles = [0, Math.PI / 3, (2 * Math.PI) / 3, Math.PI, (4 * Math.PI) / 3, (5 * Math.PI) / 3];

  return (
    <group ref={hexaGroupRef}>
      {/* Heavy Hexagonal Center Hub Plate */}
      <mesh position={[0, 0, 0]} material={carbonMaterial}>
        <cylinderGeometry args={[0.55, 0.55, 0.22, 6]} />
      </mesh>

      {/* Dual Battery Storage Bays (12S Heavy Industrial LiPo) */}
      <mesh position={[0, 0.14, 0]} material={carbonMaterial}>
        <boxGeometry args={[0.42, 0.12, 0.62]} />
      </mesh>

      {/* 6x Heavy-Lift Carbon Boom Arms & Brushless Motors */}
      {angles.map((ang, idx) => {
        const radius = 0.95;
        const x = Math.sin(ang) * radius;
        const z = Math.cos(ang) * radius;

        return (
          <group key={idx}>
            {/* Structural Carbon Arm Tube */}
            <mesh position={[x / 2, 0.02, z / 2]} rotation={[0, -ang + Math.PI / 2, Math.PI / 2]} material={armMaterial}>
              <cylinderGeometry args={[0.035, 0.035, radius, 16]} />
            </mesh>

            {/* Heavy-Duty Motor Mount & Stator */}
            <group position={[x, 0.06, z]}>
              <mesh material={motorBellMaterial}>
                <cylinderGeometry args={[0.08, 0.08, 0.1, 20]} />
              </mesh>

              {/* Navigation Beacons */}
              {idx === 0 && <pointLight color="#10b981" intensity={1.2} distance={1.8} />}
              {idx === 3 && <pointLight color="#f43f5e" intensity={1.2} distance={1.8} />}

              {/* Carbon Propeller Rotor */}
              <group
                ref={(el) => {
                  propsRef.current[idx] = el;
                }}
                position={[0, 0.07, 0]}
              >
                <mesh material={rotorMaterial}>
                  <boxGeometry args={[0.92, 0.012, 0.07]} />
                </mesh>
              </group>
            </group>
          </group>
        );
      })}

      {/* Heavy Industrial Underslung LiDAR & Payload Cage */}
      <group position={[0, -0.22, 0]}>
        <mesh material={carbonMaterial}>
          <cylinderGeometry args={[0.22, 0.22, 0.16, 16]} />
        </mesh>
        <mesh position={[0, -0.09, 0]}>
          <cylinderGeometry args={[0.18, 0.18, 0.04, 16]} />
          <meshStandardMaterial color="#f59e0b" metalness={0.95} roughness={0.1} />
        </mesh>
      </group>

      {/* Uncertainty Spatial Ellipsoid */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[uncertaintyRadius * 1.35, 32, 32]} />
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
