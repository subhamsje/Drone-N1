import { memo, useRef, useEffect, useCallback } from 'react';
import { Viewer, type CesiumComponentRef } from 'resium';
import { Cartesian3, Color, Viewer as CesiumViewer, Entity } from 'cesium';
import { cognitionEngine } from '../config/runtime';
import { applyTacticalGlobe, cognitionTerrainProvider, ensureCesiumConfigured } from './cesiumRuntime';
import {
  initAirspaceOverlays,
  syncAirspaceOverlays,
  type AirspaceEntities,
} from './airspaceOverlays';

ensureCesiumConfigured();

function syncGlobeEntities(
  entities: { aircraft?: Entity; corridor?: Entity; congestion?: Entity },
  viewer: CesiumViewer,
) {
  const g = cognitionEngine().renderState.globe;
  const alt = g.altM + 6378137;
  const pos = Cartesian3.fromDegrees(g.lon, g.lat, alt);
  const ac = entities.aircraft;
  if (ac) {
    (ac as unknown as { position: Cartesian3 }).position = pos;
    if (ac.point) {
      (ac.point as unknown as { color: Color }).color =
        g.conflictRisk > 0.5 ? Color.ORANGE : Color.fromCssColorString('#22d3a8');
    }
    if (ac.label) (ac.label as unknown as { text: string }).text = g.uavId;
  }
  const corridor = entities.corridor;
  if (corridor?.polyline) {
    (corridor.polyline as unknown as { positions: Cartesian3[] }).positions =
      Cartesian3.fromDegreesArrayHeights([
        g.lon, g.lat, alt,
        g.lon + 0.01, g.lat + 0.005, alt,
        g.lon + 0.02, g.lat, alt + 10,
      ]);
  }
  const cong = entities.congestion;
  if (cong) {
    (cong as unknown as { position: Cartesian3 }).position = Cartesian3.fromDegrees(
      g.lon + 0.03,
      g.lat + 0.02,
      alt,
    );
    if (cong.label) {
      (cong.label as unknown as { text: string }).text = `CONGESTION ${(g.congestion * 100).toFixed(0)}%`;
    }
  }
  viewer.scene.requestRender();
}

export const PlanetaryGlobe = memo(function PlanetaryGlobe() {
  const viewerRef = useRef<CesiumComponentRef<CesiumViewer> | null>(null);
  const entitiesRef = useRef<{
    aircraft?: Entity;
    corridor?: Entity;
    congestion?: Entity;
  }>({});
  const airspaceRef = useRef<AirspaceEntities>({});
  const lastRevision = useRef(-1);
  const tacticalApplied = useRef(false);

  const initEntities = useCallback((viewer: CesiumViewer) => {
    if (entitiesRef.current.aircraft) return;

    entitiesRef.current.aircraft = viewer.entities.add({
      id: 'altaria-aircraft',
      position: Cartesian3.fromDegrees(77.5, 12.9, 6378167),
      point: {
        pixelSize: 14,
        color: Color.fromCssColorString('#22d3a8'),
        outlineColor: Color.WHITE,
        outlineWidth: 2,
      },
      label: {
        text: 'ALTARIA',
        font: '11px monospace',
        fillColor: Color.WHITE,
        pixelOffset: new Cartesian3(0, -24, 0),
      },
    });

    entitiesRef.current.corridor = viewer.entities.add({
      id: 'altaria-corridor',
      polyline: {
        positions: Cartesian3.fromDegreesArrayHeights([77.5, 12.9, 6378167, 77.51, 12.905, 6378167]),
        width: 4,
        material: Color.fromCssColorString('#8b5cf6').withAlpha(0.8),
      },
    });

    entitiesRef.current.congestion = viewer.entities.add({
      id: 'altaria-congestion',
      position: Cartesian3.fromDegrees(77.53, 12.92, 6378167),
      label: {
        text: 'CONGESTION —',
        font: '10px monospace',
        fillColor: Color.YELLOW,
      },
    });

    airspaceRef.current = initAirspaceOverlays(viewer);
    syncGlobeEntities(entitiesRef.current, viewer);
    syncAirspaceOverlays(airspaceRef.current, cognitionEngine().renderState.globe, viewer);
  }, []);

  useEffect(() => {
    let raf = 0;
    const tick = () => {
      const viewer = viewerRef.current?.cesiumElement;
      if (viewer && !viewer.isDestroyed()) {
        if (!entitiesRef.current.aircraft) initEntities(viewer);
        if (!tacticalApplied.current) {
          tacticalApplied.current = true;
          applyTacticalGlobe(viewer);
          viewer.camera.setView({ destination: Cartesian3.fromDegrees(77.5, 12.9, 280000) });
        }
        const rev = cognitionEngine().renderState.revision;
        if (rev !== lastRevision.current) {
          lastRevision.current = rev;
          syncGlobeEntities(entitiesRef.current, viewer);
          syncAirspaceOverlays(airspaceRef.current, cognitionEngine().renderState.globe, viewer);
        }
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [initEntities]);

  useEffect(
    () => () => {
      const v = viewerRef.current?.cesiumElement;
      if (v && !v.isDestroyed()) {
        [...Object.values(entitiesRef.current), ...Object.values(airspaceRef.current)].forEach(
          (e) => e && v.entities.remove(e),
        );
      }
      entitiesRef.current = {};
      airspaceRef.current = {};
      tacticalApplied.current = false;
    },
    [],
  );

  const g = cognitionEngine().renderState.globe;

  return (
    <div className="relative h-full w-full">
      <Viewer
        ref={viewerRef}
        full
        baseLayer={false}
        terrainProvider={cognitionTerrainProvider}
        timeline={false}
        animation={false}
        baseLayerPicker={false}
        geocoder={false}
        homeButton={false}
        navigationHelpButton={false}
        sceneModePicker={false}
        fullscreenButton={false}
        infoBox={false}
        selectionIndicator={false}
        showRenderLoopErrors={false}
        requestRenderMode
        maximumRenderTimeChange={Infinity}
      />
      <div className="pointer-events-none absolute inset-0 z-10">
        <div className="ops-scanlines absolute inset-0 opacity-25" />
        <div className="absolute left-3 top-3 ops-panel px-2 py-1.5 font-mono text-[9px] text-violet-300">
          PLANETARY AIRSPACE · UAM HIGHWAYS
        </div>
        <div className="absolute bottom-3 left-3 flex gap-2 font-mono text-[8px]">
          <span className="text-violet-400/80">CORRIDOR</span>
          <span className="text-red-400/80">NO-FLY</span>
          <span className="text-yellow-400/80">RF {g.rfDenied > 0.1 ? 'ACTIVE' : '—'}</span>
          <span className="text-orange-400/80">THREAT {g.threatLevel > 0.1 ? '↑' : '—'}</span>
        </div>
      </div>
    </div>
  );
});
