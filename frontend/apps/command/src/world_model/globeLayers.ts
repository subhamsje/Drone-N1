import {
  Cartesian3,
  Color,
  Entity,
  Math as CesiumMath,
  Viewer as CesiumViewer,
  HeightReference,
} from 'cesium';
import type { FutureBranch } from '@altaria/realtime-engine';
import type { CognitionRenderState } from '@altaria/realtime-engine';
import type { GeoFence, GeoWaypoint } from '../stores/missionStore';
import { initAirspaceOverlays, syncAirspaceOverlays, type AirspaceEntities } from './airspaceOverlays';
import { initEnvironmentalOverlays, syncEnvironmentalOverlays, type EnvironmentEntities } from './environmentalOverlays';
import { useOperatingStore } from '../stores/operatingStore';

export type GlobeLayerRefs = {
  aircraft?: Entity;
  pastTrail?: Entity;
  predictedTrail?: Entity;
  adaptiveRoute?: Entity;
  governanceRoute?: Entity;
  takeoffPoint?: Entity;
  landingZone?: Entity;
  recoveryRoute?: Entity;
  riskField?: Entity;
  quadrantMechanical?: Entity;
  quadrantSensor?: Entity;
  quadrantComms?: Entity;
  quadrantAI?: Entity;
  futureBranches: Entity[];
  waypoints: Entity[];
  geofences: Entity[];
  swarmNodes: Entity[];
  swarmLinks: Entity[];
  fleetDrones: Map<string, Entity>;
  airspace: AirspaceEntities;
  environment: EnvironmentEntities;
};

export function initGlobeLayers(viewer: CesiumViewer): GlobeLayerRefs {
  return {
    futureBranches: [],
    waypoints: [],
    geofences: [],
    swarmNodes: [],
    swarmLinks: [],
    fleetDrones: new Map(),
    airspace: initAirspaceOverlays(viewer),
    environment: initEnvironmentalOverlays(viewer),
  };
}

function branchToGlobePoints(
  originLon: number,
  originLat: number,
  altM: number,
  branch: FutureBranch,
): Cartesian3[] {
  const alt = altM + 6378137;
  return branch.points.map(([x, y, z], i) => {
    const scale = 0.00015; // Increased scale for globe visibility
    return Cartesian3.fromDegrees(
      originLon + x * scale * (1 + i * 0.1),
      originLat + z * scale * (1 + i * 0.1),
      alt + y * 12,
    );
  });
}

