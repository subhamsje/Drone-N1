import { Cartesian3, Color, Entity, Viewer as CesiumViewer } from 'cesium';
import type { GlobeRenderState } from '@altaria/realtime-engine';
import { useOperatingStore } from '../stores/operatingStore';

export type AirspaceEntities = {
  highway?: Entity;
  noFly?: Entity;
  rfZone?: Entity;
  threat?: Entity;
  military?: Entity;
  emergency?: Entity;
};

export function initAirspaceOverlays(viewer: CesiumViewer): AirspaceEntities {
  return {
    highway: viewer.entities.add({ id: 'uam-highway', show: false }),
    noFly: viewer.entities.add({ id: 'no-fly', show: false }),
    rfZone: viewer.entities.add({ id: 'rf-denied', show: false }),
    threat: viewer.entities.add({ id: 'threat-region', show: false }),
    military: viewer.entities.add({ id: 'military-zone', show: false }),
    emergency: viewer.entities.add({ id: 'emergency-zone', show: false }),
  };
}

export function syncAirspaceOverlays(entities: AirspaceEntities, g: GlobeRenderState, viewer: CesiumViewer) {
  const alt = g.altM + 6378137;
  const op = useOperatingStore.getState().operating;
  const airspace = op?.geospatial?.airspace;

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

  if (entities.military && airspace) {
    const pos = Cartesian3.fromDegrees(g.lon + 0.015, g.lat - 0.01, alt + 200);
    (entities.military as any).position = pos;
    (entities.military as any).cylinder = {
      length: 1000,
      topRadius: 3000,
      bottomRadius: 3000,
      material: Color.DARKSLATEGRAY.withAlpha(0.2),
      outline: true,
      outlineColor: Color.BLACK.withAlpha(0.8),
    };
    entities.military.show = airspace.restriction_level === 'high';
  }

  if (entities.emergency && airspace) {
    const pos = Cartesian3.fromDegrees(g.lon - 0.01, g.lat - 0.008, alt + 50);
    (entities.emergency as any).position = pos;
    (entities.emergency as any).cylinder = {
      length: 200,
      topRadius: 500,
      bottomRadius: 500,
      material: Color.RED.withAlpha(0.3),
      outline: true,
      outlineColor: Color.WHITE.withAlpha(0.9),
    };
    entities.emergency.show = airspace.notam_active;
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

  if (entities.highway) {
    (entities.highway as any).corridor = {
      positions: Cartesian3.fromDegreesArrayHeights([
        g.lon - 0.01, g.lat - 0.01, alt - 20,
        g.lon, g.lat, alt,
        g.lon + 0.01, g.lat + 0.01, alt + 20
      ]),
      width: 400,
      material: Color.CYAN.withAlpha(0.1)
    };
    entities.highway.show = Boolean(airspace?.controlled);
  }

  viewer.scene.requestRender();
}
