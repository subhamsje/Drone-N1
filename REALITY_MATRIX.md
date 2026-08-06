# Altaria OMEGA Reality Matrix — Phase 1

## 1. Core Mission Inventory

| Feature | Backend Source | API Endpoint | WebSocket Topic | Store | UI Component | Interaction | Evidence Status | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Aircraft Telemetry** | `mavsdk_executor.py` | `/operating_state` | `operating_state` | `operatingStore` | `PlanetaryGlobe` | Select drone | [UNVERIFIED] | NO |
| **Fleet Operations** | `fleet_intel.py` | `/operating_state` | `fleet` | `operatingStore` | `FleetCommandPanel`| Filter status | [UNVERIFIED] | NO |
| **Mission Planning** | `semantic_planner.py`| `/missions/plan` | `operating_state` | `missionStore` | `MissionCommandPanel`| Submit intent | [UNVERIFIED] | NO |
| **Waypoints** | `lifecycle.py` | `/missions/plan` | `operating_state` | `missionStore` | `MissionCommandPanel`| Click WP | [UNVERIFIED] | NO |
| **Recovery Zones** | `survival.py` | `/operating_state` | `survival` | `operatingStore` | `syncMissionLayers` | Auto-render | [UNVERIFIED] | NO |
| **Risk Quadrants** | `engines/risk.py` | `/operating_state` | `survivability` | `operatingStore` | `syncCognitionLayers`| Auto-render | [UNVERIFIED] | NO |
| **Weather Overlays** | `real_world_intel.py`| `/geospatial` | `geospatial` | `operatingStore` | `envOverlays` | Auto-render | [UNVERIFIED] | NO |
| **Airspace Overlays** | `real_world_intel.py`| `/geospatial` | `geospatial` | `operatingStore` | `airspaceOverlays` | Auto-render | [UNVERIFIED] | NO |
| **Evidence DAG** | `explainability.py` | `/platform/logs` | `cognition` | `cognitionStore` | `EvidenceGraph` | Hover nodes | [UNVERIFIED] | NO |
| **Command Timeline** | `bus.py` | `/platform/logs` | `operating_state` | `operatingStore` | `EvidenceCenter` | Scroll logs | [UNVERIFIED] | NO |
| **Analytics Dash** | `clickhouse_client.py`| `/analytics` | N/A | `operatingStore` | `LakeOverlay` | Switch tenant | [UNVERIFIED] | NO |
| **Hardware Twin** | `hardware_cog.py` | `/operating_state` | `hardware` | `operatingStore` | `HardwarePanel` | Auto-render | [UNVERIFIED] | NO |
| **Sensor Twin** | `sensor_trust.py` | `/operating_state` | `cognition` | `cognitionStore` | `SpatialHUD` | Auto-render | [UNVERIFIED] | NO |
| **MLOps Dashboard** | `mlops/pipeline.py` | `/operating_state` | `mlops` | `operatingStore` | `ModelOpsPanel` | View rollout | [UNVERIFIED] | NO |
| **Mission Corridors** | `semantic_planner.py`| `/missions/plan` | `operating_state` | `missionStore` | `syncMissionLayers`| Auto-render | [UNVERIFIED] | NO |
| **Emergency Logic** | `survival.py` | `/operating_state` | `survival` | `operatingStore` | `SpatialHUD` | Trigger recovery| [UNVERIFIED] | NO |
| **Digital Twin** | `twin_bridge.py` | `/operating_state` | `world_model` | `cognitionStore` | `CognitiveTwin` | Orbit camera | [UNVERIFIED] | NO |
| **Dual Mode** | `app.py` | `/operating_state` | N/A | `cognitionStore` | `MapNativeShell` | Toggle Dual | [UNVERIFIED] | NO |

## 2. Integrity Warnings (Stubs/Mocks Detected)
- **Triton Client**: `backend/inference/gateway.py` contains a "routing stub".
- **Kafka Adapter**: `backend/events/bus.py` contains a "publish stub".
- **ROS2 Failure Handler**: `backend/ros2_bridge/node.py` logs "No mock data will be generated" if ROS2 is missing.

## 3. Succes Criteria Phase 1
- [x] Filesystem audit complete.
- [x] Directory structure validated.
- [x] Reality Matrix initialized with [UNVERIFIED] state.
- [x] Potential mocks identified.

**Next Step**: Phase 2 — API Verification (Proving every endpoint returns real data).
