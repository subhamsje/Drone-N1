/** Adaptive render budget — degrades quality under frame pressure (no React). */
let avgFrameMs = 16;
let degraded = false;

export function recordFrame(deltaMs: number): void {
  avgFrameMs = avgFrameMs * 0.92 + deltaMs * 0.08;
  degraded = avgFrameMs > 22;
}

export function isRenderDegraded(): boolean {
  return degraded;
}

export function averageFrameMs(): number {
  return avgFrameMs;
}
