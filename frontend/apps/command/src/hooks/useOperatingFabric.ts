import { useEffect } from 'react';
import { getCognitionStreamEngine, resetCognitionStreamEngine } from '@altaria/realtime-engine';
import { useOperatingStore } from '../stores/operatingStore';
import { useCognitionStore } from '../stores/cognitionStore';
import { WS_URL, UI_FLUSH_HZ } from '../config/runtime';
import { cognitionEngine } from '../config/runtime';

const API = import.meta.env.VITE_API_URL ?? '';

async function pollJson(path: string): Promise<Record<string, unknown> | null> {
  try {
    const res = await fetch(`${API}${path}`);
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

/**
 * Unified realtime fabric: WebSocket operating_state + REST platform polls.
 */
export function useOperatingFabric() {
  const applyOperating = useOperatingStore((s) => s.applyOperating);
  const applyEnvelopeFlush = useOperatingStore((s) => s.applyEnvelopeFlush);
  const setPlatform = useOperatingStore((s) => s.setPlatform);

  useEffect(() => {
    const engine = getCognitionStreamEngine(WS_URL);
    engine.stats.uiFlushHz = UI_FLUSH_HZ;

    engine.setOperatingCallback((op, stats) => {
      applyOperating(op, stats);
      useCognitionStore.getState().applyUiFlush(op.cognition, stats);
      if (op.aircraft?.geo) {
        cognitionEngine().applyLiveAircraft(
          op.aircraft.geo,
          op.aircraft.altitude_m,
          op.aircraft.heading_deg,
        );
      }
    });

    engine.setUiFlushCallback((env, stats, op) => {
      applyEnvelopeFlush(env, stats, op ?? null);
      useCognitionStore.getState().applyUiFlush(env, stats);
    });

    engine.connect();

    return () => {
      engine.setOperatingCallback(null);
      engine.setUiFlushCallback(null);
      resetCognitionStreamEngine();
    };
  }, [applyOperating, applyEnvelopeFlush]);

  useEffect(() => {
    const poll = async () => {
      const [execution, intelligence, edge, mlops] = await Promise.all([
        pollJson('/api/v1/execution/status'),
        pollJson('/api/v1/intelligence/status'),
        pollJson('/api/v1/edge/status'),
        pollJson('/api/v1/mlops/status'),
      ]);
      setPlatform({ execution: execution ?? undefined, intelligence: intelligence ?? undefined, edge: edge ?? undefined, mlops: mlops ?? undefined });

      const tel = execution?.telemetry as { lat?: number; lon?: number; alt_m?: number } | undefined;
      if (tel?.lat != null && tel?.lon != null) {
        cognitionEngine().applyLiveAircraft(
          { lat: tel.lat, lon: tel.lon },
          Number(tel.alt_m ?? 50),
        );
      }
    };
    poll();
    const t = setInterval(poll, 1000);
    return () => clearInterval(t);
  }, [setPlatform]);
}
