import {
  Color,
  EllipsoidTerrainProvider,
  Ion,
  Viewer as CesiumViewer,
  createWorldTerrainAsync,
  createWorldImageryAsync,
  IonWorldImageryStyle,
  OpenStreetMapImageryProvider,
} from 'cesium';

let configured = false;

/** Avoid default Ion imagery (requires token → tile decode failures). */
export function ensureCesiumConfigured(): void {
  if (configured) return;
  configured = true;
  const token = import.meta.env.VITE_CESIUM_ION_TOKEN as string | undefined;
  if (token) {
    console.log("[CESIUM] Using provided Ion Token");
    Ion.defaultAccessToken = token;
  } else {
    console.warn("[CESIUM] No Ion Token found. Falling back to OSM.");
  }
}

export const cognitionTerrainProvider = new EllipsoidTerrainProvider();

/** Dark tactical globe — photoreal where possible, OSM fallback. */
export async function applyTacticalGlobe(viewer: CesiumViewer): Promise<void> {
  ensureCesiumConfigured();
  const { globe } = viewer.scene;
  globe.show = true;
  globe.enableLighting = true;
  globe.showGroundAtmosphere = true;
  
  // Set a realistic dark Earth base color (Ocean/Land mix) 
  // so we don't see a bright blue procedural sphere if tiles fail.
  globe.baseColor = Color.fromCssColorString('#020b16'); 

  try {
    const token = Ion.defaultAccessToken;
    if (token) {
      viewer.terrainProvider = await createWorldTerrainAsync();
      const imagery = await createWorldImageryAsync({
        style: IonWorldImageryStyle.AERIAL_WITH_LABELS,
      });
      viewer.imageryLayers.removeAll();
      viewer.imageryLayers.addImageryProvider(imagery);
      console.log("[CESIUM] Photoreal imagery and terrain loaded.");
    } else {
      throw new Error("No Ion Token");
    }
  } catch (e) {
    console.error("[CESIUM] Photoreal load failed, falling back to OSM", e);
    viewer.imageryLayers.removeAll();
    viewer.imageryLayers.addImageryProvider(new OpenStreetMapImageryProvider({
      url: 'https://a.tile.openstreetmap.org/'
    }));
    viewer.terrainProvider = new EllipsoidTerrainProvider();
  }

  viewer.scene.backgroundColor = Color.fromCssColorString('#000508');
  if (viewer.scene.skyAtmosphere) {
    viewer.scene.skyAtmosphere.show = true;
    viewer.scene.skyAtmosphere.brightnessShift = -0.1;
  }
  viewer.scene.fog.enabled = true;
  viewer.scene.fog.density = 2e-4;
}
