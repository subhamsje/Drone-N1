# Altaria Ground Command (@altaria/command) - Frontend Audit & Master Enhancement Plan

## Executive Summary

The **Altaria Ground Command** UI (`frontend/apps/command`) is an enterprise-grade 3D aerospace mission control center built on React 18, Vite, Tailwind CSS, Three.js, Cesium, and Zustand. 

To transform the interface into a deployable, high-performance, commercial-ready ground control station (GCS), this document outlines all **technical debt, performance bottlenecks, UI/UX gaps, and real-time streaming enhancements** required.

---

```
                                  +---------------------------------------+
                                  |     FRONTEND ENHANCEMENT ROADMAP      |
                                  +-------------------+-------------------+
                                                      |
         +--------------------+-----------------------+-----------------------+--------------------+
         |                    |                       |                       |                    |
         v                    v                       v                       v                    v
+------------------+ +------------------+   +-------------------+   +-------------------+ +------------------+
|   CATEGORY 1:    | |   CATEGORY 2:    |   |    CATEGORY 3:    |   |    CATEGORY 4:    | |   CATEGORY 5:    |
| Type Safety &    | | Performance &    | | Binary WebSocket    |   | HUD & 3D Radar    | | DO-178C Safety   |
| Refactoring      | | Code Splitting   |   | Data Layer        |   | Visual Polish     | | Audit Matrix     |
+------------------+ +------------------+   +-------------------+   +-------------------+ +------------------+
```

---

## 1. Category 1: TypeScript Strictness & Type Safety

### Current Gaps & Refactoring Target
Several modules in `frontend/apps/command/src` rely on implicit or explicit `any` casting, bypassing TypeScript's safety guarantees during production builds.

| File Location | Issue / Untyped Symbol | Proposed Fix |
| :--- | :--- | :--- |
| `src/command_center/panels.tsx:25` | `(active as any)?.checks` | Define `TelemetrySnapshot` & `SystemChecks` interfaces |
| `src/command_center/panels.tsx:58` | `(window as any).cesiumViewer` | Add `CesiumViewer` to global `Window` declaration in `vite-env.d.ts` |
| `src/command_center/panels.tsx:372` | `platform.edge as any` | Define `EdgePlatformMetadata` type |
| `src/mission_studio/NodeMissionGraph.tsx:36` | `useState<any \| null>(null)` | Define `CompiledResult` interface for mission graph execution |
| `src/mission_studio/NodeMissionGraph.tsx:128` | `setSubView(tab.id as any)` | Type `subView` state as `SubViewTabId` union type |

---

## 2. Category 2: Performance & Bundle Size Optimization

### Current Bundle Analysis
* **Current Bundle Size:** `1,244.10 kB` (Minified JS chunk `index-DEw10RmK.js`).
* **Warning:** Bundle exceeds Vite's 500 kB chunk warning threshold.

### Optimization Action Plan
1. **Route-Based Lazy Loading**: Split heavy 3D viewports (`Cesium`, `Three.js`, `ECharts`) using `React.lazy()` and `<Suspense>` fallbacks.
2. **Rollup Manual Chunks Configuration** (`vite.config.ts`):
   ```typescript
   export default defineConfig({
     build: {
       rollupOptions: {
         output: {
           manualChunks: {
             'three-vendor': ['three', '@react-three/fiber', '@react-three/drei'],
             'cesium-vendor': ['cesium', 'resium'],
             'chart-vendor': ['echarts', 'echarts-for-react', 'd3']
           }
         }
       }
     }
   });
   ```
3. **Asset & Texture Compression**: Compress 3D GLTF models and HUD PNG icons to WebP / Draco compressed GLTF.

---

## 3. Category 3: Binary WebSocket Data Layer (Zero-Copy Support)

### Integration with `backend/api/websocket_hub.py`
The backend now supports zero-copy binary streaming (`broadcast_bytes`). The frontend data layer must be updated to process raw binary ArrayBuffers.

### Implementation Checklist
- [ ] Update `src/services/websocketService.ts` to set `ws.binaryType = 'arraybuffer'`.
- [ ] Build a lightweight JavaScript MAVLink binary parser (`src/services/mavlinkBinaryDecoder.ts`) using `DataView`.
- [ ] Connect binary stream directly to `useTelemetryStore` Zustand state, bypassing JSON parsing overhead for 60fps HUD rendering.

---

## 4. Category 4: HUD & 3D Spatial Visualization Enhancements

### 4.1 Primary Flight Display (PFD) Artificial Horizon
- Upgrade `src/hud/PrimaryFlightDisplay.tsx` with a dynamic SVG artificial horizon:
  - Pitch ladder with $\pm 30^\circ$ elevation ticks.
  - Roll pointer and turn coordinator arc.
  - Airspeed and Altitude vertical tape scales with dynamic color-coded warnings (stall / overspeed).

### 4.2 3D Geofence & Volumetric Hazard Zones
- Upgrade `src/twin_workbench/DigitalTwinViewport.tsx` and Cesium view:
  - Render semi-transparent 3D volumetric cylinder geofences with red warning highlights on approach.
  - Render real-time wind vector particles using GPU point clouds.

---

## 5. Category 5: DO-178C Safety Audit & Real-Time Incident Matrix

### Compliance Visualizer Component (`src/certification/SafetyMatrixPanel.tsx`)
Add a dedicated DO-178C certification panel featuring:
- **Traceability Matrix Viewer**: Real-time status of DAL-A requirements vs active software partitions ($\mathcal{D}_0 - \mathcal{D}_7$).
- **Live Event Log Stream**: Filterable feed for:
  - `AFKF TAKEOVER` (VIO takeover events during GNSS spoofing).
  - `SAFETY SHIELD` (Command clamping violations).
  - `ECDSA SECURITY` (Cryptographic verification passes/fails).
  - `EDF SCHEDULER` (Latency overrun warnings).

---

## Priority Implementation Roadmap

| Priority | Task Description | Target File | Impact |
| :--- | :--- | :--- | :--- |
| **P0 (High)** | Fix TypeScript `any` types & build errors | `panels.tsx`, `NodeMissionGraph.tsx` | Code Quality & Maintainability |
| **P0 (High)** | Configure Vite Rollup manualChunks | `vite.config.ts` | 60% reduction in initial JS bundle size |
| **P1 (Med)** | Implement ArrayBuffer MAVLink decoder | `websocketService.ts`, `telemetryStore.ts` | 60fps zero-latency HUD streaming |
| **P1 (Med)** | Add PFD Pitch Ladder SVG | `PrimaryFlightDisplay.tsx` | Realistic aerospace HUD aesthetic |
| **P2 (Low)** | Add 3D Volumetric Geofence Cylinders | `DigitalTwinViewport.tsx` | 3D visual awareness |
