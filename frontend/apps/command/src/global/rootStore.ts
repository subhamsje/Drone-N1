import { useTelemetryStore } from './telemetryState';
import { useMissionStore } from './missionState';
import { useFleetStore } from './fleetState';
import { useUiStore } from './uiState';

export {
  useTelemetryStore,
  useMissionStore,
  useFleetStore,
  useUiStore,
};

export const useAppStore = () => ({
  telemetry: useTelemetryStore(),
  mission: useMissionStore(),
  fleet: useFleetStore(),
  ui: useUiStore(),
});
