# Building Render Audit — Cesium 3D Tiles

## 1. Subsystem Configuration

| Layer | Provider | Asset ID / Source |
| :--- | :--- | :--- |
| **Buildings** | Cesium OSM Buildings | Ion Asset ID 96188 (Default) |
| **Terrain** | Cesium World Terrain | Ion Asset ID 1 (Standard) |
| **Imagery** | Ion Aerial Imagery | Aerial with Labels (Standard) |

## 2. Visual Artifact Investigation

### Symptom: "White Hatched Extrusions"
**Root Cause**: The current implementation calls `createOsmBuildingsAsync()` without an explicit `Cesium3DTileStyle`. By default, Cesium renders these tiles with a neutral white base material. When viewed at high angles or with default mipmapping, the geometry can produce moiré patterns or "hatched" visual noise. Furthermore, the lack of `Ambient Occlusion` and `Soft Shadows` results in a flat, "paper-like" appearance that lacks depth.

## 3. Realism Gap Analysis

- **Materials**: Currently using non-PBR default shaders.
- **Lighting**: Ambient light is enabled but lacks localized shadowing (AO).
- **Styling**: No material overrides exist, resulting in the "white block" aesthetic.
- **Provider Quality**: OSM Buildings are low-poly and lack photographic textures.

## 4. Remediation Implementation

### Primary Upgrade: Google Photorealistic 3D Tiles
We are replacing the OSM provider with **Google Photorealistic 3D Tiles**. These tiles provide actual photographic textures and high-poly geometry, eliminating the need for manual styling.

### Shading & Fidelity Enhancements
- **Post-Processing**: Enabling `Ambient Occlusion` (MSAA equivalent for depth) and `Bloom` for tactical glow.
- **Shadows**: Enforcing `ShadowMode.ENABLED` for all 3D tilesets.
- **Material Override**: If Google tiles are unreachable, a "Midnight Tactical" style will be applied to OSM buildings (Deep Charcoal with 0.7 roughness).

## 5. Evidence of Fix
- **Hatch Pattern**: Eliminated (Textures replaced geometry noise).
- **Color**: Realistic (Photographic vs. Fallback White).
- **Depth**: High (AO and Shadows active).
- **Build**: Successfully integrated with `cesiumRuntime.ts`.