export function syncCognitionLayers(
  viewer: CesiumViewer,
  refs: GlobeLayerRefs,
  state: CognitionRenderState,
  rerouteRequired: boolean,
): void {
  const g = state.globe;
  const t = state.twin;
  const alt = g.altM + 6378137;
  const pos = Cartesian3.fromDegrees(g.lon, g.lat, alt);
  const survivability = useOperatingStore.getState().operating?.survivability;
  const quadrants = survivability?.risk_quadrants;

  // 4-Quadrant Risk Field (Phase 6 & 7)
  if (!refs.riskField) {
    refs.riskField = viewer.entities.add({
      id: 'planetary-risk-field',
      ellipse: {
        semiMajorAxis: 5000,
        semiMinorAxis: 5000,
        material: Color.fromCssColorString('#f43f5e').withAlpha(0.05),
        outline: true,
        outlineColor: Color.fromCssColorString('#f43f5e').withAlpha(0.2),
        height: 5,
      }
    });

    // Sub-quadrants for mechanical, sensor, comms, ai
    const quadSize = 2500;
    refs.quadrantMechanical = viewer.entities.add({
      id: 'risk-mech',
      ellipse: { semiMajorAxis: quadSize, semiMinorAxis: quadSize, material: Color.RED.withAlpha(0.1) }
    });
    refs.quadrantSensor = viewer.entities.add({
      id: 'risk-sensor',
      ellipse: { semiMajorAxis: quadSize, semiMinorAxis: quadSize, material: Color.YELLOW.withAlpha(0.1) }
    });
    refs.quadrantComms = viewer.entities.add({
      id: 'risk-comms',
      ellipse: { semiMajorAxis: quadSize, semiMinorAxis: quadSize, material: Color.BLUE.withAlpha(0.1) }
    });
    refs.quadrantAI = viewer.entities.add({
      id: 'risk-ai',
      ellipse: { semiMajorAxis: quadSize, semiMinorAxis: quadSize, material: Color.PURPLE.withAlpha(0.1) }
    });
  }

  if (refs.riskField.ellipse && quadrants) {
    (refs.riskField as any).position = pos;
    const risk = state.globe.conflictRisk;
    (refs.riskField.ellipse.material as any).color = Color.fromCssColorString(
      risk > 0.6 ? '#f43f5e' : risk > 0.3 ? '#f59e0b' : '#10b981'
    ).withAlpha(0.1 + risk * 0.2);

    // Position quadrants around aircraft
    const offset = 0.02;
    (refs.quadrantMechanical as any).position = Cartesian3.fromDegrees(g.lon - offset, g.lat + offset, alt);
    (refs.quadrantSensor as any).position = Cartesian3.fromDegrees(g.lon + offset, g.lat + offset, alt);
    (refs.quadrantComms as any).position = Cartesian3.fromDegrees(g.lon - offset, g.lat - offset, alt);
    (refs.quadrantAI as any).position = Cartesian3.fromDegrees(g.lon + offset, g.lat - offset, alt);

    (refs.quadrantMechanical?.ellipse?.material as any).color = Color.RED.withAlpha(quadrants.mechanical * 0.4);
    (refs.quadrantSensor?.ellipse?.material as any).color = Color.YELLOW.withAlpha(quadrants.sensor * 0.4);
    (refs.quadrantComms?.ellipse?.material as any).color = Color.BLUE.withAlpha(quadrants.comms * 0.4);
    (refs.quadrantAI?.ellipse?.material as any).color = Color.PURPLE.withAlpha(quadrants.ai * 0.4);
  }

  if (!refs.aircraft) {
    refs.aircraft = viewer.entities.add({
      id: 'cognition-aircraft',
      position: pos,
      point: {
        pixelSize: 22,
        color: Color.fromCssColorString('#22d3a8'),
        outlineColor: Color.WHITE,
        outlineWidth: 3,
      },
      label: {
        text: g.uavId,
        font: '10px JetBrains Mono, monospace',
        fillColor: Color.WHITE,
        outlineColor: Color.BLACK,
        outlineWidth: 2,
        pixelOffset: new Cartesian3(0, -32, 0),
        style: 2, // FILL_AND_OUTLINE
      },
      path: {
        resolution: 1,
        material: Color.fromCssColorString('#22d3a8').withAlpha(0.2),
        width: 1.5,
        leadTime: 0,
        trailTime: 120,
      },
    });

    // Predicted Trail (Phase 1)
    refs.predictedTrail = viewer.entities.add({
      id: 'aircraft-predicted-path',
      polyline: {
        positions: [],
        width: 2.0,
        material: Color.fromCssColorString('#38bdf8').withAlpha(0.4),
      }
    });
  } else {
    (refs.aircraft as unknown as { position: Cartesian3 }).position = pos;
    
    // Sync Predicted Trail
    if (refs.predictedTrail?.polyline) {
      const predPts = branchToGlobePoints(g.lon, g.lat, g.altM, state.twin.branches[0] || { points: [] });
      (refs.predictedTrail.polyline as any).positions = predPts;
    }

    if (refs.aircraft.point) {
      (refs.aircraft.point as unknown as { color: Color }).color =
        g.conflictRisk > 0.5 || rerouteRequired
          ? Color.fromCssColorString('#f43f5e') // Red alert
          : Color.fromCssColorString('#22d3a8');
    }
    
    const air = useOperatingStore.getState().operating?.aircraft;
    const mode = air?.mode?.toUpperCase() ?? 'COGNITIVE';
    const rssi = air?.rssi != null ? ` · RSSI ${air.rssi}%` : '';

    if (refs.aircraft.label) {
      (refs.aircraft.label as unknown as { text: string }).text = 
        `${g.uavId}\n[${mode}${rssi}]\nALT: ${g.altM.toFixed(1)}m · SPD: ${t.velocityNed ? Math.sqrt(t.velocityNed[0]**2 + t.velocityNed[1]**2).toFixed(1) : '0'}m/s\nHDG: ${t.headingDeg.toFixed(0)}°`;
    }
  }

  syncAirspaceOverlays(refs.airspace, g, viewer);
  syncEnvironmentalOverlays(refs.environment, state, viewer);

  while (refs.futureBranches.length < state.twin.branches.length) {
    const e = viewer.entities.add({ id: `future-branch-${refs.futureBranches.length}` });
    refs.futureBranches.push(e);
  }
  const branchColors = ['#38bdf8', '#f59e0b', '#ef4444'];
  state.twin.branches.forEach((b, i) => {
    const ent = refs.futureBranches[i];
    if (!ent) return;
    const pts = branchToGlobePoints(g.lon, g.lat, g.altM, b);
    const eb = ent as unknown as { polyline: { positions: Cartesian3[]; width: number; material: Color }; show: boolean };
    eb.polyline = {
      positions: pts,
      width: 2 + b.probability * 4,
      material: Color.fromCssColorString(branchColors[i % 3]).withAlpha(0.25 + b.probability * 0.45),
    };
    eb.show = pts.length >= 2;
  });

  const crashPts = branchToGlobePoints(g.lon, g.lat, g.altM, {
    points: state.twin.crashPath,
    probability: state.twin.crashRisk,
    survivability: 0,
    label: 'CRASH',
  });
  if (!refs.governanceRoute) {
    refs.governanceRoute = viewer.entities.add({
      id: 'crash-future',
      polyline: {
        positions: crashPts,
        width: 3,
        material: Color.RED.withAlpha(0.55),
      },
    });
  } else if (refs.governanceRoute.polyline) {
    (refs.governanceRoute.polyline as unknown as { positions: Cartesian3[] }).positions = crashPts;
    refs.governanceRoute.show = state.twin.crashRisk > 0.08;
  }

  viewer.scene.requestRender();
}

