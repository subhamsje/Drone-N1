import { apiClient, ApiResponse } from './client';

export interface CompileGraphPayload {
  nodes: Array<{ id: string; type: string }>;
  corridorSafetyRadiusM?: number;
}

export interface CompileGraphResponse {
  status: string;
  node_count: number;
  compiled_waypoints: Array<{
    id: string;
    lat: number;
    lon: number;
    alt_m: number;
    speed_ms: number;
  }>;
}

export interface MissionDispatchPayload {
  missionId: string;
  uavId: string;
  waypoints: any[];
}

export class MissionApiService {
  public static async compileGraph(payload: CompileGraphPayload): Promise<ApiResponse<CompileGraphResponse>> {
    return apiClient.post<CompileGraphResponse>('/api/v1/bounded-contexts/mission/compile-graph', payload);
  }

  public static async dispatchMission(payload: MissionDispatchPayload): Promise<ApiResponse<{ status: string; mission_id: string }>> {
    return apiClient.post<{ status: string; mission_id: string }>('/api/v1/bounded-contexts/flight/dispatch', payload);
  }

  public static async abortMission(uavId: string): Promise<ApiResponse<{ status: string; action: string }>> {
    return apiClient.post<{ status: string; action: string }>('/api/v1/bounded-contexts/flight/abort', { uav_id: uavId });
  }

  public static async getActiveMission(): Promise<ApiResponse<any>> {
    return apiClient.get<any>('/api/v1/bounded-contexts/mission/active');
  }
}
