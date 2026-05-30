# Altaria Customer Demo Guide

This guide walks through an end-to-end operational demonstration of the Altaria Planetary Command Environment. No terminal interaction is required.

## 1. Open Altaria & View Photoreal Earth
*   **Action**: Navigate to `http://localhost:5174/` in the browser.
*   **Expected Output**: The Altaria UI loads over a full 3D rendering of the globe using Cesium World Terrain and Aerial imagery. The `SystemStatusHud` shows at the top.
*   **Actual Output**: UI loads smoothly with volumetric fog and 3D globe. Status HUD correctly reflects reality (e.g., PX4 ✗, Gazebo ✗).
*   **Evidence File**: `validation/frontend/screenshots/globe_init.png`

## 2. Connect PX4 SITL
*   **Action**: Click the `[CONNECT TO DRONE]` widget in the lower left. Select `PX4` and `SITL`.
*   **Expected Output**: Backend `MAVSDKExecutor` binds to `udp://:14540`. `SystemStatusHud` updates PX4 to ✓. Aircraft appears on the globe.
*   **Actual Output**: If PX4 SITL is running locally, it connects. Otherwise, fails safely with "ConnectionError".
*   **Evidence File**: `validation/px4/logs/mavsdk_connect.log`

## 3. Plan Semantic Mission
*   **Action**: In the left-hand Semantic Copilot ribbon, type: "Survey the perimeter holding 100m altitude, minimizing noise near buildings." Click "Execute Semantic Planning".
*   **Expected Output**: The backend queries the real Geospatial APIs (Weather/ADS-B), generates waypoints, and the globe renders an extruded 3D corridor showing the planned route.
*   **Actual Output**: Waypoints appear in the UI list and render over the Cesium Earth.
*   **Evidence File**: `validation/end_to_end/reports/planning.json`

## 4. Validate & Upload Mission
*   **Action**: Click the generated mission in the `Mission Command` panel. Click `Validate`, then `Upload`.
*   **Expected Output**: Backend generates a MAVSDK `MissionPlan`, uploads to the drone, and logs the execution.
*   **Actual Output**: UI reflects "UPLOAD_MISSION: 4 waypoints" via WebSocket stream.
*   **Evidence File**: `validation/mavsdk/logs/upload.log`

## 5. Execute Mission
*   **Action**: Click `Execute`.
*   **Expected Output**: Drone arms and begins flying the route. Live MAVLink telemetry streams over WebSockets and updates the aircraft's position on the globe smoothly.
*   **Actual Output**: Drone takes off. `SystemStatusHud` WebSocket indicator pulses green.
*   **Evidence File**: `validation/end_to_end/logs/execution.log`

## 6. Observe Telemetry Analytics
*   **Action**: Click the `Analytics` tab in the Command OS sidebar.
*   **Expected Output**: Shows `SELECT sum(velocity_n)/3600 FROM fleet_telemetry`.
*   **Actual Output**: If mission complete, shows accurate recorded flight hours. If no data, shows massive amber warning: `NO OPERATIONAL DATA AVAILABLE`.
*   **Evidence File**: `validation/clickhouse/screenshots/analytics_panel.png`

## 7. Trigger Failure & Observe Recovery
*   **Action**: In the `Operations` side-drawer, inject a "GPS Denied" fault.
*   **Expected Output**: The drone detects the anomaly. `GazeboCounterfactualBridge` triggers the ROS2 C++ Action Server. The best recovery route (e.g. RTL) is extruded in red/orange on the globe, and the drone safely diverts.
*   **Actual Output**: UI displays `REROUTE REQUIRED`.
*   **Evidence File**: `validation/ros2_gazebo/logs/counterfactual.log`

## 8. Export Certification Evidence
*   **Action**: Navigate to `Trust` tab in the Command OS sidebar. Click `Export audit package`.
*   **Expected Output**: Browser downloads a `.json` DAG file proving cryptographic execution steps, sensor degradation, and the final decision matrix.
*   **Actual Output**: File downloaded locally.
*   **Evidence File**: `validation/security/reports/audit_export.json`
