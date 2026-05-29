# Altaria Cognition Command Environment

The operational consciousness layer of Altaria OS — not a telemetry dashboard.

## Stack

| Layer | Technology |
|-------|------------|
| App | React 18, TypeScript, Vite |
| State | Zustand, TanStack Query |
| Realtime | WebSocket cognition channels, RxJS |
| 3D / Geo | Three.js, R3F, Cesium (resium) |
| Charts | ECharts, D3-ready |
| UI | Tailwind, tactical panels |

## Monorepo

```
frontend/
├── apps/command/          # Cognition command environment
├── packages/
│   ├── cognition-sdk/     # Types + color semantics
│   ├── realtime-engine/   # WS cognition stream client
│   └── ui/                # Aerospace-grade panels
```

## Backend integration

- `backend/api/cognition_projection.py` — projects OS snapshots to cognition envelopes
- WebSocket `/ws/v1/stream` — subscribe: `{"subscribe":["cognition","survival","world_model",...]}`

## Run

```bash
# Terminal 1 — backend with cognitive loop
cd /Users/subham/code/N1
PYTHONPATH=. python backend/run.py

# Terminal 2 — command environment
cd frontend
npm install
npm run dev --workspace=@altaria/command
```

Open http://localhost:5173

## Core views

1. **Live Cognitive Digital Twin** — R3F aircraft, thrust vectors, turbulence, future trajectory
2. **Planetary Globe** — Cesium corridors, congestion, entity track
3. **Cognition Panel** — survivability, uncertainty, reasoning chain
4. **World Model Futures** — generative survivability, consequence bars
5. **Survival / Adversarial / Hardware / Swarm / Trust / Evidence DAG**
6. **Mission Replay Timeline** — survivability over time

## Positioning

Visualizes **cognition under uncertainty** — predictive, not reactive.
