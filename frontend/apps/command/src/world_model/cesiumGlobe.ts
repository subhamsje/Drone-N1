import {
  Cartesian3,
  Color,
  EllipsoidTerrainProvider,
  OpenStreetMapImageryProvider,
  Viewer as CesiumViewer,
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

  const token = import.meta.env.VITE_CESIUM_ION_TOKEN as string | undefined;
  if (token) {
    try {
      const { createWorldTerrainAsync, IonImageryProvider } = await import('cesium');
      viewer.terrainProvider = await createWorldTerrainAsync();
      viewer.imageryLayers.removeAll();
      viewer.imageryLayers.addImageryProvider(
        await IonImageryProvider.fromAssetId(2),
      );
      viewer.scene.backgroundColor = Color.fromCssColorString('#000508');
      return 'photoreal';
    } catch {
      /* fall through */
    }
  }

  try {
    viewer.imageryLayers.removeAll();
    viewer.imageryLayers.addImageryProvider(
      new OpenStreetMapImageryProvider({ url: 'https://tile.openstreetmap.org/' }),
    );
    viewer.terrainProvider = new EllipsoidTerrainProvider();
    viewer.scene.backgroundColor = Color.fromCssColorString('#020617');
    globe.baseColor = Color.fromCssColorString('#0c1222');
    return 'osm';
  } catch {
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
