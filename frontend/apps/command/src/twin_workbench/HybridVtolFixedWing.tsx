import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export interface VtolModelProps {
  windMps: number;
  motorDegradationPct: number;
  flightPhase?: 'HOVER_TAKEOFF' | 'TRANSITION' | 'FORWARD_CRUISE' | 'RTL_LAND';
  uncertaintyRadius: number;
  riskStatus: 'NOMINAL' | 'WARNING' | 'CRITICAL';
}

export const HybridVtolFixedWing: React.FC<VtolModelProps> = ({
  windMps,
  motorDegradationPct,
  flightPhase = 'FORWARD_CRUISE',
  uncertaintyRadius,
  riskStatus,
}) => {
  const vtolGroupRef = useRef<THREE.Group>(null);
  const pusherPropRef = useRef<THREE.Group>(null);
  const vtolLift1Ref = useRef<THREE.Group>(null);
  const vtolLift2Ref = useRef<THREE.Group>(null);
  const vtolLift3Ref = useRef<THREE.Group>(null);
  const vtolLift4Ref = useRef<THREE.Group>(null);
  const gimbalRef = useRef<THREE.Group>(null);

  useFrame((state, delta) => {
    // 1. High-speed rear pusher propeller rotation (Forward thrust)
    const pusherSpeed = 70;
    if (pusherPropRef.current) {
      pusherPropRef.current.rotation.z += pusherSpeed * delta;
    }

    // 2. VTOL Lift Motors (active during hover/transition, idle during cruise)
    const liftSpeed = flightPhase === 'FORWARD_CRUISE' ? 12 : 55;
    if (vtolLift1Ref.current) vtolLift1Ref.current.rotation.y += liftSpeed * delta;
    if (vtolLift2Ref.current) vtolLift2Ref.current.rotation.y -= liftSpeed * delta;
    if (vtolLift3Ref.current) vtolLift3Ref.current.rotation.y += (liftSpeed * (1 - motorDegradationPct / 100)) * delta;
    if (vtolLift4Ref.current) vtolLift4Ref.current.rotation.y -= liftSpeed * delta;

    // 3. Forward aerodynamic flight glide & gentle bank oscillation
    if (vtolGroupRef.current) {
      const t = state.clock.getElapsedTime();
      const turbulence = (windMps / 25) * 0.08;
      vtolGroupRef.current.position.y = 0.5 + Math.sin(t * 1.8) * (0.025 + turbulence);
      vtolGroupRef.current.rotation.z = Math.sin(t * 1.2) * (0.035 + turbulence);
      vtolGroupRef.current.rotation.x = -0.04 + Math.cos(t * 1.0) * (0.015 + turbulence);
    }

    // 4. Gimbal forward-looking ground track stabilization
    if (gimbalRef.current) {
      gimbalRef.current.rotation.x = -0.25;
    }
  });

  // Aerospace PBR Materials
  const matteWhiteComposite = new THREE.MeshStandardMaterial({
    color: '#f8fafc',
    roughness: 0.28,
    metalness: 0.45,
  });

  const carbonSparMaterial = new THREE.MeshStandardMaterial({
    color: '#090d16',
    roughness: 0.18,
    metalness: 0.9,
  });

  const motorBellMaterial = new THREE.MeshStandardMaterial({
    color: '#0284c7',
    metalness: 0.98,
    roughness: 0.12,
  });

  const pusherBladeMaterial = new THREE.MeshStandardMaterial({
    color: '#38bdf8',
    roughness: 0.1,
    metalness: 0.8,
  });

  const liftBladeMaterial = new THREE.MeshStandardMaterial({
    color: '#0284c7',
    roughness: 0.2,
    metalness: 0.7,
    transparent: true,
    opacity: 0.65,
  });

  return (
    <group ref={vtolGroupRef}>
      {/* ========================================================================= */}
      {/* 1. AERODYNAMIC STREAMLINED FUSELAGE & AVIONICS POD                        */}
      {/* ========================================================================= */}
      {/* Main Longitudinal Fuselage Body */}
      <mesh position={[0, 0, 0]} rotation={[Math.PI / 2, 0, 0]} material={matteWhiteComposite}>
        <cylinderGeometry args={[0.16, 0.14, 1.8, 24]} />
      </mesh>

      {/* Aerodynamic Tapered Nose Dome */}
      <mesh position={[0, 0, 0.9]} rotation={[Math.PI / 2, 0, 0]} material={matteWhiteComposite}>
        <coneGeometry args={[0.16, 0.42, 24]} />
      </mesh>

      {/* Tapered Tail Cone Heading to Pusher */}
      <mesh position={[0, 0, -0.9]} rotation={[-Math.PI / 2, 0, 0]} material={matteWhiteComposite}>
        <coneGeometry args={[0.14, 0.35, 24]} />
      </mesh>

      {/* Top GPS / Iridium Satellite Communication Fairing */}
      <mesh position={[0, 0.18, -0.1]} material={carbonSparMaterial}>
        <boxGeometry args={[0.12, 0.05, 0.32]} />
      </mesh>

      {/* ========================================================================= */}
      {/* 2. HIGH-ASPECT RATIO MAIN WINGS & AERODYNAMIC WINGLETS (SPAN: 2.8m)       */}
      {/* ========================================================================= */}
      {/* Main Left Wing */}
      <group position={[-0.95, 0.04, 0.1]}>
        <mesh material={matteWhiteComposite} rotation={[0, 0, -0.02]}>
          <boxGeometry args={[1.7, 0.032, 0.48]} />
        </mesh>
        {/* Left Upward Winglet */}
        <mesh position={[-0.85, 0.12, 0]} rotation={[0, 0, 0.65]} material={matteWhiteComposite}>
          <boxGeometry args={[0.26, 0.02, 0.28]} />
        </mesh>
        {/* Left Port Navigation Red Beacon */}
        <mesh position={[-0.88, 0.04, 0.22]}>
          <sphereGeometry args={[0.025, 8, 8]} />
          <meshBasicMaterial color="#f43f5e" />
        </mesh>
        <pointLight position={[-0.88, 0.04, 0.22]} color="#f43f5e" intensity={1.5} distance={2.5} />
      </group>

      {/* Main Right Wing */}
      <group position={[0.95, 0.04, 0.1]}>
        <mesh material={matteWhiteComposite} rotation={[0, 0, 0.02]}>
          <boxGeometry args={[1.7, 0.032, 0.48]} />
        </mesh>
        {/* Right Upward Winglet */}
        <mesh position={[0.85, 0.12, 0]} rotation={[0, 0, -0.65]} material={matteWhiteComposite}>
          <boxGeometry args={[0.26, 0.02, 0.28]} />
        </mesh>
        {/* Right Starboard Navigation Green Beacon */}
        <mesh position={[0.88, 0.04, 0.22]}>
          <sphereGeometry args={[0.025, 8, 8]} />
          <meshBasicMaterial color="#10b981" />
        </mesh>
        <pointLight position={[0.88, 0.04, 0.22]} color="#10b981" intensity={1.5} distance={2.5} />
      </group>

      {/* ========================================================================= */}
      {/* 3. DUAL VTOL BOOM SPARS (LONGITUDINAL CARBON TUBES ACROSS WINGS)          */}
      {/* ========================================================================= */}
      {/* Left VTOL Boom Spar */}
      <mesh position={[-0.65, 0.02, 0.05]} rotation={[Math.PI / 2, 0, 0]} material={carbonSparMaterial}>
        <cylinderGeometry args={[0.034, 0.034, 1.45, 16]} />
      </mesh>

      {/* Right VTOL Boom Spar */}
      <mesh position={[0.65, 0.02, 0.05]} rotation={[Math.PI / 2, 0, 0]} material={carbonSparMaterial}>
        <cylinderGeometry args={[0.034, 0.034, 1.45, 16]} />
      </mesh>

      {/* ========================================================================= */}
      {/* 4. 4X QUAD-PLANE VTOL LIFT MOTORS & PROPELLERS                           */}
      {/* ========================================================================= */}
      {/* VTOL 1: Front-Right (+0.65, +0.72) */}
      <group position={[0.65, 0.06, 0.72]}>
        <mesh material={motorBellMaterial}>
          <cylinderGeometry args={[0.065, 0.065, 0.08, 16]} />
        </mesh>
        <group ref={vtolLift1Ref} position={[0, 0.05, 0]}>
          <mesh material={liftBladeMaterial}>
            <boxGeometry args={[0.74, 0.008, 0.05]} />
          </mesh>
        </group>
      </group>

      {/* VTOL 2: Front-Left (-0.65, +0.72) */}
      <group position={[-0.65, 0.06, 0.72]}>
        <mesh material={motorBellMaterial}>
          <cylinderGeometry args={[0.065, 0.065, 0.08, 16]} />
        </mesh>
        <group ref={vtolLift2Ref} position={[0, 0.05, 0]}>
          <mesh material={liftBladeMaterial}>
            <boxGeometry args={[0.74, 0.008, 0.05]} />
          </mesh>
        </group>
      </group>

      {/* VTOL 3: Rear-Right (+0.65, -0.62) */}
      <group position={[0.65, 0.06, -0.62]}>
        <mesh material={motorBellMaterial}>
          <cylinderGeometry args={[0.065, 0.065, 0.08, 16]} />
        </mesh>
        <group ref={vtolLift3Ref} position={[0, 0.05, 0]}>
          <mesh material={liftBladeMaterial}>
            <boxGeometry args={[0.74, 0.008, 0.05]} />
          </mesh>
        </group>
      </group>

      {/* VTOL 4: Rear-Left (-0.65, -0.62) */}
      <group position={[-0.65, 0.06, -0.62]}>
        <mesh material={motorBellMaterial}>
          <cylinderGeometry args={[0.065, 0.065, 0.08, 16]} />
        </mesh>
        <group ref={vtolLift4Ref} position={[0, 0.05, 0]}>
          <mesh material={liftBladeMaterial}>
            <boxGeometry args={[0.74, 0.008, 0.05]} />
          </mesh>
        </group>
      </group>

      {/* ========================================================================= */}
      {/* 5. REAR BRUSHLESS PUSHER MOTOR & 2-BLADE FOLDING PUSHER PROPELLER         */}
      {/* ========================================================================= */}
      <group position={[0, 0, -1.1]}>
        {/* Pusher Motor Mount */}
        <mesh rotation={[Math.PI / 2, 0, 0]} material={motorBellMaterial}>
          <cylinderGeometry args={[0.06, 0.06, 0.08, 16]} />
        </mesh>
        {/* Spinning Pusher Propeller */}
        <group ref={pusherPropRef} position={[0, 0, -0.05]}>
          <mesh material={pusherBladeMaterial}>
            <boxGeometry args={[0.68, 0.045, 0.01]} />
          </mesh>
          <mesh rotation={[0, 0, Math.PI / 2]} material={pusherBladeMaterial}>
            <boxGeometry args={[0.68, 0.045, 0.01]} />
          </mesh>
        </group>
      </group>

      {/* ========================================================================= */}
      {/* 6. AERODYNAMIC V-TAIL RUDDEVATORS EMPENNAGE                              */}
      {/* ========================================================================= */}
      {/* Left V-Tail Fin */}
      <mesh position={[-0.24, 0.22, -0.85]} rotation={[0, 0, 0.75]} material={matteWhiteComposite}>
        <boxGeometry args={[0.55, 0.02, 0.26]} />
      </mesh>
      {/* Right V-Tail Fin */}
      <mesh position={[0.24, 0.22, -0.85]} rotation={[0, 0, -0.75]} material={matteWhiteComposite}>
        <boxGeometry args={[0.55, 0.02, 0.26]} />
      </mesh>
      {/* Rear Anti-Collision White Strobe */}
      <mesh position={[0, 0.38, -0.92]}>
        <sphereGeometry args={[0.025, 8, 8]} />
        <meshBasicMaterial color="#ffffff" />
      </mesh>
      <pointLight position={[0, 0.38, -0.92]} color="#ffffff" intensity={1.8} distance={3.0} />

      {/* ========================================================================= */}
      {/* 7. NOSE 3-AXIS GYRO-STABILIZED EO/IR SURVEILLANCE GIMBAL                  */}
      {/* ========================================================================= */}
      <group ref={gimbalRef} position={[0, -0.12, 0.82]}>
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.095, 24, 24]} />
          <meshStandardMaterial color="#0f172a" metalness={0.85} roughness={0.15} />
        </mesh>
        {/* 4K Optical Telephoto Lens */}
        <mesh position={[0.028, 0, 0.085]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.024, 0.024, 0.02, 16]} />
          <meshStandardMaterial color="#38bdf8" roughness={0.02} metalness={0.98} />
        </mesh>
        {/* FLIR Radiometric Germanium Thermal Lens */}
        <mesh position={[-0.028, 0, 0.085]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.02, 0.02, 0.02, 16]} />
          <meshStandardMaterial color="#f59e0b" roughness={0.02} metalness={0.98} />
        </mesh>
      </group>

      {/* ========================================================================= */}
      {/* 8. DYNAMIC SPATIAL UNCERTAINTY BUBBLE (EKF2 COVARIANCE ELLIPSOID)         */}
      {/* ========================================================================= */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[uncertaintyRadius * 1.25, 36, 36]} />
        <meshStandardMaterial
          color={riskStatus === 'CRITICAL' ? '#f43f5e' : riskStatus === 'WARNING' ? '#f59e0b' : '#38bdf8'}
          transparent
          opacity={0.14}
          wireframe={riskStatus !== 'NOMINAL'}
        />
      </mesh>
    </group>
  );
};
