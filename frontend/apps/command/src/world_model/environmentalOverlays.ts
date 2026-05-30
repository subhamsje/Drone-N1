import { Cartesian3, Color, Entity, Viewer as CesiumViewer } from 'cesium';
import type { CognitionRenderState } from '@altaria/realtime-engine';

export type EnvironmentEntities = {
  windVectors: Entity[];
  turbulenceMap?: Entity;
};

export function initEnvironmentalOverlays(viewer: CesiumViewer): EnvironmentEntities {
  const windVectors: Entity[] = [];
  
  // Create a grid of wind vectors
  for (let i = 0; i < 16; i++) {
    windVectors.push(viewer.entities.add({
      id: `wind-vector-${i}`,
      polyline: {
        positions: [],
        width: 1.5,
        material: Color.fromCssColorString('#94a3b8').withAlpha(0.2), // Subtle grey
      }
    }));
  }

  // Turbulence Heatmap/Field
  const turbulenceMap = viewer.entities.add({
    id: 'turbulence-field',
    polygon: {
      hierarchy: undefined,
      height: 0,
      material: Color.fromCssColorString('#3b82f6').withAlpha(0.0),
      outline: true,
      outlineColor: Color.fromCssColorString('#60a5fa').withAlpha(0.0),
    }
  });

  return { windVectors, turbulenceMap };
}

export function syncEnvironmentalOverlays(entities: EnvironmentEntities, state: CognitionRenderState, viewer: CesiumViewer) {
  const g = state.globe;
  const t = state.twin;
  const alt = g.altM + 6378137;
  const time = Date.now() / 1000;

  entities.windVectors.forEach((ent, i) => {
    const offsetLon = (Math.floor(i / 4) - 2) * 0.005;
    const offsetLat = ((i % 4) - 2) * 0.005;
    const flow = Math.sin(time + i) * 0.002 * t.turbulence;
    
    const polyline = ent.polyline as any;
    if (polyline) {
      polyline.positions = [
        Cartesian3.fromDegrees(g.lon + offsetLon, g.lat + offsetLat, alt + 10),
        Cartesian3.fromDegrees(g.lon + offsetLon + flow, g.lat + offsetLat + 0.001, alt + 10)
      ];
      polyline.show = true;
    }
  });

  if (entities.turbulenceMap?.polygon) {
    const p = entities.turbulenceMap.polygon as any;
    const radius = 0.015;
    p.hierarchy = {
      positions: Cartesian3.fromDegreesArray([
        g.lon - radius, g.lat,
        g.lon - radius/2, g.lat + radius,
        g.lon + radius/2, g.lat + radius,
        g.lon + radius, g.lat,
        g.lon + radius/2, g.lat - radius,
        g.lon - radius/2, g.lat - radius,
      ])
    };
    p.height = alt + 5;
    p.material = Color.fromCssColorString('#3b82f6').withAlpha(t.turbulence * 0.15);
    p.outlineColor = Color.fromCssColorString('#60a5fa').withAlpha(t.turbulence * 0.3);
    entities.turbulenceMap.show = t.turbulence > 0.1;
  }
}
