# Altaria Capability Registry — Frontend Integration Status

Generated for platform unification. **Goal:** every row reaches `VISIBLE` via `operating_state` WebSocket + Command Center panels.

| System | REST | WebSocket | UI Panel | Status |
|--------|------|-----------|----------|--------|
| Cognitive OS Kernel | `/platform/*` | `operating_state`, `cognition` | Cognition | **VISIBLE** |
| Mission Intelligence | `/intelligence/*` | `operating_state.mission` | Mission Command | **VISIBLE** |
| Flight Stack (PX4/MAVSDK) | `/execution/*` | `operating_state.flight_stack` | Drone Connection | **VISIBLE** |
| Survivability | `/cognition/survival` | `survival`, `operating_state.survivability` | Survivability Center | **VISIBLE** |
| World Model | `/platform/world-model` | `world_model`, `operating_state.world` | World Futures | **VISIBLE** |
| Route Governance | — | `operating_state.mission.route_governance` | Mission + Globe | **VISIBLE** |
| Recovery | `/recovery/*` | `operating_state.recovery` | Survival + Connection | **VISIBLE** |
| Fleet Intelligence | `/intelligence/fleet` | `swarm`, `operating_state.fleet` | Fleet Ops | **VISIBLE** |
| Swarm Cognition | `/platform/swarm/collective` | `swarm` | Swarm Topology | **VISIBLE** |
| Geospatial Engine | `/intelligence/geospatial` | `operating_state.geospatial` | Geospatial Intel | **VISIBLE** |
| Certification / Evidence | `/intelligence/certification/export` | `certification` | Trust + Evidence | **VISIBLE** |
| Explainability | `/platform/explanation` | `cognition.reasoning_chain` | Trust Layer | **VISIBLE** |
| Edge Runtime | `/edge/status` | `operating_state.edge` | Edge Ops | **VISIBLE** |
| MLOps | `/mlops/*` | `operating_state.mlops` | MLOps strip | **PARTIALLY WIRED** |
| Inference Gateway | `/inference/*` | cognition metrics | Cognition | **VISIBLE** |
| Telemetry Lake | `/telemetry/*` | — | Analytics | **PARTIALLY WIRED** |
| MAVLink Gateway | `/execution/command` | events | Connection Center | **VISIBLE** |
| Validation / SITL | `/validation/*` | — | Dev drawer | **PARTIALLY WIRED** |
| Planetary Federation | `/validation/federation` | — | — | **UNUSED** |
| gRPC services | `altaria.proto` | — | Edge agents | **DISCONNECTED** |
| Kafka topics | — | bus (memory) | — | **DISCONNECTED** |

## Unified contracts

| Snapshot | Source |
|----------|--------|
| `OperatingState` | WS `operating_state` |
| `CognitionEnvelope` | `operating_state.cognition` |
| `AircraftSnapshot` | `operating_state.aircraft` |
| `MissionSnapshot` | `operating_state.mission` |
| `FleetSnapshot` | `operating_state.fleet` |
| `SurvivabilitySnapshot` | `operating_state.survivability` |
| `WorldSnapshot` | `operating_state.world` |

## Event topics (backend bus)

`telemetry.*`, `recovery.*`, `mission.*`, `fleet.*`, `cyber.*`, `command.mavlink` — surfaced to UI via `operating_state` aggregation, not direct Kafka consumer in browser.