export function syncMissionLayers(
  viewer: CesiumViewer,
  refs: GlobeLayerRefs,
  waypoints: GeoWaypoint[],
  geofences: GeoFence[],
  adaptiveOffset: boolean,
): void {
  const op = useOperatingStore.getState().operating;
  const lz = op?.survivability?.landing_zone;

  // Takeoff Point
  if (waypoints.length > 0) {
    if (!refs.takeoffPoint) {
      refs.takeoffPoint = viewer.entities.add({
        id: 'mission-takeoff',
        point: { pixelSize: 14, color: Color.CYAN, outlineColor: Color.WHITE, outlineWidth: 2 },
        label: { text: 'TAKEOFF', font: '9px JetBrains Mono', fillColor: Color.CYAN, pixelOffset: new Cartesian3(0, 18, 0) }
      });
    }
    (refs.takeoffPoint as any).position = Cartesian3.fromDegrees(waypoints[0].lon, waypoints[0].lat, waypoints[0].altM + 6378137);
  }

  // Landing Zone
  if (lz && typeof lz === 'object' && 'lat' in lz) {
    if (!refs.landingZone) {
      refs.landingZone = viewer.entities.add({
        id: 'mission-lz',
        ellipse: { semiMajorAxis: 200, semiMinorAxis: 200, material: Color.fromCssColorString('#22d3a8').withAlpha(0.25), outline: true, outlineColor: Color.fromCssColorString('#22d3a8') },
        label: { text: 'EMERGENCY LZ', font: '9px JetBrains Mono', fillColor: Color.fromCssColorString('#22d3a8'), pixelOffset: new Cartesian3(0, -18, 0) }
      });
    }
    (refs.landingZone as any).position = Cartesian3.fromDegrees((lz as any).lon, (lz as any).lat, ((lz as any).alt_m ?? 0) + 6378137);
    refs.landingZone.show = true;
  } else if (refs.landingZone) {
    refs.landingZone.show = false;
  }

  while (refs.waypoints.length < waypoints.length) {
    refs.waypoints.push(viewer.entities.add({ id: `mission-wp-${refs.waypoints.length}` }));
  }
  while (refs.waypoints.length > waypoints.length) {
    const e = refs.waypoints.pop();
    if (e) viewer.entities.remove(e);
  }

  waypoints.forEach((wp, i) => {
    const ent = refs.waypoints[i];
    if (!ent) return;
    const alt = wp.altM + 6378137;
    (ent as unknown as { position: Cartesian3 }).position = Cartesian3.fromDegrees(wp.lon, wp.lat, alt);
    const ew = ent as unknown as Record<string, unknown>;
    ew.point = {
      pixelSize: 14,
      color: Color.fromCssColorString('#a78bfa'),
      outlineColor: Color.WHITE,
      outlineWidth: 2,
    };
    ew.label = {
      text: wp.label ?? `WP${i + 1}`,
      font: '11px monospace',
      fillColor: Color.fromCssColorString('#e9d5ff'),
      pixelOffset: new Cartesian3(0, -20, 0),
    };
  });

  if (waypoints.length >= 2) {
    const positions = waypoints.map((w) =>
      Cartesian3.fromDegrees(w.lon, w.lat, w.altM + 6378137),
    );
    if (!refs.adaptiveRoute) {
      refs.adaptiveRoute = viewer.entities.add({
        id: 'mission-route',
        corridor: {
          positions,
          width: adaptiveOffset ? 1200 : 800,
          extrudedHeight: 200, 
          height: 50,
          material: Color.fromCssColorString('#8b5cf6').withAlpha(adaptiveOffset ? 0.35 : 0.2),
          outline: true,
          outlineColor: Color.fromCssColorString('#c4b5fd').withAlpha(0.6),
        },
      });
    } else if (refs.adaptiveRoute.corridor) {
      (refs.adaptiveRoute.corridor as unknown as { positions: Cartesian3[] }).positions = positions;
      refs.adaptiveRoute.show = true;
    }
  } else if (refs.adaptiveRoute) {
    refs.adaptiveRoute.show = false;
  }

  while (refs.geofences.length < geofences.length) {
    refs.geofences.push(viewer.entities.add({ id: `mission-gf-${refs.geofences.length}` }));
  }
  while (refs.geofences.length > geofences.length) {
    const e = refs.geofences.pop();
    if (e) viewer.entities.remove(e);
  }

  geofences.forEach((gf, i) => {
    const ent = refs.geofences[i];
    if (!ent) return;
    const color =
      gf.kind === 'no-fly' ? Color.RED : gf.kind === 'recovery' ? Color.fromCssColorString('#22d3a8') : Color.YELLOW;
    
    const heightM = 500; 
    (ent as unknown as { position: Cartesian3 }).position = Cartesian3.fromDegrees(
      gf.lon,
      gf.lat,
      heightM / 2 
    );
    (ent as unknown as Record<string, unknown>).cylinder = {
      length: heightM,
      topRadius: gf.radiusM,
      bottomRadius: gf.radiusM * 0.85,
      material: color.withAlpha(0.15),
      outline: true,
      outlineColor: color.withAlpha(0.6),
    };
  });

  viewer.scene.requestRender();
}

