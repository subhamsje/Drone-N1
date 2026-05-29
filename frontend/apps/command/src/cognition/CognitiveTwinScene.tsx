import { useRef, type MutableRefObject } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { OrbitControls, Grid, Line } from '@react-three/drei';
import { survivabilityColor } from '@altaria/cognition-sdk';
import { cognitionEngine } from '../config/runtime';
import { isRenderDegraded, recordFrame } from '../runtime/renderScheduler';
import { useCognitionStore } from '../stores/cognitionStore';
import { WorldFuturesEngine } from '../world_model/WorldFuturesEngine';
import { EnvironmentalWorld } from './battlefield/EnvironmentalWorld';
import { OperationalCamera } from './battlefield/OperationalCamera';
import { UncertaintyFog } from './battlefield/UncertaintyFog';
import {
  AnimatedTurbulence,
  HardwareStressOverlay,
  RfDeniedVolume,
  SurvivabilityHalo,
  SwarmCouplingArcs,
  ThreatVolume,
  UncertaintyBreathingField,
} from './battlefield/BattlefieldLayers';

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

function FrameBudget() {
  useFrame((_, delta) => {
    recordFrame(delta * 1000);
    if (isRenderDegraded()) useCognitionStore.getState().setDegraded(true);
  });
  return null;
}

function AircraftBody() {
  const group = useRef<THREE.Group>(null);
  const mat = useRef<THREE.MeshStandardMaterial>(null);
  const display = useRef({ surv: 0.75, heading: 0 });
  const hover = useRef(0);

  useFrame((_, delta) => {
    const t = cognitionEngine().renderState.twin;
    display.current.surv = lerp(display.current.surv, t.survivability, Math.min(1, delta * 8));
    display.current.heading = lerp(display.current.heading, THREE.MathUtils.degToRad(t.headingDeg), delta * 4);
    hover.current = lerp(hover.current, Math.sin(performance.now() * 0.001) * 0.03, delta * 2);
    if (group.current) {
      group.current.position.y = hover.current;
      group.current.rotation.y = display.current.heading;
    }
    if (mat.current) {
      const c = survivabilityColor(display.current.surv);
      mat.current.color.set(c);
      mat.current.emissive.set(c);
      mat.current.emissiveIntensity = 0.35 + (1 - display.current.surv) * 0.25;
    }
  });

  return (
    <group ref={group}>
      <mesh castShadow>
        <boxGeometry args={[1.2, 0.15, 1.2]} />
        <meshStandardMaterial color="#1e293b" metalness={0.75} roughness={0.25} />
      </mesh>
      <mesh position={[0, 0.2, 0]} castShadow>
        <coneGeometry args={[0.08, 0.5, 8]} />
        <meshStandardMaterial ref={mat} color="#22d3a8" emissive="#22d3a8" emissiveIntensity={0.4} />
      </mesh>
      {[1, -1].map((x) =>
        [1, -1].map((z) => (
          <mesh key={`${x}-${z}`} position={[x * 0.5, -0.05, z * 0.5]} castShadow>
            <cylinderGeometry args={[0.06, 0.08, 0.12, 8]} />
            <meshStandardMaterial color="#64748b" metalness={0.5} roughness={0.4} />
          </mesh>
        )),
      )}
      <ThermalPlume />
    </group>
  );
}

function ThermalPlume() {
  const mesh = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    const load = cognitionEngine().renderState.twin.thermalLoad;
    if (mesh.current) {
      mesh.current.visible = load > 0.15;
      const mat = mesh.current.material as THREE.MeshBasicMaterial;
      mat.opacity = lerp(mat.opacity, load * 0.35, delta * 4);
      mesh.current.scale.y = 0.5 + load * 1.2;
    }
  });
  return (
    <mesh ref={mesh} position={[0, -0.2, 0]}>
      <coneGeometry args={[0.25, 0.5, 8]} />
      <meshBasicMaterial color="#f97316" transparent opacity={0.15} />
    </mesh>
  );
}

