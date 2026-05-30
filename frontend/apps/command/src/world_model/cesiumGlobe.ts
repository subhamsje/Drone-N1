import {
  Cartesian3,
  Color,
  Viewer as CesiumViewer,
  createWorldTerrainAsync,
  createWorldImageryAsync,
  IonWorldImageryStyle
} from 'cesium';
import { ensureCesiumConfigured } from './cesiumRuntime';

export type GlobeImageryMode = 'photoreal' | 'tactical' | 'osm';

/** Configure real-world or tactical globe imagery + terrain. */
export async function configureOperationalGlobe(viewer: CesiumViewer): Promise<GlobeImageryMode> {
  ensureCesiumConfigured();
  const { globe, sun, moon, skyAtmosphere } = viewer.scene;
  
  // Cinematic Operational Atmospherics
  globe.show = true;
  globe.enableLighting = true;
  globe.showGroundAtmosphere = true;
  
  if (sun) sun.show = false; // Hide sun mesh for tactical feel
  if (moon) moon.show = false;
  
  // Dark, volumetric fog feel
  viewer.scene.fog.enabled = true;
  viewer.scene.fog.density = 3.5e-4; // Dense operational fog
  viewer.scene.fog.minimumBrightness = 0.05;
  
  if (skyAtmosphere) {
    skyAtmosphere.show = true;
    skyAtmosphere.brightnessShift = -0.3; // Darker atmosphere
    skyAtmosphere.hueShift = -0.1; // Cynerpunk/blueish shift
    skyAtmosphere.saturationShift = 0.2;
  }

  try {
    viewer.terrainProvider = await createWorldTerrainAsync();
    viewer.imageryLayers.removeAll();
    const imagery = await createWorldImageryAsync({
      style: IonWorldImageryStyle.AERIAL_WITH_LABELS,
    });
    viewer.imageryLayers.addImageryProvider(imagery);
    viewer.scene.backgroundColor = Color.fromCssColorString('#000508');
    return 'photoreal';
  } catch (e) {
    console.error("Cesium Photoreal load failed, falling back", e);
    viewer.imageryLayers.removeAll();
    globe.baseColor = Color.fromCssColorString('#0c1222');
    viewer.scene.backgroundColor = Color.fromCssColorString('#020617');
    return 'tactical';
  }
}

export function flyToOperationalArea(viewer: CesiumViewer, lon: number, lat: number, altM = 280000): void {
  viewer.camera.flyTo({
    destination: Cartesian3.fromDegrees(lon, lat, altM),
    duration: 1.2,
  });
}

export function zoomToUserLocation(viewer: CesiumViewer): void {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((pos) => {
      viewer.camera.flyTo({
        destination: Cartesian3.fromDegrees(pos.coords.longitude, pos.coords.latitude, 2000),
        duration: 2.0
      });
    });
  }
}