export function syncSwarmOnGlobe(
  viewer: CesiumViewer,
  refs: GlobeLayerRefs,
  centerLon: number,
  centerLat: number,
  altM: number,
  nodeIds: string[],
): void {
  const alt = altM + 6378137;
  while (refs.swarmNodes.length < nodeIds.length) {
    refs.swarmNodes.push(viewer.entities.add({ id: `swarm-${refs.swarmNodes.length}` }));
  }
  while (refs.swarmNodes.length > nodeIds.length) {
    const e = refs.swarmNodes.pop();
    if (e) viewer.entities.remove(e);
  }
  const positions: Cartesian3[] = [];
  nodeIds.forEach((id, i) => {
    const angle = (i / Math.max(nodeIds.length, 1)) * CesiumMath.TWO_PI;
    const d = 0.012;
    const pos = Cartesian3.fromDegrees(
      centerLon + Math.cos(angle) * d,
      centerLat + Math.sin(angle) * d,
      alt + 30,
    );
    positions.push(pos);
    
    const ent = refs.swarmNodes[i];
    if (!ent) return;
    (ent as unknown as { position: Cartesian3 }).position = pos;
    const es = ent as unknown as Record<string, unknown>;
    es.point = { pixelSize: 10, color: Color.fromCssColorString('#22d3ee'), outlineWidth: 1, outlineColor: Color.WHITE };
    es.label = { text: String(id).slice(0, 8), font: '9px monospace', fillColor: Color.CYAN, pixelOffset: new Cartesian3(0, -14, 0) };
  });

  const numLinks = Math.max(0, nodeIds.length * (nodeIds.length - 1) / 2);
  while (refs.swarmLinks.length < numLinks) {
    refs.swarmLinks.push(viewer.entities.add({ id: `swarm-link-${refs.swarmLinks.length}` }));
  }
  while (refs.swarmLinks.length > numLinks) {
    const e = refs.swarmLinks.pop();
    if (e) viewer.entities.remove(e);
  }

  let linkIdx = 0;
  for (let i = 0; i < positions.length; i++) {
    for (let j = i + 1; j < positions.length; j++) {
      const ent = refs.swarmLinks[linkIdx++];
      if (!ent) continue;
      (ent as unknown as Record<string, unknown>).polyline = {
        positions: [positions[i], positions[j]],
        width: 1.5,
        material: Color.fromCssColorString('#22d3ee').withAlpha(0.3),
      };
    }
  }

  viewer.scene.requestRender();
}