function ThrustVectors() {
  const scales = useRef([0.35, 0.35, 0.35, 0.35]);
  const origins: [number, number, number][] = [
    [0.5, -0.05, 0.5],
    [-0.5, -0.05, 0.5],
    [0.5, -0.05, -0.5],
    [-0.5, -0.05, -0.5],
  ];

  useFrame((_, delta) => {
    const target = cognitionEngine().renderState.twin.thrustScale * 0.35;
    for (let i = 0; i < 4; i++) {
      scales.current[i] = lerp(scales.current[i], target, Math.min(1, delta * 6));
    }
  });

  return (
    <>
      {origins.map((o, i) => (
        <ThrustColumn key={i} origin={o} scaleRef={scales} index={i} />
      ))}
    </>
  );
}

function ThrustColumn({
  origin,
  scaleRef,
  index,
}: {
  origin: [number, number, number];
  scaleRef: MutableRefObject<number[]>;
  index: number;
}) {
  const mesh = useRef<THREE.Mesh>(null);
  useFrame(() => {
    const h = scaleRef.current[index];
    if (mesh.current) mesh.current.position.set(origin[0], origin[1] - h / 2, origin[2]);
    if (mesh.current) mesh.current.scale.set(1, h / 0.35, 1);
  });
  return (
    <mesh ref={mesh} position={[origin[0], origin[1] - 0.175, origin[2]]}>
      <cylinderGeometry args={[0.02, 0.04, 0.35, 6]} />
      <meshBasicMaterial color="#22d3a8" transparent opacity={0.85} />
    </mesh>
  );
}

function PrimaryFuturePath() {
  const display = useRef<[number, number, number][]>([
    [0, 0, 0],
    [0.5, 0.33, 0.5],
    [1, 0.5, 1],
    [1.5, 0.67, 1.8],
  ]);

  useFrame((_, delta) => {
    const target = cognitionEngine().renderState.twin.trajectory;
    const d = display.current;
    for (let i = 0; i < target.length; i++) {
      if (!d[i]) d[i] = [...target[i]] as [number, number, number];
      d[i][0] = lerp(d[i][0], target[i][0], Math.min(1, delta * 5));
      d[i][1] = lerp(d[i][1], target[i][1], Math.min(1, delta * 5));
      d[i][2] = lerp(d[i][2], target[i][2], Math.min(1, delta * 5));
    }
  });

  return (
    <Line points={display.current} color="#22d3a8" lineWidth={2.5} transparent opacity={0.9} />
  );
}

export function CognitiveTwinScene() {
  return (
    <>
      <FrameBudget />
      <color attach="background" args={['#010409']} />
      <fog attach="fog" args={['#0f172a', 14, 42]} />
      <ambientLight intensity={0.28} />
      <directionalLight position={[8, 14, 6]} intensity={1.2} color="#e2e8f0" castShadow />
      <hemisphereLight args={['#1e3a5f', '#020617', 0.35]} />
      <pointLight position={[-4, 3, -3]} intensity={0.35} color="#22d3ee" />

      <EnvironmentalWorld />
      <Grid
        infiniteGrid
        fadeDistance={32}
        cellColor="#0c1929"
        sectionColor="#1e3a5f"
        cellThickness={0.5}
        sectionThickness={0.9}
        position={[0, -0.07, 0]}
      />

      <UncertaintyFog />
      <SurvivabilityHalo />
      <UncertaintyBreathingField />
      <WorldFuturesEngine />
      <ThreatVolume />
      <RfDeniedVolume />
      <AnimatedTurbulence />
      <SwarmCouplingArcs />
      <PrimaryFuturePath />

      <AircraftBody />
      <HardwareStressOverlay />
      <ThrustVectors />

      <OperationalCamera />
      <OrbitControls makeDefault enableDamping dampingFactor={0.06} enablePan enableZoom maxPolarAngle={Math.PI / 2.05} />
    </>
  );
}
