# Altaria OS — API Reference (v1.0.0)

## Base Endpoints: `http://localhost:8080/api/v1`

### 1. Mission Management
*   `POST /intelligence/missions/plan`: Generates a semantic mission package.
    *   *Payload*: `{ "intent": "Survey area", "lat": 12.9, "lon": 77.5 }`
*   `POST /intelligence/missions/{mission_id}/advance`: Advances the mission state machine.
    *   *Transitions*: `plan -> validate -> approve -> upload -> execute -> learn`.
*   `GET /intelligence/missions/{mission_id}/export`: Returns a QGC-compatible `.plan` file.

### 2. Live Execution
*   `POST /execution/command`: Dispatches low-level instructions to MAVSDK.
    *   *Commands*: `ARM`, `DISARM`, `TAKEOFF`, `LAND`, `RTL`, `HOLD`, `GOTO`.
*   `GET /execution/status`: Returns current flight stack connectivity and autopilot mode.

### 3. Intelligence & Geospatial
*   `GET /intelligence/geospatial`: Retrieves live environmental context (METAR, ADS-B).
*   `GET /intelligence/status`: Kernel health and cognitive cycle metrics.

### 4. Analytics & Telemetry Lake
*   `GET /intelligence/analytics/enterprise`: Returns executive KPIs from ClickHouse.
*   `GET /intelligence/analytics/lake`: Streams historical telemetry windows for replay.

### 5. Platform & Edge
*   `GET /platform/status`: Edge runtime, ROS2 bridge, and Gazebo simulator state.
*   `GET /platform/logs`: Sequential system event history from the internal bus.
