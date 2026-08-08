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
  const gimbalPitchRef = useRef<THREE.Group>(null);

  // High-fidelity R3F render loop for physics, rotor harmonics, and gimbal hold
  useFrame((state, delta) => {
    const baseSpeed = 52;
    if (prop1Ref.current) prop1Ref.current.rotation.y += baseSpeed * delta;
    if (prop2Ref.current) prop2Ref.current.rotation.y -= baseSpeed * delta;
    if (prop3Ref.current) prop3Ref.current.rotation.y += (baseSpeed * (1 - motorDegradationPct / 100)) * delta;
    if (prop4Ref.current) prop4Ref.current.rotation.y -= baseSpeed * delta;

    // Aerodynamic hover pitch & micro-turbulence
    if (droneGroupRef.current) {
      const t = state.clock.getElapsedTime();
      const turbulence = (windMps / 25) * 0.09;
      droneGroupRef.current.position.y = 0.55 + Math.sin(t * 2.2) * (0.03 + turbulence);
      droneGroupRef.current.rotation.z = Math.sin(t * 1.8) * (0.015 + turbulence);
      droneGroupRef.current.rotation.x = Math.cos(t * 1.4) * (0.015 + turbulence);
    }

    // 3-Axis Gimbal Horizon Stabilization
    if (gimbalPitchRef.current) {
      gimbalPitchRef.current.rotation.x = -0.35 + Math.sin(state.clock.getElapsedTime() * 0.5) * 0.05;
    }
  });

  // Aerospace PBR Materials
  const matteCarbonMaterial = new THREE.MeshStandardMaterial({
    color: '#080d1a',
    roughness: 0.22,
    metalness: 0.88,
  });

  const aluminumArmMaterial = new THREE.MeshStandardMaterial({
    color: '#1a2333',
    roughness: 0.35,
    metalness: 0.92,
  });

  const goldPlatedMaterial = new THREE.MeshStandardMaterial({
    color: '#f59e0b',
    roughness: 0.15,
    metalness: 0.95,
  });

  const rotorBladeMaterial = new THREE.MeshStandardMaterial({
    color: '#38bdf8',
    roughness: 0.15,
    metalness: 0.75,
    transparent: true,
    opacity: 0.7,
  });

  const rotorBlurDiscMaterial = new THREE.MeshBasicMaterial({
    color: '#38bdf8',
    transparent: true,
    opacity: 0.18,
    side: THREE.DoubleSide,
  });

  const motorBellMaterial = new THREE.MeshStandardMaterial({
    color: '#0284c7',
    metalness: 0.98,
    roughness: 0.12,
  });

  const skidLegMaterial = new THREE.MeshStandardMaterial({
    color: '#0f172a',
    metalness: 0.8,
    roughness: 0.4,
  });

  return (
    <group ref={droneGroupRef}>
      {/* ========================================================================= */}
      {/* 1. CENTRAL AEROSPACE MONOCOQUE AVIONICS FUSELAGE                         */}
      {/* ========================================================================= */}
      {/* Main Core Body Shell */}
      <mesh position={[0, 0, 0]} material={matteCarbonMaterial}>
        <boxGeometry args={[0.55, 0.18, 0.75]} />
      </mesh>

      {/* Top Battery Pack / Power Pod Hatch (6S 22000mAh LiPo) */}
      <mesh position={[0, 0.12, -0.05]} material={matteCarbonMaterial}>
        <boxGeometry args={[0.38, 0.08, 0.48]} />
      </mesh>

      {/* Titanium Cooling Heatsink Fins on Avionics Bay */}
      {[-0.12, -0.04, 0.04, 0.12].map((x, i) => (
        <mesh key={i} position={[x, 0.165, -0.05]}>
          <boxGeometry args={[0.015, 0.02, 0.42]} />
          <meshStandardMaterial color="#64748b" metalness={0.95} roughness={0.1} />
        </mesh>
      ))}

      {/* Dual Top-Mounted RTK GNSS Antenna Masts (Sub-Centimeter Accuracy) */}
      <group position={[0.18, 0.22, -0.26]}>
        <mesh position={[0, -0.06, 0]}>
          <cylinderGeometry args={[0.012, 0.012, 0.12, 8]} />
          <primitive object={aluminumArmMaterial} />
        </mesh>
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.055, 0.055, 0.025, 16]} />
          <meshStandardMaterial color="#0f172a" metalness={0.9} roughness={0.2} />
        </mesh>
        <pointLight color="#38bdf8" intensity={0.4} distance={0.8} />
      </group>

      <group position={[-0.18, 0.22, -0.26]}>
        <mesh position={[0, -0.06, 0]}>
          <cylinderGeometry args={[0.012, 0.012, 0.12, 8]} />
          <primitive object={aluminumArmMaterial} />
        </mesh>
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.055, 0.055, 0.025, 16]} />
          <meshStandardMaterial color="#0f172a" metalness={0.9} roughness={0.2} />
        </mesh>
      </group>

      {/* Forward Stereoscopic Binocular Obstacle Avoidance Lenses */}
      <group position={[0, 0.02, 0.38]}>
        <mesh position={[0.14, 0, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.025, 0.025, 0.02, 16]} />
          <meshStandardMaterial color="#38bdf8" roughness={0.05} metalness={0.95} />
        </mesh>
        <mesh position={[-0.14, 0, 0]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.025, 0.025, 0.02, 16]} />
          <meshStandardMaterial color="#38bdf8" roughness={0.05} metalness={0.95} />
        </mesh>
        {/* Tactical Headlight Strip */}
        <mesh position={[0, -0.04, 0]}>
          <boxGeometry args={[0.22, 0.02, 0.02]} />
          <meshStandardMaterial color="#f8fafc" emissive="#38bdf8" emissiveIntensity={1.2} />
        </mesh>
        <pointLight position={[0, 0, 0.3]} color="#38bdf8" intensity={2.0} distance={5} />
      </group>

      {/* Downward Optical Flow & LiDAR Ground Proximity Sensor Array */}
      <group position={[0, -0.09, 0]}>
        <mesh position={[0, 0, 0]} rotation={[0, 0, 0]}>
          <cylinderGeometry args={[0.045, 0.045, 0.02, 16]} />
          <meshStandardMaterial color="#050914" metalness={0.9} roughness={0.1} />
        </mesh>
        <mesh position={[0, -0.012, 0]}>
          <circleGeometry args={[0.035, 16]} />
          <meshBasicMaterial color="#f43f5e" />
        </mesh>
      </group>

      {/* ========================================================================= */}
      {/* 2. DUAL CARBON TUBULAR LANDING GEAR SKIDS WITH RUBBER FEET               */}
      {/* ========================================================================= */}
      {/* Left Landing Skid & Struts */}
      <group position={[-0.32, -0.28, 0]}>
        {/* Longitudinal Skid Tube */}
        <mesh rotation={[Math.PI / 2, 0, 0]} material={skidLegMaterial}>
          <cylinderGeometry args={[0.02, 0.02, 0.95, 12]} />
        </mesh>
        {/* Front Angled Strut */}
        <mesh position={[0, 0.14, 0.26]} rotation={[0, 0, 0.25]} material={skidLegMaterial}>
          <cylinderGeometry args={[0.016, 0.016, 0.32, 12]} />
        </mesh>
        {/* Rear Angled Strut */}
        <mesh position={[0, 0.14, -0.26]} rotation={[0, 0, 0.25]} material={skidLegMaterial}>
          <cylinderGeometry args={[0.016, 0.016, 0.32, 12]} />
        </mesh>
      </group>

      {/* Right Landing Skid & Struts */}
      <group position={[0.32, -0.28, 0]}>
        {/* Longitudinal Skid Tube */}
        <mesh rotation={[Math.PI / 2, 0, 0]} material={skidLegMaterial}>
          <cylinderGeometry args={[0.02, 0.02, 0.95, 12]} />
        </mesh>
        {/* Front Angled Strut */}
        <mesh position={[0, 0.14, 0.26]} rotation={[0, 0, -0.25]} material={skidLegMaterial}>
          <cylinderGeometry args={[0.016, 0.016, 0.32, 12]} />
        </mesh>
        {/* Rear Angled Strut */}
        <mesh position={[0, 0.14, -0.26]} rotation={[0, 0, -0.25]} material={skidLegMaterial}>
          <cylinderGeometry args={[0.016, 0.016, 0.32, 12]} />
        </mesh>
      </group>

      {/* ========================================================================= */}
      {/* 3. 4X STRUCTURAL CARBON TRUSS BOOM ARMS WITH CNC MOTOR MOUNTS             */}
      {/* ========================================================================= */}
      {/* Motor 1: Front-Right (+0.85, +0.85) */}
      <mesh position={[0.55, 0.02, 0.55]} rotation={[0, -Math.PI / 4, 0]} material={aluminumArmMaterial}>
        <cylinderGeometry args={[0.032, 0.032, 1.1, 16]} />
      </mesh>
      {/* Motor 2: Front-Left (-0.85, +0.85) */}
      <mesh position={[-0.55, 0.02, 0.55]} rotation={[0, Math.PI / 4, 0]} material={aluminumArmMaterial}>
        <cylinderGeometry args={[0.032, 0.032, 1.1, 16]} />
      </mesh>
      {/* Motor 3: Rear-Right (+0.85, -0.85) */}
      <mesh position={[0.55, 0.02, 0.55 * -1]} rotation={[0, Math.PI / 4, 0]} material={aluminumArmMaterial}>
        <cylinderGeometry args={[0.032, 0.032, 1.1, 16]} />
      </mesh>
      {/* Motor 4: Rear-Left (-0.85, -0.85) */}
      <mesh position={[-0.55, 0.02, 0.55 * -1]} rotation={[0, -Math.PI / 4, 0]} material={aluminumArmMaterial}>
        <cylinderGeometry args={[0.032, 0.032, 1.1, 16]} />
      </mesh>

      {/* ========================================================================= */}
      {/* 4. 4X HIGH-RPM BRUSHLESS MOTORS & AIRFOIL PROPELLERS                      */}
      {/* ========================================================================= */}
      {/* Motor 1 Assembly: Front-Right */}
      <group position={[0.92, 0.06, 0.92]}>
        {/* CNC Anodized Motor Mount Flange */}
        <mesh position={[0, -0.04, 0]}>
          <cylinderGeometry args={[0.08, 0.08, 0.04, 16]} />
          <primitive object={matteCarbonMaterial} />
        </mesh>
        {/* 12-Slot Brushless Stator Bell */}
        <mesh position={[0, 0.02, 0]} material={motorBellMaterial}>
          <cylinderGeometry args={[0.07, 0.07, 0.09, 20]} />
        </mesh>
        {/* Copper Stator Coil Accent Ring */}
        <mesh position={[0, 0.01, 0]}>
          <torusGeometry args={[0.06, 0.008, 8, 24]} />
          <primitive object={goldPlatedMaterial} />
        </mesh>
        {/* Starboard Green Navigation LED */}
        <mesh position={[0, -0.06, 0]}>
          <sphereGeometry args={[0.028, 12, 12]} />
          <meshBasicMaterial color="#10b981" />
        </mesh>
        <pointLight position={[0, -0.08, 0]} color="#10b981" intensity={1.2} distance={1.8} />

        {/* Spinning Propeller Rotor Airfoils */}
        <group ref={prop1Ref} position={[0, 0.08, 0]}>
          <mesh material={rotorBladeMaterial}>
            <boxGeometry args={[0.85, 0.01, 0.06]} />
          </mesh>
          <mesh rotation={[0, Math.PI / 2, 0]} material={rotorBladeMaterial}>
            <boxGeometry args={[0.85, 0.01, 0.06]} />
          </mesh>
          {/* High-RPM Motion Blur Disc */}
          <mesh rotation={[-Math.PI / 2, 0, 0]} material={rotorBlurDiscMaterial}>
            <ringGeometry args={[0.08, 0.44, 32]} />
          </mesh>
        </group>
      </group>

      {/* Motor 2 Assembly: Front-Left */}
      <group position={[-0.92, 0.06, 0.92]}>
        <mesh position={[0, -0.04, 0]}>
          <cylinderGeometry args={[0.08, 0.08, 0.04, 16]} />
          <primitive object={matteCarbonMaterial} />
        </mesh>
        <mesh position={[0, 0.02, 0]} material={motorBellMaterial}>
          <cylinderGeometry args={[0.07, 0.07, 0.09, 20]} />
        </mesh>
        <mesh position={[0, 0.01, 0]}>
          <torusGeometry args={[0.06, 0.008, 8, 24]} />
          <primitive object={goldPlatedMaterial} />
        </mesh>
        {/* Port Red Navigation LED */}
        <mesh position={[0, -0.06, 0]}>
          <sphereGeometry args={[0.028, 12, 12]} />
          <meshBasicMaterial color="#f43f5e" />
        </mesh>
        <pointLight position={[0, -0.08, 0]} color="#f43f5e" intensity={1.2} distance={1.8} />

        <group ref={prop2Ref} position={[0, 0.08, 0]}>
          <mesh material={rotorBladeMaterial}>
            <boxGeometry args={[0.85, 0.01, 0.06]} />
          </mesh>
          <mesh rotation={[0, Math.PI / 2, 0]} material={rotorBladeMaterial}>
            <boxGeometry args={[0.85, 0.01, 0.06]} />
          </mesh>
          <mesh rotation={[-Math.PI / 2, 0, 0]} material={rotorBlurDiscMaterial}>
            <ringGeometry args={[0.08, 0.44, 32]} />
          </mesh>
        </group>
      </group>

      {/* Motor 3 Assembly: Rear-Right (Affected by bearing wear slider) */}
      <group position={[0.92, 0.06, -0.92]}>
        <mesh position={[0, -0.04, 0]}>
          <cylinderGeometry args={[0.08, 0.08, 0.04, 16]} />
          <primitive object={matteCarbonMaterial} />
        </mesh>
        <mesh position={[0, 0.02, 0]} material={motorBellMaterial}>
          <cylinderGeometry args={[0.07, 0.07, 0.09, 20]} />
        </mesh>
        <mesh position={[0, 0.01, 0]}>
          <torusGeometry args={[0.06, 0.008, 8, 24]} />
          <primitive object={goldPlatedMaterial} />
        </mesh>
        {/* Rear White Anti-Collision Strobe */}
        <mesh position={[0, -0.06, 0]}>
          <sphereGeometry args={[0.028, 12, 12]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
        <pointLight position={[0, -0.08, 0]} color="#ffffff" intensity={1.2} distance={1.8} />

        <group ref={prop3Ref} position={[0, 0.08, 0]}>
          <mesh material={rotorBladeMaterial}>
            <boxGeometry args={[0.85, 0.01, 0.06]} />
          </mesh>
          <mesh rotation={[0, Math.PI / 2, 0]} material={rotorBladeMaterial}>
            <boxGeometry args={[0.85, 0.01, 0.06]} />
          </mesh>
          <mesh rotation={[-Math.PI / 2, 0, 0]} material={rotorBlurDiscMaterial}>
            <ringGeometry args={[0.08, 0.44, 32]} />
          </mesh>
        </group>
      </group>

      {/* Motor 4 Assembly: Rear-Left */}
      <group position={[-0.92, 0.06, -0.92]}>
        <mesh position={[0, -0.04, 0]}>
          <cylinderGeometry args={[0.08, 0.08, 0.04, 16]} />
          <primitive object={matteCarbonMaterial} />
        </mesh>
        <mesh position={[0, 0.02, 0]} material={motorBellMaterial}>
          <cylinderGeometry args={[0.07, 0.07, 0.09, 20]} />
        </mesh>
        <mesh position={[0, 0.01, 0]}>
          <torusGeometry args={[0.06, 0.008, 8, 24]} />
          <primitive object={goldPlatedMaterial} />
        </mesh>
        {/* Rear White Anti-Collision Strobe */}
        <mesh position={[0, -0.06, 0]}>
          <sphereGeometry args={[0.028, 12, 12]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
        <pointLight position={[0, -0.08, 0]} color="#ffffff" intensity={1.2} distance={1.8} />

        <group ref={prop4Ref} position={[0, 0.08, 0]}>
          <mesh material={rotorBladeMaterial}>
            <boxGeometry args={[0.85, 0.01, 0.06]} />
          </mesh>
          <mesh rotation={[0, Math.PI / 2, 0]} material={rotorBladeMaterial}>
            <boxGeometry args={[0.85, 0.01, 0.06]} />
          </mesh>
          <mesh rotation={[-Math.PI / 2, 0, 0]} material={rotorBlurDiscMaterial}>
            <ringGeometry args={[0.08, 0.44, 32]} />
          </mesh>
        </group>
      </group>

      {/* ========================================================================= */}
      {/* 5. 3-AXIS STABILIZED TRI-SENSOR EO/IR/LRF GIMBAL TURRET                  */}
      {/* ========================================================================= */}
      <group position={[0, -0.16, 0.22]}>
        {/* Yaw Gimbal Arm */}
        <mesh position={[0, 0.04, 0]}>
          <cylinderGeometry args={[0.045, 0.045, 0.06, 16]} />
          <meshStandardMaterial color="#1e293b" metalness={0.95} roughness={0.1} />
        </mesh>

        {/* Pitch & Roll Stabilized Turret Shell */}
        <group ref={gimbalPitchRef} position={[0, -0.06, 0]}>
          <mesh>
            <sphereGeometry args={[0.11, 32, 32]} />
            <meshStandardMaterial color="#0b1220" metalness={0.88} roughness={0.2} />
          </mesh>

          {/* 1. 4K Sony Exmor CMOS Optical Lens */}
          <mesh position={[0.038, 0, 0.095]} rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.032, 0.032, 0.03, 20]} />
            <meshStandardMaterial color="#38bdf8" roughness={0.02} metalness={0.98} />
          </mesh>

          {/* 2. Radiometric FLIR Boson Thermal LWIR Core (Germanium Gold Lens) */}
          <mesh position={[-0.038, 0, 0.095]} rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.026, 0.026, 0.03, 20]} />
            <meshStandardMaterial color="#f59e0b" roughness={0.02} metalness={0.98} />
          </mesh>

          {/* 3. Eye-Safe 1200m Laser Rangefinder (LRF) Emitter Aperture */}
          <mesh position={[0, 0.045, 0.09]} rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.012, 0.012, 0.02, 12]} />
            <meshStandardMaterial color="#10b981" roughness={0.1} metalness={0.9} />
          </mesh>
        </group>
      </group>

      {/* ========================================================================= */}
      {/* 6. DYNAMIC 3D SPATIAL UNCERTAINTY BUBBLE (EKF2 COVARIANCE ELLIPSOID)      */}
      {/* ========================================================================= */}
      <mesh position={[0, 0.12, 0]}>
        <sphereGeometry args={[uncertaintyRadius, 36, 36]} />
        <meshStandardMaterial
          color={riskStatus === 'CRITICAL' ? '#f43f5e' : riskStatus === 'WARNING' ? '#f59e0b' : '#38bdf8'}
          transparent
          opacity={0.15}
          wireframe={riskStatus !== 'NOMINAL'}
        />
      </mesh>
    </group>
  );
};
