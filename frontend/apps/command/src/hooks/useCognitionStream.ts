import { useEffect } from 'react';
import { getCognitionStreamEngine, resetCognitionStreamEngine } from '@altaria/realtime-engine';
import { useCognitionStore } from '../stores/cognitionStore';
import { WS_URL, UI_FLUSH_HZ } from '../config/runtime';

export function useCognitionStream() {
  const applyUiFlush = useCognitionStore((s) => s.applyUiFlush);
  const setDegraded = useCognitionStore((s) => s.setDegraded);

  useEffect(() => {
    const engine = getCognitionStreamEngine(WS_URL);
    engine.stats.uiFlushHz = UI_FLUSH_HZ;
    engine.setUiFlushCallback(applyUiFlush);
    engine.connect();

    return () => {
      engine.setUiFlushCallback(null);
      resetCognitionStreamEngine();
    };
  }, [applyUiFlush]);

  useEffect(() => {
    const onVis = () => setDegraded(document.hidden);
    document.addEventListener('visibilitychange', onVis);
    return () => document.removeEventListener('visibilitychange', onVis);
  }, [setDegraded]);
}
