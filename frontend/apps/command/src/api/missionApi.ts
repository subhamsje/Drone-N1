import type { SemanticConstraints } from '../stores/missionStore';

const API = import.meta.env.VITE_API_URL ?? '';

export async function submitSemanticIntent(intent: string): Promise<{
  intent: string;
  constraints: SemanticConstraints;
}> {
  const res = await fetch(`${API}/api/v1/cognition/mission-intent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ intent }),
  });
  if (!res.ok) throw new Error(`mission-intent ${res.status}`);
  return res.json();
}

export async function createMission(body: {
  name: string;
  intent: string;
  objectives?: string[];
}): Promise<Record<string, unknown>> {
  const res = await fetch(`${API}/api/v1/missions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...body, fleet_id: 'swarm-alpha-1', uav_ids: ['Altaria-Alpha'] }),
  });
  if (!res.ok) throw new Error(`create mission ${res.status}`);
  return res.json();
}
