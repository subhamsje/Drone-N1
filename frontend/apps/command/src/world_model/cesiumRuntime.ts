import {
  Color,
  EllipsoidTerrainProvider,
  Ion,
  Viewer as CesiumViewer,
  createWorldTerrainAsync,
  createWorldImageryAsync,
  IonWorldImageryStyle,
  OpenStreetMapImageryProvider,
  createOsmBuildingsAsync,
  createGooglePhotorealistic3DTileset,
  ShadowMode,
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

/** Baseline Cesium globe — no post-processing, no visual fluff. */
export async function applyTacticalGlobe(viewer: CesiumViewer): Promise<void> {
  ensureCesiumConfigured();
  const { scene } = viewer;
  const globe = scene.globe;
  
  // Disable all post-processing
  scene.postProcessStages.bloom.enabled = false;
  scene.postProcessStages.ambientOcclusion.enabled = false;
  // Clear any active post-process stages
  scene.postProcessStages.removeAll();

  globe.show = true;
  globe.enableLighting = true;
  globe.showGroundAtmosphere = true;
  
  // Shadows & Occlusion
  scene.shadowMap.enabled = true;
  (globe as any).shadows = ShadowMode.ENABLED;

  // Atmospheric Realism (Baseline)
  if (scene.skyAtmosphere) {
    scene.skyAtmosphere.show = true;
    scene.skyAtmosphere.brightnessShift = 0.0;
    scene.skyAtmosphere.hueShift = 0.0;
  }
  
  // Set a realistic dark Earth base color
  globe.baseColor = Color.fromCssColorString('#020b16'); 

  try {
    const token = Ion.defaultAccessToken;
    if (token) {
      // 1. Load Photoreal Terrain
      viewer.terrainProvider = await createWorldTerrainAsync();
      
      // 2. Load High-Res Imagery
      const imagery = await createWorldImageryAsync({
        style: IonWorldImageryStyle.AERIAL_WITH_LABELS,
      });
      viewer.imageryLayers.removeAll();
      viewer.imageryLayers.addImageryProvider(imagery);
      
      // 3. Load Highest Quality Buildings (Google Photorealistic 3D Tiles)
      try {
        console.log("[CESIUM] Loading Google Photorealistic 3D Tiles...");
        const googleTileset = await createGooglePhotorealistic3DTileset();
        viewer.scene.primitives.add(googleTileset);
      } catch (ge) {
        console.warn("[CESIUM] Google Tiles failed, falling back to OSM Buildings", ge);
        const osmBuildings = await createOsmBuildingsAsync();
        viewer.scene.primitives.add(osmBuildings);
      }
      
      console.log("[CESIUM] Baseline stack initialized.");
    } else {
      throw new Error("No Ion Token");
    }
  } catch (e) {
    console.error("[CESIUM] High-fidelity load failed, falling back to OSM", e);
    viewer.imageryLayers.removeAll();
    viewer.imageryLayers.addImageryProvider(new OpenStreetMapImageryProvider({
      url: 'https://a.tile.openstreetmap.org/'
    }));
    viewer.terrainProvider = new EllipsoidTerrainProvider();
  }

  scene.backgroundColor = Color.fromCssColorString('#000000');
  scene.fog.enabled = false;
}
