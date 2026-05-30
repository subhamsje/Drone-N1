import { memo, useRef, useEffect, useCallback, useState } from 'react';
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
import { flyToOperationalArea, zoomToUserLocation } from './cesiumGlobe';
import { ensureCesiumConfigured, applyTacticalGlobe } from './cesiumRuntime';
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
  const globeReady = useRef(false);
  const [initStatus, setInitStatus] = useState({ 
    ready: false, 
    error: null as string | null,
    terrain: 'pending',
    imagery: 'pending'
  });

  const tool = useMissionStore((s) => s.tool);
  const waypoints = useMissionStore((s) => s.waypoints);
  const geofences = useMissionStore((s) => s.geofences);
  const governanceActive = useMissionStore((s) => s.governanceActive);
  const envelope = useCognitionStore((s) => s.envelope);

  const setupViewer = useCallback(async (viewer: CesiumViewer) => {
    if (globeReady.current) return;
    globeReady.current = true;
    
    try {
      console.log("[CESIUM] Initializing photoreal globe...");
      await applyTacticalGlobe(viewer);
      setInitStatus(prev => ({ ...prev, terrain: 'loaded', imagery: 'loaded' }));
    } catch (e) {
      console.error("[CESIUM] Initialization failed", e);
      setInitStatus(prev => ({ ...prev, error: String(e) }));
    }

    layersRef.current = initGlobeLayers(viewer);
    const g = cognitionEngine().renderState.globe;
    flyToOperationalArea(viewer, g.lon, g.lat);
    setInitStatus(prev => ({ ...prev, ready: true }));

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
      if (viewer && !viewer.isDestroyed()) {
        if (!globeReady.current) {
          void setupViewer(viewer);
        }
        
        if (layersRef.current) {
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
      />
      <div className="pointer-events-none absolute inset-0 z-10">
        <div className="ops-scanlines absolute inset-0 opacity-20" />
        <div className="absolute left-3 top-3 ops-panel px-3 py-2">
          <p className="font-mono text-[9px] uppercase tracking-widest text-violet-300">Planetary command</p>
          <p className="font-mono text-[10px] text-slate-400">PHOTOREAL TERRAIN · {tool.toUpperCase()}</p>
        </div>

        <div className="absolute right-3 top-12 flex flex-col gap-2 pointer-events-auto">
          <button
            onClick={() => {
              const v = viewerRef.current?.cesiumElement;
              if (v) zoomToUserLocation(v);
            }}
            className="ops-panel px-3 py-1.5 font-mono text-[9px] text-cyan-400 uppercase tracking-widest hover:bg-cyan-950/40 transition-colors"
          >
            [ GPS LOCATE ME ]
          </button>
        </div>
        
        {envelope?.uav_id && (
          <div className="absolute bottom-24 left-3 ops-panel px-3 py-2 flex flex-col gap-1 border-teal-500/30">
            <p className="font-mono text-[10px] font-bold text-teal-400 uppercase tracking-widest">{envelope.uav_id}</p>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1 font-mono text-[9px] text-slate-400">
              <span>ALT:</span> <span className="text-white">{(envelope.pose.altitude_m ?? 0).toFixed(1)}m</span>
              <span>SPD:</span> <span className="text-white">{(envelope.pose.velocity_ned ? Math.sqrt(envelope.pose.velocity_ned[0]**2 + envelope.pose.velocity_ned[1]**2) : 0).toFixed(1)}m/s</span>
              <span>BAT:</span> <span className={(envelope.hardware?.battery_remaining as number ?? 1) < 0.2 ? 'text-red-500' : 'text-emerald-400'}>{((envelope.hardware?.battery_remaining as number ?? 1) * 100).toFixed(0)}%</span>
              <span>HDG:</span> <span className="text-white">{(envelope.pose.heading_deg ?? 0).toFixed(0)}°</span>
            </div>
          </div>
        )}

        <div className="absolute right-3 top-3 ops-panel px-2 py-1 font-mono text-[9px] text-slate-500 flex flex-col items-end">
          <span>REAL-TIME TELEMETRY · MISSION PLAN · RECOVERY CORRIDORS</span>
          <div className="mt-1 flex gap-2 border-t border-slate-800 pt-1">
            <span className={initStatus.ready ? 'text-emerald-500' : 'text-amber-500'}>RENDERER: CESIUM</span>
            <span className={initStatus.terrain === 'loaded' ? 'text-emerald-500' : 'text-red-500'}>TERRAIN: {initStatus.terrain.toUpperCase()}</span>
            <span className={initStatus.imagery === 'loaded' ? 'text-emerald-500' : 'text-red-500'}>IMAGERY: {initStatus.imagery.toUpperCase()}</span>
          </div>
        </div>

        {initStatus.error && (
          <div className="absolute inset-0 flex items-center justify-center bg-red-950/20 backdrop-blur-md pointer-events-auto">
            <div className="ops-panel p-6 border-red-500 max-w-md">
              <h1 className="text-red-500 font-mono text-xl mb-2 font-bold">CESIUM INITIALIZATION FAILED</h1>
              <p className="text-white font-mono text-xs leading-relaxed">{initStatus.error}</p>
              <div className="mt-4 p-2 bg-slate-900 rounded font-mono text-[10px] text-slate-400">
                POSSIBLE CAUSES:<br/>
                • Invalid VITE_CESIUM_ION_TOKEN<br/>
                • No internet connection<br/>
                • Tile server CORS rejection<br/>
                • GPU drivers / WebGL issues
              </div>
              <button 
                onClick={() => window.location.reload()}
                className="mt-6 w-full py-2 bg-red-900/40 text-red-200 border border-red-500 font-mono text-xs uppercase tracking-widest hover:bg-red-800/60"
              >
                Restart Kernel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});
