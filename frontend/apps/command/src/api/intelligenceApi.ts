const API = import.meta.env.VITE_API_URL ?? '';

export type MissionLifecycle = {
  mission_id: string;
  phase: string;
  intent: string;
  plan?: Record<string, unknown>;
  simulation?: Record<string, unknown>;
  validation?: { passed?: boolean };
  operator_summary?: string;
};

export async function planMission(body: {
  intent: string;
  lat: number;
  lon: number;
  alt_m?: number;
  waypoints?: Array<{ lat: number; lon: number; altM?: number }>;
}): Promise<MissionLifecycle & { operator_summary?: string }> {
  const res = await fetch(`${API}/api/v1/intelligence/missions/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`plan ${res.status}`);
  return res.json();
}

export async function advanceMission(
  missionId: string,
  phase?: string,
  operator = 'operator',
): Promise<{ success: boolean; mission: MissionLifecycle; phase_result?: unknown }> {
  const res = await fetch(`${API}/api/v1/intelligence/missions/${missionId}/advance`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phase, operator }),
  });
  if (!res.ok) throw new Error(`advance ${res.status}`);
  return res.json();
}

export async function copilotMission(message: string, lat: number, lon: number, alt_m = 100) {
  const res = await fetch(`${API}/api/v1/intelligence/copilot`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, lat, lon, alt_m }),
  });
  if (!res.ok) throw new Error(`copilot ${res.status}`);
  return res.json();
}

export async function flightStackStatus() {
  const res = await fetch(`${API}/api/v1/intelligence/status`);
  if (!res.ok) throw new Error(`status ${res.status}`);
  return res.json();
}

export async function getEnterpriseAnalytics(tenantId?: string) {
  const url = new URL(`${API}/api/v1/intelligence/analytics/enterprise`);
  if (tenantId) url.searchParams.set('tenant_id', tenantId);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`analytics ${res.status}`);
  return res.json();
}

export async function getTelemetryLakeHistory(tenantId?: string, range = '7d') {
  const url = new URL(`${API}/api/v1/intelligence/analytics/lake`);
  if (tenantId) url.searchParams.set('tenant_id', tenantId);
  url.searchParams.set('range', range);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`lake ${res.status}`);
  return res.json();
}
