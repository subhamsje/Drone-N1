import { Cartesian3, Color, Entity, Viewer as CesiumViewer } from 'cesium';
import type { GlobeRenderState } from '@altaria/realtime-engine';

export type AirspaceEntities = {
  highway?: Entity;
  noFly?: Entity;
  rfZone?: Entity;
  threat?: Entity;
};

export function initAirspaceOverlays(viewer: CesiumViewer): AirspaceEntities {
  // Empty init, will sync on first telemetry
  return {
    highway: viewer.entities.add({ id: 'uam-highway', show: false }),
    noFly: viewer.entities.add({ id: 'no-fly', show: false }),
    rfZone: viewer.entities.add({ id: 'rf-denied', show: false }),
    threat: viewer.entities.add({ id: 'threat-region', show: false }),
  };
}

export function syncAirspaceOverlays(entities: AirspaceEntities, g: GlobeRenderState, viewer: CesiumViewer) {
  const alt = g.altM + 6378137;

  if (entities.threat) {
    const baseRadius = 800 + g.threatLevel * 2000;
    const pos = Cartesian3.fromDegrees(g.lon + 0.005, g.lat + 0.004, alt + 100);
    (entities.threat as any).position = pos;
    (entities.threat as any).cylinder = {
      length: 400,
      topRadius: baseRadius,
      bottomRadius: baseRadius * 0.8,
      material: Color.ORANGE.withAlpha(0.15),
      outline: true,
      outlineColor: Color.ORANGE.withAlpha(0.6),
    };
    entities.threat.show = g.threatLevel > 0.1;
  }

  if (entities.noFly) {
    const pos = Cartesian3.fromDegrees(g.lon - 0.006, g.lat + 0.002, alt + 50);
    (entities.noFly as any).position = pos;
    (entities.noFly as any).cylinder = {
      length: 300,
      topRadius: 1000,
      bottomRadius: 1000,
      material: Color.RED.withAlpha(0.12),
      outline: true,
      outlineColor: Color.RED.withAlpha(0.5),
    };
    entities.noFly.show = true;
  }

  if (entities.rfZone) {
    const pos = Cartesian3.fromDegrees(g.lon + 0.002, g.lat - 0.005, alt + 150);
    (entities.rfZone as any).position = pos;
    (entities.rfZone as any).cylinder = {
      length: 500,
      topRadius: 1200,
      bottomRadius: 1000,
      material: Color.YELLOW.withAlpha(0.1),
      outline: true,
      outlineColor: Color.YELLOW.withAlpha(0.4),
    };
    entities.rfZone.show = g.rfDenied > 0.1;
  }

  viewer.scene.requestRender();
}
