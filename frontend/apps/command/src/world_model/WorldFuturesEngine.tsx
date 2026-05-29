import { useRef } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';
import type { FutureBranch } from '@altaria/realtime-engine';
import { cognitionEngine } from '../config/runtime';
import { cognitionBreath, cognitionTime } from '../runtime/cognitionClock';
import { UncertaintyConeScene } from './UncertaintyCone';

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

/** Probabilistic route cone rings along each future branch */
function RouteConeRings({ branchIndex, color }: { branchIndex: number; color: string }) {
  const rings = useRef<THREE.Group>(null);
  const prob = useRef(0.3);

  useFrame((_, delta) => {
    const branch = cognitionEngine().renderState.twin.branches[branchIndex];
    if (!branch) return;
    prob.current = lerp(prob.current, branch.probability, delta * 3);
    if (!rings.current) return;
    rings.current.visible = prob.current > 0.04;
  });

  const branch = cognitionEngine().renderState.twin.branches[branchIndex];
  if (!branch || branch.points.length < 2) return null;
  const pts = branch.points;

  return (
    <group ref={rings}>
      {pts.map((p, i) => {
        const r = 0.15 + i * 0.12 + prob.current * 0.35;
        const segments = 24;
        const ring: [number, number, number][] = [];
        for (let s = 0; s <= segments; s++) {
          const a = (s / segments) * Math.PI * 2;
          ring.push([p[0] + Math.cos(a) * r, p[1], p[2] + Math.sin(a) * r]);
        }
        return (
          <Line
            key={i}
            points={ring}
            color={color}
            lineWidth={0.8}
            transparent
            opacity={0.08 + prob.current * 0.2}
          />
        );
      })}
    </group>
  );
}

/** Predicted crash trajectory — what AI fears before acting */
function PredictedCrashPath() {
  const display = useRef<[number, number, number][]>([]);
  const opacity = useRef(0);

  useFrame((_, delta) => {
    const t = cognitionEngine().renderState.twin;
    display.current = t.crashPath;
    opacity.current = lerp(opacity.current, Math.min(0.85, t.crashRisk * 1.2 + t.uncertainty * 0.3), delta * 4);
  });

  if (display.current.length < 2 || opacity.current < 0.05) return null;

  return (
    <Line
      points={display.current}
      color="#ef4444"
      lineWidth={2}
      transparent
      opacity={opacity.current}
      dashed
      dashSize={0.12}
      gapSize={0.08}
    />
  );
}

/** Survivability evolution shells at prediction horizons */
function SurvivabilityEvolutionShells() {
  const shells = useRef<THREE.Mesh[]>([]);
  const radii = useRef([1.2, 1.8, 2.4]);

  useFrame((_, delta) => {
    const t = cognitionEngine().renderState.twin;
    const breath = cognitionBreath(0.3);
    const targets = [
      1 + (1 - t.futureSurvivability[0]) * 0.8 + breath * 0.05,
      1.4 + (1 - t.futureSurvivability[1]) * 1.1,
      1.9 + (1 - t.futureSurvivability[2]) * 1.4 + t.crashRisk * 0.6,
    ];
    for (let i = 0; i < 3; i++) {
      radii.current[i] = lerp(radii.current[i], targets[i], delta * 2);
      const m = shells.current[i];
      if (m) {
        m.scale.setScalar(radii.current[i]);
        const mat = m.material as THREE.MeshBasicMaterial;
        const surv = t.futureSurvivability[i] ?? 0.7;
        mat.opacity = 0.03 + (1 - surv) * 0.08 + breath * 0.02;
        mat.color.setHSL(0.45 - (1 - surv) * 0.25, 0.8, 0.45);
      }
    }
  });

  return (
    <group position={[0, 0.5, 0]}>
      {[0, 1, 2].map((i) => (
        <mesh
          key={i}
          ref={(el) => {
            if (el) shells.current[i] = el;
          }}
          rotation={[-Math.PI / 2, 0, 0]}
        >
          <ringGeometry args={[0.9 + i * 0.15, 1 + i * 0.15, 48]} />
          <meshBasicMaterial transparent side={THREE.DoubleSide} color="#22d3a8" />
        </mesh>
      ))}
    </group>
  );
}

/** Landing outcome markers per branch terminus */
function LandingOutcomes() {
  const branches = useRef(cognitionEngine().renderState.twin.branches);

  useFrame(() => {
    branches.current = cognitionEngine().renderState.twin.branches;
  });

  const colors = ['#22d3a8', '#f59e0b', '#ef4444'];

  return (
    <group>
      {branches.current.map((b, i) => {
        const end = b.points[b.points.length - 1];
        if (!end) return null;
        return (
          <mesh key={i} position={[end[0], end[1] + 0.08, end[2]]}>
            <cylinderGeometry args={[0.2 + b.probability * 0.3, 0.25, 0.06, 6]} />
            <meshBasicMaterial color={colors[i % colors.length]} transparent opacity={0.35 + b.probability * 0.4} />
          </mesh>
        );
      })}
      <mesh position={cognitionEngine().renderState.twin.landingPoint}>
        <ringGeometry args={[0.35, 0.55, 32]} />
        <meshBasicMaterial color="#22d3a8" transparent opacity={0.5} side={THREE.DoubleSide} />
      </mesh>
    </group>
  );
}

/** Spatial world-model futures — predictive cognition, not telemetry */
export function WorldFuturesEngine() {
  const branches = useRef(cognitionEngine().renderState.twin.branches);

  useFrame(() => {
    branches.current = cognitionEngine().renderState.twin.branches;
  });

  const colors = ['#38bdf8', '#f59e0b', '#f87171'];

  return (
    <group>
      <UncertaintyConeScene />
      <SurvivabilityEvolutionShells />
      <PredictedCrashPath />
      {branches.current.map((b, i) => (
        <group key={b.label}>
          <Line
            points={b.points}
            color={colors[i % colors.length]}
            lineWidth={1 + b.probability * 2}
            transparent
            opacity={0.2 + b.probability * 0.55}
            dashed={i > 0}
          />
          <RouteConeRings branchIndex={i} color={colors[i % colors.length]} />
        </group>
      ))}
      <LandingOutcomes />
      <CognitionWaveGround />
    </group>
  );
}

/** Subtle ground cognition waves */
function CognitionWaveGround() {
  const mesh = useRef<THREE.Mesh>(null);
  useFrame(() => {
    const t = cognitionTime();
    const unc = cognitionEngine().renderState.twin.uncertainty;
    if (mesh.current) {
      mesh.current.scale.set(12 + Math.sin(t * 0.8) * unc * 0.5, 1, 12 + Math.cos(t * 0.6) * unc * 0.5);
      const mat = mesh.current.material as THREE.MeshBasicMaterial;
      mat.opacity = 0.02 + unc * 0.04;
    }
  });
  return (
    <mesh ref={mesh} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
      <ringGeometry args={[4, 8, 64]} />
      <meshBasicMaterial color="#22d3ee" transparent opacity={0.03} />
    </mesh>
  );
}
