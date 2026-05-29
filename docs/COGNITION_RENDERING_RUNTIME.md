# Cognition Rendering Runtime

The Altaria command frontend is a **realtime cognition rendering engine**, not a telemetry dashboard.

## Architecture

| Layer | Responsibility |
|-------|----------------|
| `CognitionStreamEngine` | WebSocket ingest, survivability-first priority, 12Hz UI flush, rich `renderState` (branches, futures, threats) |
| `cognitionStore` (Zustand) | Throttled UI snapshot for panels only |
| `WorldFuturesEngine` (R3F) | Spatial predictive cognition — route cones, crash paths, survivability shells, landing outcomes |
| `EnvironmentalWorld` (R3F) | Urban terrain, clouds, towers, landing zones, congestion heat |
| `OperationalCamera` (R3F) | Threat/recovery/uncertainty framing (damped OrbitControls) |
| `UncertaintyFog` (R3F) | Probabilistic uncertainty volume (pulse/breathe) |
| Cesium (`PlanetaryGlobe`) | Single `Viewer`, airspace overlays, imperative entity updates |
| `renderScheduler` | Frame budget → adaptive degraded DPR |
| `RenderErrorBoundary` | Per-domain degraded mode + manual recovery |

## Stream priority

1. survivability / cognition  
2. pose (embedded in cognition)  
3. recovery / survival  
4. trust  
5. world / airspace  
6. swarm  
7. analytics (hardware, adversarial, certification)

## Configuration

- Dev WebSocket: `ws://127.0.0.1:8080/ws/v1/stream` (bypasses Vite proxy EPIPE)
- `VITE_WS_URL` — override WS endpoint
- `VITE_UI_FLUSH_HZ` — panel update rate (default 12)

## Run

```bash
cd frontend && npm install
PYTHONPATH=. python backend/run.py   # :8080
npm run dev --workspace=@altaria/command   # :5173
```
