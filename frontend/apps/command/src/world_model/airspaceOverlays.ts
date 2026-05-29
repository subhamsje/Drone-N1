import { Cartesian3, Color, Entity, Viewer as CesiumViewer } from 'cesium';
import type { GlobeRenderState } from '@altaria/realtime-engine';

export type AirspaceEntities = {
  highway?: Entity;
  noFly?: Entity;
  rfZone?: Entity;
  threat?: Entity;
};

export function initAirspaceOverlays(viewer: CesiumViewer): AirspaceEntities {
  const g = { lon: 77.5, lat: 12.9, altM: 30 };
  const alt = g.altM + 6378137;

  return {
    highway: viewer.entities.add({
      id: 'uam-highway',
      corridor: {
        positions: Cartesian3.fromDegreesArrayHeights([
          g.lon - 0.02, g.lat, alt,
          g.lon, g.lat + 0.01, alt,
          g.lon + 0.03, g.lat, alt + 20,
        ]),
        width: 8000,
        material: Color.fromCssColorString('#8b5cf6').withAlpha(0.15),
      },
    }),
    noFly: viewer.entities.add({
      id: 'no-fly',
      cylinder: {
        length: 2000,
        topRadius: 12000,
        bottomRadius: 9000,
        material: Color.RED.withAlpha(0.12),
        outline: true,
        outlineColor: Color.RED.withAlpha(0.5),
      },
      position: Cartesian3.fromDegrees(g.lon + 0.025, g.lat - 0.015, alt + 1000),
    }),
    rfZone: viewer.entities.add({
      id: 'rf-denied',
      cylinder: {
        length: 3000,
        topRadius: 14000,
        bottomRadius: 11000,
        material: Color.YELLOW.withAlpha(0.1),
        outline: true,
        outlineColor: Color.YELLOW.withAlpha(0.4),
      },
      position: Cartesian3.fromDegrees(g.lon - 0.02, g.lat + 0.02, alt + 1500),
    }),
    threat: viewer.entities.add({
      id: 'threat-region',
      cylinder: {
        length: 4000,
        topRadius: 10000,
        bottomRadius: 8000,
        material: Color.ORANGE.withAlpha(0.15),
        outline: true,
        outlineColor: Color.ORANGE.withAlpha(0.6),
      },
      position: Cartesian3.fromDegrees(g.lon + 0.04, g.lat + 0.03, alt + 2000),
    }),
  };
}

export function syncAirspaceOverlays(entities: AirspaceEntities, g: GlobeRenderState, viewer: CesiumViewer) {
  if (entities.threat?.cylinder) {
    const top = entities.threat.cylinder.topRadius as unknown as { getValue: () => number, setValue: (v: number) => void } | number;
    const baseRadius = 8000 + g.threatLevel * 12000;
    
    // In Cesium properties might be ConstantProperty or raw values
    if (typeof top === 'number' || top === undefined) {
      (entities.threat.cylinder as any).topRadius = baseRadius;
      (entities.threat.cylinder as any).bottomRadius = baseRadius * 0.8;
    } else if (typeof top.setValue === 'function') {
      top.setValue(baseRadius);
      (entities.threat.cylinder.bottomRadius as any).setValue(baseRadius * 0.8);
    }

    entities.threat.show = g.threatLevel > 0.05;
  }
  if (entities.rfZone?.cylinder) {
    entities.rfZone.show = g.rfDenied > 0.05;
  }
  viewer.scene.requestRender();
}
