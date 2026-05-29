# Frontend / Backend Unification

Altaria is one operating system: backend cognition flows into the command UI through a **single contract**.

## Single source of truth

WebSocket channel: **`operating_state`**

```typescript
import type { OperatingState } from '@altaria/cognition-sdk';
```

Contains: `cognition`, `aircraft`, `survivability`, `world`, `mission`, `fleet`, `geospatial`, `edge`, `flight_stack`, `recovery`, `analytics`.

REST polls (2.5s): `/execution/status`, `/intelligence/status`, `/edge/status`, `/mlops/status` — merged into `useOperatingStore.platform`.

## Command environment

| UI | Store | Backend |
|----|-------|---------|
| Altaria Command Center (left rail) | `useOperatingStore` | All subsystems |
| Planetary globe | `cognitionEngine().renderState` + `operating_state.aircraft.geo` | `operating_projection` |
| Flight Stack panel | `DroneConnectionCenter` | `/execution/*` |
| Mission lifecycle | `MissionLifecycleRail` | `/intelligence/missions/*` |
| AI Copilot ribbon | `MissionCommandRibbon` | `/intelligence/copilot` |

## Capability registry

See [`CAPABILITY_REGISTRY.md`](CAPABILITY_REGISTRY.md) for integration status per subsystem.

## Run

```bash
PYTHONPATH=. python backend/run.py
cd frontend && npm run dev --workspace=@altaria/command
```

Set `ALTARIA_HOME_LAT` / `ALTARIA_HOME_LON` for simulation NED→geo anchor. Connect PX4 SITL via Flight Stack panel (`udp://:14540`).
