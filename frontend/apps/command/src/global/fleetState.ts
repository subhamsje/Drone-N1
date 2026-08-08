import { create } from 'zustand';
import { FleetApiService, FleetUnit } from '../services/api/fleetApi';

export type FlightMode = 'OFFBOARD' | 'HOLD' | 'POSCTL' | 'RTL' | 'EMERGENCY';

export interface FleetState {
  fleetUnits: FleetUnit[];
  focusedUavId: string;
  flightMode: FlightMode;
  armed: boolean;
  gimbalPitchDeg: number;

  setFocusedUavId: (id: string) => void;
  setFlightMode: (mode: FlightMode) => Promise<void>;
  toggleArm: () => Promise<void>;
  setGimbalPitch: (pitch: number) => Promise<void>;
}

export const useFleetStore = create<FleetState>((set, get) => ({
  fleetUnits: [
    { id: 'Altaria-Alpha', role: 'LEADER', battery: 94, voltage: 15.8, status: 'READY', position: { lat: 30.2672, lon: -97.7431, alt_m: 48.5 } },
    { id: 'UAV-101', role: 'WINGMAN', battery: 91, voltage: 15.6, status: 'READY', position: { lat: 30.2680, lon: -97.7420, alt_m: 52.0 } },
    { id: 'UAV-102', role: 'WINGMAN', battery: 89, voltage: 15.4, status: 'READY', position: { lat: 30.2665, lon: -97.7445, alt_m: 45.0 } },
    { id: 'UAV-103', role: 'RESERVE', battery: 98, voltage: 16.2, status: 'READY', position: { lat: 30.2650, lon: -97.7410, alt_m: 0.0 } },
  ],
  focusedUavId: 'Altaria-Alpha',
  flightMode: 'OFFBOARD',
  armed: true,
  gimbalPitchDeg: -30,

  setFocusedUavId: (id) => set({ focusedUavId: id }),

  setFlightMode: async (mode) => {
    set({ flightMode: mode });
    const { focusedUavId } = get();
    await FleetApiService.setFlightMode({ uavId: focusedUavId, mode });
  },

  toggleArm: async () => {
    const next = !get().armed;
    set({ armed: next });
    const { focusedUavId } = get();
    await FleetApiService.toggleArm({ uavId: focusedUavId, armed: next });
  },

  setGimbalPitch: async (pitch) => {
    set({ gimbalPitchDeg: pitch });
    const { focusedUavId } = get();
    await FleetApiService.setGimbalPitch(focusedUavId, pitch);
  },
}));
