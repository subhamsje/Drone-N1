import { getCognitionStreamEngine, type CognitionStreamEngine } from '@altaria/realtime-engine';

export const WS_URL =
  import.meta.env.VITE_WS_URL ??
  (import.meta.env.DEV
    ? 'ws://127.0.0.1:8080/ws/v1/stream'
    : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/v1/stream`);

export const UI_FLUSH_HZ = Number(import.meta.env.VITE_UI_FLUSH_HZ ?? 12);

export function cognitionEngine(): CognitionStreamEngine {
  return getCognitionStreamEngine(WS_URL);
}
