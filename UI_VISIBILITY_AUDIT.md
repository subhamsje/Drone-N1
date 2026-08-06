# Altaria OMEGA UI Visibility Audit — Phase 4

## 1. Resolution Stress Test

| Resolution | Clipping Detected | Overlap Found | Inaccessible Controls | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **1366x768** | YES (Sidebar + HUD) | YES (Mission Ribbon) | NO | ⚠️ WARNING |
| **1440x900** | NO | NO | NO | ✓ PASS |
| **1920x1080** | NO | NO | NO | ✓ PASS |
| **2560x1440** | NO | NO | NO | ✓ PASS |

## 2. Component Visibility Status

- **Planetary Globe**: [VISIBLE] Full viewport coverage.
- **Cognitive Twin**: [VISIBLE] Side-by-side dual mode stable.
- **Mission Command**: [VISIBLE] Sidebar logic correctly pushes map.
- **Command HUD**: [VISIBLE] Transparent overlay correctly positioned.
- **Replay Timeline**: [VISIBLE] Fixed footer prevents map occlusion.
- **Analytics Overlay**: [VISIBLE] Fullscreen backdrop blur active.

## 3. Critical UI Findings
1. **Low Res Clipping**: At 1366x768, the `MissionCommandRibbon` (absolute bottom-center) overlaps with the `ReplayTimeline` footer.
2. **Absolute Overflow**: The `SystemDetailDrawer` uses `absolute top-0 right-0 h-full w-80`. In narrow viewports, this covers 30% of the active command area.
3. **Z-Index Stability**: `TelemetryLakeOverlay` uses `z-40` while `SystemDetailDrawer` uses `z-50`. The drawer correctly appears over the analytics layer.

## 4. Remediation Plan
1. **Flex-Box Refactor**: Convert `MapNativeShell` from absolute positioning to a proper flex-col/row grid to prevent ribbon-footer collision.
2. **Media Queries**: Implement Tailwind `sm:hidden` or dynamic width for the sidebar at <1024px width.

**Status**: PARTIALLY VISIBLE — 1366x768 requires layout hardening.
