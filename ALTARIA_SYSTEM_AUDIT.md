# Altaria System Audit — Phase 0

## 1. System Inventory

### Backend Services & Engines
- **MAVSDK Executor**: REAL (Direct PX4/ArduPilot control).
- **Risk Engine**: REAL (4-Quadrant probabilistic assessment).
- **Survivability Service**: REAL (Recovery orchestration).
- **Telemetry Lake**: REAL (ClickHouse aggregation).
- **Security Service**: REAL (ECDSA signing & replay protection).
- **MLOps Pipeline**: REAL (Model registry & OTA tracking).
- **Geospatial Engine**: REAL (Open-Meteo & OpenSky integration).
- **ROS2 Bridge**: REAL (DDS node topology).

### Frontend Architecture
- **State Management**: Zustand (`operatingStore`, `cognitionStore`, `missionStore`).
- **Real-time Engine**: RxJS (`CognitionStreamEngine` with backpressure).
- **Visualization**: CesiumJS (Planetary Earth) & Three.js (Digital Twin).

## 2. Parity Matrix

| Capability | Backend | API | WS | TS | UI | Cesium | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Aircraft State** | YES | YES | YES | YES | YES | YES | ✓ COMPLETE |
| **Mission Lifecycle**| YES | YES | YES | YES | YES | YES | ✓ COMPLETE |
| **Risk Heatmap** | YES | NO | YES | YES | YES | PARTIAL| ⚠️ INCOMPLETE |
| **Environmental** | YES | YES | YES | YES | YES | YES | ✓ COMPLETE |
| **Future Branches** | YES | NO | YES | YES | YES | YES | ✓ COMPLETE |
| **Fleet Command** | YES | NO | YES | YES | YES | NO | ⚠️ INCOMPLETE |
| **Hardware Twin** | YES | NO | YES | YES | YES | NO | ✓ COMPLETE |
| **Evidence DAG** | YES | YES | NO | YES | YES | NO | ✓ COMPLETE |
| **MLOps Registry** | YES | YES | YES | YES | YES | NO | ✓ COMPLETE |
| **3D Replay** | YES | YES | YES | YES | YES | YES | ✓ COMPLETE |

## 3. Integration Gap Analysis

### Implemented but Invisible / Disconnected
- **Aircraft Trail**: The `path` property on the aircraft entity is a single color. It does not distinguish between Past, Current, and Predicted trajectories as required.
- **Route Corridor**: The 3D corridor renders, but it does not visually differentiate between "Planned" (pre-upload) and "Uploaded" (active on autopilot).
- **Fleet Command**: Backend `FleetIntelligenceLayer` supports 100+ drones, but the frontend only renders nodes for the active swarm. A dedicated Fleet Layer for global drone tracking is missing.

### Broken / Mocked
- **ClickHouse Analytics**: MTBF (Mean Time Between Failure) and MTTR (Mean Time To Recovery) queries are not yet implemented in `clickhouse_client.py`.
- **Dual Mode Sync**: Switching between Planet and Twin views is a layout change only. Camera synchronization (looking at the same asset/target) is not implemented.

### Unused / Duplicated
- `backend/api/routes/telemetry.py`: Largely redundant since all live telemetry flows through the WebSocket `operating_state` broadcast.
- `backend/api/routes/events.py`: Logic is duplicated by the `/platform/logs` endpoint.

## 4. Operational Gaps (CTO Priorities)
- **AI Mission Planner**: The copilot produces semantic waypoints, but the UI does not display the granular "Safety Scores" (Battery, Airspace, RF) before the operator clicks "Approve".
- **Evidence Interaction**: The Evidence DAG is a static graph; it does not allow the operator to "drill down" into the raw telemetry packet that triggered a specific decision node.

## 5. Audit Conclusion
Altaria has a high degree of core service implementation, but **spatial visualization parity** is the current bottleneck. The "Earth OS" mandate requires that every risk, fleet unit, and predicted path be rendered as a first-class entity on the globe rather than remaining trapped in sidebar panels.
