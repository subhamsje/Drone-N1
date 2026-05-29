import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { cognitionEngine } from '../config/runtime';

/** Volumetric, pulsing uncertainty cone shader */
const UncertaintyConeShader = {
  uniforms: {
    uTime: { value: 0 },
    uUncertainty: { value: 0.3 },
    uSurvivability: { value: 0.75 },
    uColorHigh: { value: new THREE.Color('#38bdf8') },
    uColorLow: { value: new THREE.Color('#ef4444') },
  },
  vertexShader: `
    varying vec2 vUv;
    varying vec3 vPosition;
    uniform float uTime;
    uniform float uUncertainty;

    // Simplex noise function
    vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 permute(vec4 x) { return mod289(((x * 34.0) + 1.0) * x); }
    vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
    
    float snoise(vec3 v) {
      const vec2 C = vec2(1.0/6.0, 1.0/3.0);
      const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
      vec3 i  = floor(v + dot(v, C.yyy));
      vec3 x0 = v - i + dot(i, C.xxx);
      vec3 g = step(x0.yzx, x0.xyz);
      vec3 l = 1.0 - g;
      vec3 i1 = min(g.xyz, l.zxy);
      vec3 i2 = max(g.xyz, l.zxy);
      vec3 x1 = x0 - i1 + C.xxx;
      vec3 x2 = x0 - i2 + C.yyy;
      vec3 x3 = x0 - D.yyy;
      i = mod289(i);
      vec4 p = permute(permute(permute(
                i.z + vec4(0.0, i1.z, i2.z, 1.0))
              + i.y + vec4(0.0, i1.y, i2.y, 1.0))
              + i.x + vec4(0.0, i1.x, i2.x, 1.0));
      float n_ = 0.142857142857;
      vec3 ns = n_ * D.wyz - D.xzx;
      vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
      vec4 x_ = floor(j * ns.z);
      vec4 y_ = floor(j - 7.0 * x_);
      vec4 x = x_ *ns.x + ns.yyyy;
      vec4 y = y_ *ns.x + ns.yyyy;
      vec4 h = 1.0 - abs(x) - abs(y);
      vec4 b0 = vec4(x.xy, y.xy);
      vec4 b1 = vec4(x.zw, y.zw);
      vec4 s0 = floor(b0)*2.0 + 1.0;
      vec4 s1 = floor(b1)*2.0 + 1.0;
      vec4 sh = -step(h, vec4(0.0));
      vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
      vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
      vec3 p0 = vec3(a0.xy, h.x);
      vec3 p1 = vec3(a0.zw, h.y);
      vec3 p2 = vec3(a1.xy, h.z);
      vec3 p3 = vec3(a1.zw, h.w);
      vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
      p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
      vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
      m = m * m;
      return 42.0 * dot(m * m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
    }

    void main() {
      vUv = uv;
      vPosition = position;
      
      // Turbulence effect along the cone
      float noise = snoise(position * 2.0 + uTime * 1.5) * uUncertainty * 0.4;
      vec3 pos = position + normal * noise * (vUv.y); // More noise at the wide end
      
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    varying vec2 vUv;
    varying vec3 vPosition;
    uniform float uTime;
    uniform float uUncertainty;
    uniform float uSurvivability;
    uniform vec3 uColorHigh;
    uniform vec3 uColorLow;

    void main() {
      // Base fog transparency decreases towards edges and wide end
      float alpha = (1.0 - vUv.y) * 0.8;
      
      // Pulse effect
      float pulse = sin(uTime * 3.0 - vUv.y * 10.0) * 0.5 + 0.5;
      alpha *= 0.2 + pulse * 0.3 * uUncertainty;
      
      // Color interpolation based on survivability
      vec3 color = mix(uColorLow, uColorHigh, uSurvivability);
      
      // Add subtle scanline effect
      float scanline = sin(vUv.y * 100.0 - uTime * 10.0) * 0.5 + 0.5;
      color += scanline * 0.1 * uUncertainty;
      
      // Soft edges
      float edge = smoothstep(0.0, 0.2, vUv.x) * smoothstep(1.0, 0.8, vUv.x);
      alpha *= edge;

      gl_FragColor = vec4(color, alpha * uUncertainty);
    }
  `,
};

export function UncertaintyConeScene() {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(() => {
    return {
      uTime: { value: 0 },
      uUncertainty: { value: 0.3 },
      uSurvivability: { value: 0.75 },
      uColorHigh: { value: new THREE.Color('#38bdf8') },
      uColorLow: { value: new THREE.Color('#ef4444') },
    };
  }, []);

  useFrame(({ clock }) => {
    const t = cognitionEngine().renderState.twin;
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = clock.elapsedTime;
      // Lerp for smooth transitions
      const uUnc = materialRef.current.uniforms.uUncertainty.value;
      const uSurv = materialRef.current.uniforms.uSurvivability.value;
      materialRef.current.uniforms.uUncertainty.value += (t.uncertainty - uUnc) * 0.1;
      materialRef.current.uniforms.uSurvivability.value += (t.survivability - uSurv) * 0.1;
    }
    
    if (meshRef.current) {
      // Scale and point cone based on trajectory
      const traj = t.trajectory;
      if (traj && traj.length >= 2) {
        const start = new THREE.Vector3(...traj[0]);
        const end = new THREE.Vector3(...traj[traj.length - 1]);
        const distance = start.distanceTo(end);
        
        // Transform the cylinder (cone)
        meshRef.current.position.copy(start).lerp(end, 0.5);
        meshRef.current.quaternion.setFromUnitVectors(
          new THREE.Vector3(0, 1, 0),
          end.clone().sub(start).normalize()
        );
        
        // Scale based on uncertainty
        const spread = 0.5 + t.uncertainty * 3.0;
        meshRef.current.scale.set(spread, distance, spread);
      }
    }
  });

  return (
    <group>
      <mesh ref={meshRef}>
        <cylinderGeometry args={[1.0, 0.01, 1, 32, 32, true]} />
        <shaderMaterial
          ref={materialRef}
          args={[UncertaintyConeShader]}
          transparent={true}
          side={THREE.DoubleSide}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
    </group>
  );
}