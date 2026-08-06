import { Cartesian3, Color, Entity, Viewer as CesiumViewer } from 'cesium';
import type { CognitionRenderState } from '@altaria/realtime-engine';
import { useOperatingStore } from '../stores/operatingStore';

export type EnvironmentEntities = {
  windVectors: Entity[];
  turbulenceMap?: Entity;
  stormCell?: Entity;
  precipitation?: Entity;
};

export function initEnvironmentalOverlays(viewer: CesiumViewer): EnvironmentEntities {
  const windVectors: Entity[] = [];
  for (let i = 0; i < 16; i++) {
    windVectors.push(viewer.entities.add({
      id: `wind-vector-${i}`,
      polyline: {
        positions: [Cartesian3.ZERO, Cartesian3.ZERO],
        width: 1.5,
        material: Color.AQUA.withAlpha(0.2),
      },
      show: false,
    }));
  }

  return {
    windVectors,
    turbulenceMap: viewer.entities.add({
      id: 'turbulence-region',
      polygon: {
        hierarchy: [],
        material: Color.fromCssColorString('#3b82f6').withAlpha(0.1),
        outline: true,
        outlineColor: Color.fromCssColorString('#60a5fa').withAlpha(0.4),
      },
      show: false,
    }),
    stormCell: viewer.entities.add({
      id: 'storm-cell',
      cylinder: {
        length: 2000,
        topRadius: 4000,
        bottomRadius: 3000,
        material: Color.DARKSLATEGRAY.withAlpha(0.3),
        outline: true,
        outlineColor: Color.WHITE.withAlpha(0.2),
      },
      show: false,
    }),
    precipitation: viewer.entities.add({
      id: 'precip-field',
      ellipse: {
        semiMajorAxis: 6000,
        semiMinorAxis: 6000,
        material: Color.CORNFLOWERBLUE.withAlpha(0.15),
        height: 10,
      },
      show: false,
    }),
  };
}

export function syncEnvironmentalOverlays(entities: EnvironmentEntities, state: CognitionRenderState, viewer: CesiumViewer) {
  const g = state.globe;
  const t = state.twin;
  const alt = g.altM + 6378137;
  const time = Date.now() / 1000;
  const geo = useOperatingStore.getState().operating?.geospatial;
  const weather = geo?.weather;

  entities.windVectors.forEach((ent, i) => {
    const offsetLon = (Math.floor(i / 4) - 2) * 0.005;
    const offsetLat = ((i % 4) - 2) * 0.005;

    // Wind Direction based on backend weather context
    const windSpeed = weather?.wind_mps ?? 2.0;
    const windScale = 0.0001 * windSpeed;

    const polyline = ent.polyline as any;
    if (polyline) {
      polyline.positions = [
        Cartesian3.fromDegrees(g.lon + offsetLon, g.lat + offsetLat, alt + 10),
        Cartesian3.fromDegrees(g.lon + offsetLon + windScale, g.lat + offsetLat + windScale, alt + 10)
      ];
      polyline.show = true;
      polyline.width = 1.0 + windSpeed / 5.0;
      polyline.material = Color.AQUA.withAlpha(0.1 + (windSpeed / 20.0));
    }
  });

  if (entities.stormCell && weather) {
    (entities.stormCell as any).position = Cartesian3.fromDegrees(g.lon + 0.04, g.lat + 0.03, alt + 1000);
    entities.stormCell.show = weather.turbulence_index > 0.4;
  }

  if (entities.precipitation && weather) {
    (entities.precipitation as any).position = Cartesian3.fromDegrees(g.lon + 0.03, g.lat + 0.02, alt);
    entities.precipitation.show = weather.precip_mm_h > 0.5;
  }

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
