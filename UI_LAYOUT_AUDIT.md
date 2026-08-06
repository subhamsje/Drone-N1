# Altaria UI Layout Audit

## 1. Subsystem Layout Investigation

### Header (`CommandHUD`)
- **Current State**: `relative` inside `MapNativeShell`, but siblings are `absolute`.
- **Violations**: Does not use standard document flow. Overlaps with `SystemStatusHud` which is `absolute top-0`.
- **Responsive Risk**: Overlaps center controls on narrow viewports.

### System Status HUD
- **Current State**: `absolute top-0 z-30`.
- **Violations**: Hardcoded `top-0` forces it to cover the actual application header or be covered by it. Viewport violation at 1366px.

### Sidebar (`AltariaCommandCenter`)
- **Current State**: `absolute left-0 top-14`.
- **Violations**: Linked to hardcoded `top-14` which breaks if header height changes. Height is `calc(100%-8rem)`, which is brittle.

### Diagnostics Panel
- **Current State**: `absolute bottom-3 right-3`.
- **Violations**: Overlaps with the `ReplayTimeline` footer. The user reports clipping; likely caused by the parent container `absolute inset-0 top-14` not accounting for the footer height properly or being pushed down.

### Viewport & Clipping
- **Diagnostics Panel**: Truncated at the bottom. Only "IMAGERY PROVIDER" visible.
- **Z-Index Conflicts**: `SystemStatusHud` (z-30) vs `CommandHUD` (z-20). 

## 2. Remediation Plan

- **Phase 1**: Rebuild `MapNativeShell` as a `flex flex-col`. 
  - Row 1: `SystemStatusHud`
  - Row 2: `CommandHUD` (Header)
  - Row 3: `flex-1 relative` (Main Body)
- **Phase 2**: Move `DiagnosticsPanel` to a stable corner that doesn't conflict with the footer, or adjust footer padding.
- **Phase 3**: Implement `viewMode` logic in `MapNativeShell` to actually switch between Planet/Twin/Dual.
- **Phase 4**: Map Status clicks to drawers.
