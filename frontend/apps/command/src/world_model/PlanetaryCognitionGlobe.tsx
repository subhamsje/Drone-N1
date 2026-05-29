import { memo, useRef, useEffect, useCallback } from 'react';
import { Viewer, type CesiumComponentRef } from 'resium';
import {
  Cartesian2,
  Cartographic,
  Math as CesiumMath,
  ScreenSpaceEventHandler,
  ScreenSpaceEventType,
  Viewer as CesiumViewer,
} from 'cesium';
import { cognitionEngine } from '../config/runtime';
import { configureOperationalGlobe, flyToOperationalArea, type GlobeImageryMode } from './cesiumGlobe';
import { ensureCesiumConfigured } from './cesiumRuntime';
import {
  initGlobeLayers,
  syncCognitionLayers,
  syncMissionLayers,
  syncSwarmOnGlobe,
  type GlobeLayerRefs,
} from './globeLayers';
import { useMissionStore } from '../stores/missionStore';
import { useCognitionStore } from '../stores/cognitionStore';

ensureCesiumConfigured();

export const PlanetaryCognitionGlobe = memo(function PlanetaryCognitionGlobe() {
  const viewerRef = useRef<CesiumComponentRef<CesiumViewer> | null>(null);
  const layersRef = useRef<GlobeLayerRefs | null>(null);
  const handlerRef = useRef<ScreenSpaceEventHandler | null>(null);
  const lastRevision = useRef(-1);
  const imageryMode = useRef<GlobeImageryMode>('osm');
  const globeReady = useRef(false);

  const tool = useMissionStore((s) => s.tool);
  const waypoints = useMissionStore((s) => s.waypoints);
  const geofences = useMissionStore((s) => s.geofences);
  const governanceActive = useMissionStore((s) => s.governanceActive);
  const envelope = useCognitionStore((s) => s.envelope);

  const setupViewer = useCallback(async (viewer: CesiumViewer) => {
    if (globeReady.current) return;
    imageryMode.current = await configureOperationalGlobe(viewer);
    layersRef.current = initGlobeLayers(viewer);
    const g = cognitionEngine().renderState.globe;
    flyToOperationalArea(viewer, g.lon, g.lat);
    globeReady.current = true;

    handlerRef.current = new ScreenSpaceEventHandler(viewer.scene.canvas);
    handlerRef.current.setInputAction((movement: { position: Cartesian2 }) => {
      const t = useMissionStore.getState().tool;
      if (t === 'navigate') return;
      const cartesian = viewer.camera.pickEllipsoid(movement.position, viewer.scene.globe.ellipsoid);
      if (!cartesian) return;
      const carto = Cartographic.fromCartesian(cartesian);
      const lon = CesiumMath.toDegrees(carto.longitude);
      const lat = CesiumMath.toDegrees(carto.latitude);
      const altM = cognitionEngine().renderState.globe.altM + 100;
      if (t === 'waypoint') {
        useMissionStore.getState().addWaypoint({ lon, lat, altM });
      } else if (t === 'geofence') {
        useMissionStore.getState().addGeofence({ lon, lat, radiusM: 1800, kind: 'no-fly' });
      } else if (t === 'corridor') {
        useMissionStore.getState().addWaypoint({ lon, lat, altM: altM + 20 });
      }
      viewer.scene.requestRender();
    }, ScreenSpaceEventType.LEFT_CLICK);
  }, []);

  useEffect(() => {
    let raf = 0;
    const tick = () => {
      const viewer = viewerRef.current?.cesiumElement;
      if (viewer && !viewer.isDestroyed() && layersRef.current) {
        if (!globeReady.current) void setupViewer(viewer);
        const rev = cognitionEngine().renderState.revision;
        const rg = envelope?.route_governance as { reroute_required?: boolean } | undefined;
        const reroute = Boolean(rg?.reroute_required) && governanceActive;
        if (rev !== lastRevision.current) {
          lastRevision.current = rev;
          syncCognitionLayers(viewer, layersRef.current, cognitionEngine().renderState, reroute);
        }
        syncMissionLayers(viewer, layersRef.current, waypoints, geofences, reroute);
        const swarm = envelope?.swarm as { cognition_graph?: { nodes?: string[] } } | undefined;
        const nodes = swarm?.cognition_graph?.nodes ?? ['α', 'β', 'γ', 'δ'];
        const g = cognitionEngine().renderState.globe;
        syncSwarmOnGlobe(viewer, layersRef.current, g.lon, g.lat, g.altM, nodes);
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [setupViewer, waypoints, geofences, governanceActive, envelope?.route_governance, envelope?.swarm]);

  useEffect(
    () => () => {
      handlerRef.current?.destroy();
      const v = viewerRef.current?.cesiumElement;
      if (v && !v.isDestroyed() && layersRef.current) {
        [
          layersRef.current.aircraft,
          layersRef.current.adaptiveRoute,
          layersRef.current.governanceRoute,
          ...layersRef.current.futureBranches,
          ...layersRef.current.waypoints,
          ...layersRef.current.geofences,
          ...layersRef.current.swarmNodes,
          ...Object.values(layersRef.current.airspace),
        ].forEach((e) => e && v.entities.remove(e));
      }
      layersRef.current = null;
      globeReady.current = false;
    },
    [],
  );

  const modeLabel =
    imageryMode.current === 'photoreal' ? 'PHOTOREAL TERRAIN' : imageryMode.current === 'osm' ? 'LIVE MAP' : 'TACTICAL';

  return (
    <div className="relative h-full w-full">
      <Viewer
        ref={viewerRef}
        full
        baseLayer={false}
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
        <div className="ops-scanlines absolute inset-0 opacity-20" />
        <div className="absolute left-3 top-3 ops-panel px-3 py-2">
          <p className="font-mono text-[9px] uppercase tracking-widest text-violet-300">Planetary cognition</p>
          <p className="font-mono text-[10px] text-slate-400">{modeLabel} · {tool.toUpperCase()}</p>
        </div>
        <div className="absolute right-3 top-3 ops-panel px-2 py-1 font-mono text-[9px] text-slate-500">
          FUTURES ON GLOBE · SWARM · ROUTE GOVERNANCE
        </div>
      </div>
    </div>
  );
});
