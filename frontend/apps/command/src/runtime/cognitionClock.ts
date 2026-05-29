/** Shared operational timebase for tactical motion (no React rerenders). */
let elapsed = 0;

export function advanceCognitionClock(delta: number): void {
  elapsed += delta;
}

export function cognitionTime(): number {
  return elapsed;
}

export function cognitionPulse(freq = 1.2): number {
  return 0.5 + 0.5 * Math.sin(elapsed * Math.PI * 2 * freq);
}

export function cognitionBreath(freq = 0.35): number {
  return 0.5 + 0.5 * Math.sin(elapsed * Math.PI * 2 * freq);
}
