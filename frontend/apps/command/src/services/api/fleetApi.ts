import { apiClient, ApiResponse } from './client';

export interface FleetUnit {
  id: string;
  role: 'LEADER' | 'WINGMAN' | 'RESERVE';
  battery: number;
  voltage: number;
  status: 'READY' | 'ARMED' | 'EXECUTING' | 'RTL' | 'EMERGENCY';
  position: {
    lat: number;
    lon: number;
    alt_m: number;
  };
}

export interface SetModePayload {
  uavId: string;
  mode: 'OFFBOARD' | 'HOLD' | 'POSCTL' | 'RTL' | 'EMERGENCY';
}

export interface ArmPayload {
  uavId: string;
  armed: boolean;
}

export class FleetApiService {
  public static async getFleet(): Promise<ApiResponse<{ fleet_units: FleetUnit[] }>> {
    return apiClient.get<{ fleet_units: FleetUnit[] }>('/api/v1/bounded-contexts/fleet/status');
  }

  public static async setFlightMode(payload: SetModePayload): Promise<ApiResponse<{ status: string; mode: string }>> {
    return apiClient.post<{ status: string; mode: string }>('/api/v1/bounded-contexts/flight/set-mode', payload);
  }

  public static async toggleArm(payload: ArmPayload): Promise<ApiResponse<{ status: string; armed: boolean }>> {
    return apiClient.post<{ status: string; armed: boolean }>('/api/v1/bounded-contexts/flight/arm', payload);
  }

  public static async setGimbalPitch(uavId: string, pitchDeg: number): Promise<ApiResponse<{ status: string; pitch: number }>> {
    return apiClient.post<{ status: string; pitch: number }>('/api/v1/bounded-contexts/payload/gimbal', {
      uav_id: uavId,
      pitch_deg: pitchDeg,
    });
  }
}