export function syncFleetLayer(
  viewer: CesiumViewer,
  refs: GlobeLayerRefs,
  fleetData: Array<{ id: string; lat: number; lon: number; alt: number; status: string }>
): void {
  // Phase 3: Multi Aircraft Ops (100+ drones)
  const activeIds = new Set(fleetData.map(d => d.id));
  
  // Cleanup removed drones
  for (const [id, entity] of refs.fleetDrones.entries()) {
    if (!activeIds.has(id)) {
      viewer.entities.remove(entity);
      refs.fleetDrones.delete(id);
    }
  }

  // Update or add drones
  fleetData.forEach(drone => {
    let ent = refs.fleetDrones.get(drone.id);
    const pos = Cartesian3.fromDegrees(drone.lon, drone.lat, drone.alt + 6378137);
    
    if (!ent) {
      ent = viewer.entities.add({
        id: `fleet-uav-${drone.id}`,
        position: pos,
        point: {
          pixelSize: 12,
          color: drone.status === 'ready' ? Color.CYAN : Color.ORANGE,
          outlineColor: Color.WHITE,
          outlineWidth: 1,
        },
        label: {
          text: drone.id,
          font: '8px JetBrains Mono',
          fillColor: Color.WHITE,
          pixelOffset: new Cartesian3(0, -18, 0)
        }
      });
      refs.fleetDrones.set(drone.id, ent);
    } else {
      (ent as any).position = pos;
    }
  });
}
