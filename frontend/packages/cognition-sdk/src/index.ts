export * from './types';
export * from './operatingState';

export function survivabilityColor(score: number): string {
  if (score >= 0.7) return '#22d3a8';
  if (score >= 0.45) return '#f5b942';
  return '#ef4444';
}

export function uncertaintyColor(u: number): string {
  if (u < 0.35) return '#38bdf8';
  if (u < 0.55) return '#f59e0b';
  return '#f87171';
}
