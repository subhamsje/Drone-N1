import {
  Color,
  EllipsoidTerrainProvider,
  Ion,
  Viewer as CesiumViewer,
} from 'cesium';

let configured = false;

/** Avoid default Ion imagery (requires token → tile decode failures). */
export function ensureCesiumConfigured(): void {
  if (configured) return;
  configured = true;
  const token = import.meta.env.VITE_CESIUM_ION_TOKEN as string | undefined;
  if (token) {
    Ion.defaultAccessToken = token;
  }
}

export const cognitionTerrainProvider = new EllipsoidTerrainProvider();

/** Dark tactical globe — no raster tiles, no image decode failures. */
export function applyTacticalGlobe(viewer: CesiumViewer): void {
  ensureCesiumConfigured();
  const { globe } = viewer.scene;
  globe.show = true;
  globe.enableLighting = true;
  globe.showGroundAtmosphere = true;
  globe.baseColor = Color.fromCssColorString('#0c1222');
  viewer.scene.backgroundColor = Color.fromCssColorString('#020617');
  if (viewer.scene.skyAtmosphere) viewer.scene.skyAtmosphere.show = true;
  viewer.scene.fog.enabled = true;
  viewer.scene.fog.density = 2e-4;
}
