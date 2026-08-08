import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export interface DroneModelProps {
  windMps: number;
  motorDegradationPct: number;
  uncertaintyRadius: number;
  riskStatus: 'NOMINAL' | 'WARNING' | 'CRITICAL';
}

export const RealisticTacticalDrone: React.FC<DroneModelProps> = ({
  windMps,
  motorDegradationPct,
  uncertaintyRadius,
  riskStatus,
}) => {
  const droneGroupRef = useRef<THREE.Group>(null);
  const prop1Ref = useRef<THREE.Group>(null);
  const prop2Ref = useRef<THREE.Group>(null);
  const prop3Ref = useRef<THREE.Group>(null);
  const prop4Ref = useRef<THREE.Group>(null);
  const gimbalRef = useRef<THREE.Group>(null);

  // High-speed rotor spin & aerodynamic pitch oscillation in R3F render loop
  useFrame((state, delta) => {
    // Spin propellers at high RPM (degraded motor 3 spins slightly slower)
    const baseSpeed = 45;
    if (prop1Ref.current) prop1Ref.current.rotation.y += baseSpeed * delta;
    if (prop2Ref.current) prop2Ref.current.rotation.y -= baseSpeed * delta;
    if (prop3Ref.current) prop3Ref.current.rotation.y += (baseSpeed * (1 - motorDegradationPct / 120)) * delta;
    if (prop4Ref.current) prop4Ref.current.rotation.y -= baseSpeed * delta;

    // Hover aerodynamics oscillation influenced by wind shear
    if (droneGroupRef.current) {
      const t = state.clock.getElapsedTime();
      const windTurbulence = (windMps / 20) * 0.08;
      droneGroupRef.current.position.y = 0.5 + Math.sin(t * 2) * (0.04 + windTurbulence);
      droneGroupRef.current.rotation.z = Math.sin(t * 1.5) * (0.02 + windTurbulence);
      droneGroupRef.current.rotation.x = Math.cos(t * 1.2) * (0.02 + windTurbulence);
    }

    // Gimbal optical pod self-stabilization (horizon hold)
    if (gimbalRef.current) {
      gimbalRef.current.rotation.x = -0.4;
    }
  });

  const bodyMaterial = new THREE.MeshStandardMaterial({
    color: '#0a0f1d',
    roughness: 0.25,
    metalness: 0.85,
  });

  const armMaterial = new THREE.MeshStandardMaterial({
    color: '#1e293b',
    roughness: 0.3,
    metalness: 0.9,
  });

  const rotorMaterial = new THREE.MeshStandardMaterial({
    color: '#38bdf8',
    roughness: 0.2,
    metalness: 0.8,
    transparent: true,
    opacity: 0.65,
  });

  const motorBellMaterial = new THREE.MeshStandardMaterial({
    color: '#0284c7',
    metalness: 0.95,
    roughness: 0.15,
  });

  return (
    <group ref={droneGroupRef}>
      {/* 1. CENTRAL CARBON-FIBER AVIONICS FUSELAGE */}
      <mesh position={[0, 0, 0]} material={bodyMaterial}>
        <cylinderGeometry args={[0.35, 0.45, 0.16, 8]} />
      </mesh>
      
      {/* Top GPS / RTK Antenna Puck Dome */}
      <mesh position={[0, 0.11, -0.05]}>
        <cylinderGeometry args={[0.12, 0.12, 0.05, 16]} />
        <meshStandardMaterial color="#0f172a" metalness={0.9} roughness={0.1} />
      </mesh>
      <mesh position={[0, 0.14, -0.05]}>
        <sphereGeometry args={[0.12, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshStandardMaterial color="#38bdf8" emissive="#0284c7" emissiveIntensity={0.3} metalness={0.5} roughness={0.2} />
      </mesh>

      {/* Frontal Tactical Headlight */}
      <mesh position={[0, 0.02, 0.38]}>
        <boxGeometry args={[0.18, 0.06, 0.05]} />
        <meshStandardMaterial color="#f8fafc" emissive="#38bdf8" emissiveIntensity={0.8} />
      </mesh>
      <pointLight position={[0, 0.02, 0.6]} color="#38bdf8" intensity={1.5} distance={4} />

      {/* 2. 4X ANODIZED CARBON-FIBER BOOM ARMS */}
      {/* Front-Right Boom */}
      <mesh position={[0.45, 0.02, 0.45]} rotation={[0, -Math.PI / 4, 0]} material={armMaterial}>
        <cylinderGeometry args={[0.028, 0.028, 0.9, 12]} />
      </mesh>
      {/* Front-Left Boom */}
      <mesh position={[-0.45, 0.02, 0.45]} rotation={[0, Math.PI / 4, 0]} material={armMaterial}>
        <cylinderGeometry args={[0.028, 0.028, 0.9, 12]} />
      </mesh>
      {/* Rear-Right Boom */}
      <mesh position={[0.45, 0.02, -0.45]} rotation={[0, Math.PI / 4, 0]} material={armMaterial}>
        <cylinderGeometry args={[0.028, 0.028, 0.9, 12]} />
      </mesh>
      {/* Rear-Left Boom */}
      <mesh position={[-0.45, 0.02, -0.45]} rotation={[0, -Math.PI / 4, 0]} material={armMaterial}>
        <cylinderGeometry args={[0.028, 0.028, 0.9, 12]} />
      </mesh>

      {/* 3. 4X BRUSHLESS MOTORS & PROPELLERS */}
      {/* Motor 1: Front-Right (+0.75, +0.75) */}
      <group position={[0.75, 0.06, 0.75]}>
        <mesh material={motorBellMaterial} position={[0, 0, 0]}>
          <cylinderGeometry args={[0.065, 0.065, 0.08, 16]} />
        </mesh>
        <pointLight position={[0, -0.06, 0]} color="#10b981" intensity={0.8} distance={1.2} />
        {/* Starboard Green Navigation LED */}
        <mesh position={[0, -0.04, 0]}>
          <sphereGeometry args={[0.025, 8, 8]} />
          <meshBasicMaterial color="#10b981" />
        </mesh>
        {/* Spinning Rotor Group */}
        <group ref={prop1Ref} position={[0, 0.05, 0]}>
          <mesh material={rotorMaterial}>
            <boxGeometry args={[0.72, 0.008, 0.05]} />
          </mesh>
        </group>
      </group>

      {/* Motor 2: Front-Left (-0.75, +0.75) */}
      <group position={[-0.75, 0.06, 0.75]}>
        <mesh material={motorBellMaterial} position={[0, 0, 0]}>
          <cylinderGeometry args={[0.065, 0.065, 0.08, 16]} />
        </mesh>
        {/* Port Red Navigation LED */}
        <pointLight position={[0, -0.06, 0]} color="#f43f5e" intensity={0.8} distance={1.2} />
        <mesh position={[0, -0.04, 0]}>
          <sphereGeometry args={[0.025, 8, 8]} />
          <meshBasicMaterial color="#f43f5e" />
        </mesh>
        <group ref={prop2Ref} position={[0, 0.05, 0]}>
          <mesh material={rotorMaterial}>
            <boxGeometry args={[0.72, 0.008, 0.05]} />
          </mesh>
        </group>
      </group>

      {/* Motor 3: Rear-Right (+0.75, -0.75) */}
      <group position={[0.75, 0.06, -0.75]}>
        <mesh material={motorBellMaterial} position={[0, 0, 0]}>
          <cylinderGeometry args={[0.065, 0.065, 0.08, 16]} />
        </mesh>
        {/* White Strobe LED */}
        <mesh position={[0, -0.04, 0]}>
          <sphereGeometry args={[0.025, 8, 8]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
        <group ref={prop3Ref} position={[0, 0.05, 0]}>
          <mesh material={rotorMaterial}>
            <boxGeometry args={[0.72, 0.008, 0.05]} />
          </mesh>
        </group>
      </group>

      {/* Motor 4: Rear-Left (-0.75, -0.75) */}
      <group position={[-0.75, 0.06, -0.75]}>
        <mesh material={motorBellMaterial} position={[0, 0, 0]}>
          <cylinderGeometry args={[0.065, 0.065, 0.08, 16]} />
        </mesh>
        {/* White Strobe LED */}
        <mesh position={[0, -0.04, 0]}>
          <sphereGeometry args={[0.025, 8, 8]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
        <group ref={prop4Ref} position={[0, 0.05, 0]}>
          <mesh material={rotorMaterial}>
            <boxGeometry args={[0.72, 0.008, 0.05]} />
          </mesh>
        </group>
      </group>

      {/* 4. 3-AXIS GYRO-STABILIZED EO/IR SENSOR POD GIMBAL */}
      <group ref={gimbalRef} position={[0, -0.12, 0.18]}>
        {/* Gimbal Yaw Arm */}
        <mesh position={[0, 0.02, 0]}>
          <cylinderGeometry args={[0.04, 0.04, 0.04, 12]} />
          <meshStandardMaterial color="#1e293b" metalness={0.9} />
        </mesh>
        {/* Spherical Camera Turret */}
        <mesh position={[0, -0.06, 0]}>
          <sphereGeometry args={[0.09, 24, 24]} />
          <meshStandardMaterial color="#0f172a" metalness={0.8} roughness={0.2} />
        </mesh>
        {/* Dual EO/IR Optics Lenses */}
        <mesh position={[0.025, -0.06, 0.08]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.024, 0.024, 0.02, 16]} />
          <meshStandardMaterial color="#38bdf8" roughness={0.05} metalness={0.9} />
        </mesh>
        <mesh position={[-0.025, -0.06, 0.08]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.018, 0.018, 0.02, 16]} />
          <meshStandardMaterial color="#f59e0b" roughness={0.05} metalness={0.9} />
        </mesh>
      </group>

      {/* 5. 3D SPATIAL UNCERTAINTY BUBBLE (EKF2 COVARIANCE ELLIPSOID) */}
      <mesh position={[0, 0.1, 0]}>
        <sphereGeometry args={[uncertaintyRadius, 32, 32]} />
        <meshStandardMaterial
          color={riskStatus === 'CRITICAL' ? '#f43f5e' : riskStatus === 'WARNING' ? '#f59e0b' : '#38bdf8'}
          transparent
          opacity={0.18}
          wireframe={riskStatus !== 'NOMINAL'}
        />
      </mesh>
    </group>
  );
};
