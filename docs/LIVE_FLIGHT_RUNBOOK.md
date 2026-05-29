# ALTARIA OS: LIVE FLIGHT DEMONSTRATION RUNBOOK

**Classification:** CONFIDENTIAL / FIELD OPERATIONS
**Objective:** Physical field demonstration of Altaria OS commanding a real Pixhawk quadcopter via Jetson Orin Edge.

## 1. PRE-FLIGHT CHECKLIST
- [ ] **Hardware:** Pixhawk 4/Cube Orange connected via TELEM2 to Jetson Orin NX (Serial `/dev/ttyACM0`).
- [ ] **Power:** Jetson powered via independent 5V BEC. Drone on 6S LiPo.
- [ ] **Network:** Jetson connected to field LTE router. Operator Toughbook connected to same VPN/Tailscale network.
- [ ] **Firmware:** Pixhawk flashed with PX4 v1.13.2+.
- [ ] **Altaria Edge:** `edge_provision.sh` executed. Docker container `altaria-kernel` running on Jetson.

## 2. COMMAND CENTER INITIALIZATION
1. Operator opens `Altaria Command Environment` in Chrome on Toughbook.
2. Select **Drone Connection Center**.
3. Select **Serial (/dev/ttyACM0)** or **TCP (Jetson IP)**.
4. Click **Initiate Connection**.
5. Verify `UPLINK SECURE`. Verify Battery, Velocity, and Altitude streams are active.

## 3. SEMANTIC MISSION PLANNING
1. Open **Semantic Copilot** ribbon.
2. Type: `"Execute industrial perimeter sweep at 30m altitude, avoid RF hotspots."`
3. Click **Execute Semantic Planning**.
4. Observe the 3D globe generate the extruded flight corridor and waypoints.
5. Review AI Survivability confidence score (Must be > 95%).
6. Approve Mission Upload.

## 4. EXECUTION & ANOMALY INJECTION
1. Drone arms and takes off.
2. **The Test:** At Waypoint 2, the field engineer wraps the Pixhawk GPS antenna in RF shielding (Faraday foil) to simulate GPS Loss.
3. **Observation:** 
   - Altaria Command Center instantly flags `GPS_DENIED`.
   - The UI renders a massive **Uncertainty Cone**.
   - The `TrustLayer` DAG updates: `PREDICT: DEGRADED`.
   - The AI evaluates Gazebo counterfactuals natively on the Jetson.
4. **Resolution:** Altaria autonomously overrides the mission, taking VISUAL_NAV_HOLD or executing an intelligent RTL using IMU dead-reckoning.

## 5. POST-FLIGHT AUDIT
1. Drone lands safely.
2. Operator clicks **Export Audit Package**.
3. Cryptographically signed `.zip` is generated containing the telemetry log, the Causality DAG, and the SORA compliance file proving Altaria saved the airframe.