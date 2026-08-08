# Altaria OS — Unified API Reference Manual

Complete REST, WebSocket, and gRPC endpoints exposed across the 16 Domain-Driven Bounded Contexts.

---

## 📡 REST API Endpoints (`http://localhost:8080/api/v1/*`)

### 1. Sovereign Cognitive Kernel
- `GET /api/v1/intelligence/reasoning-tree`: Returns XAI Cause-and-Effect decision trees, candidate trajectory evaluations, sensor trust matrix, and global confidence percentages.
- `GET /api/v1/intelligence/learning/experiences`: Returns certified offline model retraining pipeline status.

### 2. Multi-Domain Robotics
- `GET /api/v1/bounded-contexts/robotics/vehicles`: Returns active multi-domain vehicle state (`UAV`, `VTOL`, `UGV`, `USV`, `Robot Arm`).
- `POST /api/v1/bounded-contexts/robotics/command`: Dispatches domain-specific hardware commands (`DRIVE_VELOCITY`, `TRANSITION_FLIGHT_MODE`, `CONTROL_THRUST`).

### 3. Enterprise Security & Compliance
- `POST /api/v1/bounded-contexts/security/sign-command`: Cryptographically signs commands using ECDSA NIST256p.
- `GET /api/v1/bounded-contexts/security/audit-package`: Generates formal FAA Part 107 / EASA BVLOS compliance audit package.
- `GET /api/v1/bounded-contexts/security/soc-status`: Returns real-time DEFCON cybersecurity and RF threat metrics.

### 4. Adversarial Simulation Sandbox
- `POST /api/v1/bounded-contexts/simulation/inject-fault`: Injects live physical anomalies (`GPS_JAMMING`, `MOTOR_RAMP`, `WIND_BURST`, `BATTERY_SAG`).
- `POST /api/v1/bounded-contexts/simulation/clear-faults`: Clears active anomaly states.

### 5. Operational Knowledge Graph & Analytics
- `POST /api/v1/bounded-contexts/knowledge/search`: Natural language query search over 1,420+ historical mission experiences.
- `GET /api/v1/bounded-contexts/analytics/economics`: Returns itemized mission costs and financial ROI multiplier.
- `POST /api/v1/bounded-contexts/mission/compile-graph`: Compiles visual node blueprints into executable MAVSDK waypoints.

---

## ⚡ Realtime WebSocket Stream (`ws://localhost:8080/ws/v1/stream`)
Streams 12Hz RxJS-throttled 20D state vectors, spatial uncertainty cones, and active recovery envelopes to the WebGL command surface.
