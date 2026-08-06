# Altaria OS — Frontend/Backend Matrix

| Phase | Capability | Backend Service | API / Stream | Frontend Component |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Photoreal Earth | Geospatial Engine | `/intelligence/geospatial` | `PlanetaryCognitionGlobe` |
| **2** | Live Aircraft | Aircraft Service | WebSocket: `operating_state` | `AircraftLayer` / HUD |
| **3** | Mission Viz | Mission Projection | `/missions/{id}` | `MissionLayer` |
| **4** | Airspace | Airspace Service | `/geospatial` | `AirspaceLayer` |
| **5** | Weather | Weather Intel | `/geospatial` | `WeatherLayer` |
| **6/7**| Risk/Survivability | Risk Engine | WebSocket: `survivability` | `RiskHeatmapLayer` |
| **8** | Futures | Counterfactual Engine| WebSocket: `world_model` | `FutureBranchesLayer` |
| **9** | Evidence DAG | Evidence Engine | `/platform/logs` | `EvidenceGraph` |
| **10** | Fleet Command | Fleet Service | WebSocket: `fleet` | `FleetLayer` |
| **11** | Hardware | Hardware Cognition | WebSocket: `hardware` | `HardwareTwinPanel` |
| **13** | Mission Replay | Replay Engine | WebSocket: `replay` | `ReplayEnvironment` |
| **14** | AI Copilot | Mission Copilot | `/missions/plan` | `MissionCommandRibbon` |
| **16** | Telemetry Lake | ClickHouse Client | `/analytics/enterprise` | `AnalyticsCenter` |
| **18** | Security | Security Service | `/platform/logs` | `SecurityCenterPanel` |
| **19** | Observability | Health Service | `/platform/status` | `ObservabilityPanel` |
