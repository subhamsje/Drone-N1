# Altaria OMEGA Feature Proof Book — Phase 9

## 1. Aircraft Telemetry
- **Live Payload**: `{"uav_id": "Altaria-Alpha", "pose": {"altitude_m": 120.5, "heading_deg": 185.0}}`
- **Store State**: `operatingStore.operating.aircraft.altitude_m == 120.5`
- **UI State**: HUD bottom-left renders `ALT: 120.5m`.
- **Render Proof**: Cesium entity `cognition-aircraft` position updated via `syncCognitionLayers`.
- **Verification**: ✓ PASS

## 2. Fleet Operations
- **Live Payload**: `{"fleet": {"status": {"UAV-101": {"survivability": {"composite_survivability": 0.35}}}}}`
- **Store State**: `operatingStore.operating.fleet.status['UAV-101']` exists.
- **UI State**: `FleetCommandPanel` shows UAV-101 row with `HLTH: 35%` in red.
- **Render Proof**: `syncFleetLayer` adds cyan/orange markers for all IDs in the dictionary.
- **Verification**: ✓ PASS

## 3. Mission Corridors
- **Live Payload**: `{"plan": {"waypoints": [{"lat": 12.97, "lon": 77.59}]}}`
- **Store State**: `missionStore.waypoints` populated with 4+ points.
- **UI State**: Violet 3D corridor extruded on the map.
- **Render Proof**: `refs.adaptiveRoute` entity visible in Cesium entity list.
- **Verification**: ✓ PASS

## 4. Recovery Zones
- **Live Payload**: `{"landing_zone": {"lat": 12.972, "lon": 77.596}}`
- **Store State**: `operatingStore.operating.survivability.landing_zone.lat == 12.972`
- **UI State**: Emerald green circle labeled "EMERGENCY LZ" on terrain.
- **Render Proof**: `refs.landingZone` entity visible via `syncMissionLayers`.
- **Verification**: ✓ PASS

## 5. Risk Quadrants
- **Live Payload**: `{"risk_quadrants": {"mechanical": 0.75}}`
- **Store State**: `operatingStore.operating.survivability.risk_quadrants.mechanical == 0.75`
- **UI State**: Bright red spatial ellipse orbiting aircraft's Top-Left.
- **Render Proof**: `refs.quadrantMechanical` opacity set to 0.3 in `syncCognitionLayers`.
- **Verification**: ✓ PASS

## 6. Weather Overlays
- **Live Payload**: `{"weather": {"wind_mps": 5.1}}`
- **Store State**: `operatingStore.operating.geospatial.weather.wind_mps == 5.1`
- **UI State**: Animated cyan arrows flowing NE on the map.
- **Render Proof**: `entities.windVectors` positions updated in `envOverlays.ts`.
- **Verification**: ✓ PASS

## 7. Airspace Overlays
- **Live Payload**: `{"airspace": {"active_traffic": 78}}`
- **Store State**: `operatingStore.operating.geospatial.airspace.active_traffic == 78`
- **UI State**: Charcoal "Military Zone" visible when restriction is high.
- **Render Proof**: `entities.military.show == true` in `airspaceOverlays.ts`.
- **Verification**: ✓ PASS

## 8. Evidence DAG
- **Live Payload**: `{"reasoning_chain": ["Risk elevated to HIGH"]}`
- **Store State**: `cognitionStore.envelope.cognition.reasoning_chain` length > 0.
- **UI State**: Interactive force-graph in Evidence tab with labeled reasoning nodes.
- **Render Proof**: ECharts re-rendering triggered in `EvidenceGraph.tsx`.
- **Verification**: ✓ PASS

## 9. Command Timeline
- **Live Payload**: `[{"event_type": "mission.started"}]`
- **Store State**: `useQuery` data contains the started event.
- **UI State**: "STARTED" bullet point in Evidence sidebar.
- **Render Proof**: List mapped in `EvidenceCenterPanel`.
- **Verification**: ✓ PASS

## 10. Analytics Dashboard
- **Live Payload**: `{"mtbf_hours": 42.1}`
- **Store State**: REST query result cached in TanStack Query.
- **UI State**: "MTBF (Hours): 42.1" rendered in blurred overlay.
- **Render Proof**: `lakeQ.data` passed to `ReactECharts` options.
- **Verification**: ✓ PASS

## 11. Hardware Twin
- **Live Payload**: `{"hardware": {"motor_wear": 0.052}}`
- **Store State**: `operatingStore.operating.hardware.motor_wear == 0.052`
- **UI State**: "Motor Deg: 5.2%" in Hardware tab.
- **Render Proof**: `HardwareTwinPanel` labels updated.
- **Verification**: ✓ PASS

## 12. Sensor Twin
- **Live Payload**: `{"gps_trust": 0.95}`
- **Store State**: `cognitionStore.envelope.cognition.gps_trust == 0.95`
- **UI State**: "GPS ±5%" in tactical overlay of Digital Twin view.
- **Render Proof**: `t.gpsUncertainty` mapped in `SpatialHUD.tsx`.
- **Verification**: ✓ PASS

## 13. MLOps Dashboard
- **Live Payload**: `{"mlops": {"models": ["found-v1"]}}`
- **Store State**: `operatingStore.operating.mlops.models` count == 1.
- **UI State**: Model list showing "found-v1" in MLOps tab.
- **Render Proof**: `ModelOpsPanel` updated.
- **Verification**: ✓ PASS

## 14. Mission Replay
- **Live Payload**: `{"frame_count": 1, "frames": [...]}`
- **Store State**: `cognitionStore.replayFrames` populated.
- **UI State**: Interactive slider in footer with scrubbable timestamps.
- **Render Proof**: `ReplayTimeline` rendering in `MapNativeShell` footer.
- **Verification**: ✓ PASS
