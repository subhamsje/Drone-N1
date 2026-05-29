# Altaria Intelligence Architecture

**Principle:** ArduPilot / PX4 control **how** to fly. Altaria controls **why, where, when, and whether** to fly.

Altaria does **not** replace MAVLink, MAVSDK, Mission Planner, Gazebo, MAVProxy, or autopilot firmware. It is the **mission intelligence layer** above them.

---

## Layer Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│  OPERATIONAL COMMAND ENVIRONMENT (React + Cesium + Cognition Runtime)   │
│  Plan · Simulate · Approve · Monitor · Replay · Copilot                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│  ALTARIA INTELLIGENCE PLATFORM (this document)                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │ Semantic     │ │ Predictive   │ │ Survivability│ │ Fleet            │ │
│  │ Mission      │ │ World Model  │ │ Engine       │ │ Intelligence     │ │
│  │ Planning     │ │              │ │              │ │                  │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │ Planetary    │ │ AI Copilot   │ │ Certification│ │ Operational      │ │
│  │ Geospatial   │ │              │ │ Evidence     │ │ Analytics        │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │ Mission Lifecycle Orchestrator (Plan→…→Learn)                       │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│  COGNITIVE OS KERNEL (altaria_os/kernel.py)                               │
│  Sensor trust · Inference · Survival · Route governance · Evidence DAG  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│  FLIGHT STACK ADAPTER (backend/intelligence/flight_stack)               │
│  Telemetry ingest · Command egress · Safety envelope · Audit              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────┐
│  PROVEN INFRASTRUCTURE (do not replace)                                   │
│  PX4 · ArduPilot · Pixhawk · MAVLink · MAVSDK · Gazebo · SITL · HITL      │
│  Mission Planner · MAVProxy                                                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Ten Intelligence Systems

| # | System | Module | Responsibility |
|---|--------|--------|----------------|
| 1 | Planetary Geospatial Engine | `backend/intelligence/geospatial/` | Cesium-facing layers: terrain, imagery, weather, airspace, RF, infrastructure |
| 2 | Semantic Mission Planning | `backend/intelligence/mission/semantic_planner.py` | Intent → plan, route, contingencies, recovery |
| 3 | Predictive World Model | `engines/predictive_world_model.py` + lifecycle simulate | Pre-execution futures |
| 4 | Survivability Engine | `engines/survival.py`, `altaria_os/safety/` | Crash P, continuity, landing/recovery P, emergency actions |
| 5 | Fleet Intelligence | `backend/intelligence/fleet_intel.py` | 1→1000 UAV scaling, shared memory, threat propagation |
| 6 | Digital Twin Infrastructure | `backend/intelligence/twin_bridge.py` | Gazebo/SITL/HITL fault injection hooks |
| 7 | Operational Command Environment | `frontend/apps/command` | Map-native mission command |
| 8 | AI Copilot | `backend/intelligence/mission/copilot.py` | NL → full mission package |
| 9 | Operational Analytics | `backend/intelligence/analytics.py` | Flight hours, failure rates, readiness |
| 10 | Certification Infrastructure | `backend/intelligence/certification.py` | Audit trail, evidence graph, lineage |

---

## Mission Lifecycle (single workflow object)

| Phase | Altaria action | Autopilot action |
|-------|----------------|------------------|
| **Plan** | Parse intent, generate route + contingencies | — |
| **Simulate** | World model futures, survivability forecast | — |
| **Validate** | Airspace, battery, risk gates | — |
| **Approve** | Human operator + audit record | — |
| **Upload** | Translate plan → MAVSDK mission / goto sequence | Receives mission |
| **Execute** | Monitor cognition, authorize overrides | Flies waypoints |
| **Monitor** | WS cognition stream, globe position | Telemetry |
| **Adapt** | Route governance reroute | Executes new setpoints |
| **Recover** | Survival → recovery service → RTL/LAND | Executes RTL/LAND |
| **Replay** | Mission cognition replay + evidence DAG | — |
| **Learn** | Telemetry lake + fleet meta-learning | — |

API: `POST /api/v1/intelligence/missions/{id}/advance?phase=simulate`

---

## Flight Stack Adapter

- **PX4 / ArduPilot:** via MAVSDK (`MAVSDKExecutor`) and MAVLink gateway (`backend/mavlink/`)
- **SITL:** `udp://:14540` (PX4) or `udp:127.0.0.1:14550` (MAVProxy classic)
- **HITL / LIVE:** serial or companion UDP
- **Gazebo:** twin bridge injects wind/spoof/failures into simulation snapshot path

Commands pass through **safety envelope** before `execute()`.

---

## Data Flow (live aircraft)

```
Aircraft MAVLink → MAVLinkGateway → normalized telemetry → CognitiveBridge
                                                      ↓
                                            OS Kernel process()
                                                      ↓
                                            cognition_projection → WebSocket
                                                      ↓
                                            Cesium globe + twin

Operator approve → MissionLifecycle.upload() → FlightStackAdapter.upload_mission()
                                                      ↓
                                            MAVSDK mission / goto (PX4/ArduPilot)
```

---

## Degradation Matrix

| Failure | Altaria response |
|---------|------------------|
| Telemetry loss | Sensor trust decay; hold/RTL recommendation |
| GPS spoofing | Cyber engines; GPS-denied nav; abort upload |
| RF degradation | Comm trust; degraded autonomy mode |
| Backend outage | Edge buffer + local envelope (edge agent roadmap) |
| Cloud outage | Edge continues monitor; sync on restore |

---

## Success Criteria Mapping

| # | Criterion | Implementation |
|---|-----------|----------------|
| 1 | Open Altaria | `frontend/apps/command` |
| 2 | Real Earth | Cesium OSM + optional Ion |
| 3 | Connect drone | `POST /execution/command` CONNECT + flight stack status |
| 4 | Mission intent | Copilot + semantic planner |
| 5 | AI plan | `POST /intelligence/missions/plan` |
| 6 | Simulate futures | `phase=simulate` |
| 7 | Upload mission | `phase=upload` → MAVSDK |
| 8 | Execute | `phase=execute` |
| 9 | Observe cognition | WS `/ws/v1/stream` |
| 10 | Recover | survival + recovery service |
| 11 | Replay | mission_replay + UI timeline |
| 12 | Learn | telemetry lake ingest |

---

## What We Do Not Build

- Autopilot firmware
- Low-level attitude controllers
- MAVLink protocol replacements
- Gazebo physics engine
- Mission Planner UI clone

---

## Implementation Status

| Component | Status |
|-----------|--------|
| Intelligence package + lifecycle API | **Implemented (v1)** |
| Flight stack CONNECT | **Implemented (v1)** |
| Geospatial providers (weather/airspace) | **Interface + stub** |
| Full QGC .plan upload | **Roadmap** |
| Postgres mission persistence | **Roadmap** |
| Edge autonomy on partition | **Roadmap** |

See `backend/intelligence/` and `POST /api/v1/intelligence/*`.
