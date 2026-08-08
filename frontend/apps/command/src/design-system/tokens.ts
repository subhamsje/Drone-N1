/**
 * Altaria OS Design Tokens & System Specification.
 * Conforms to Apple System UI clarity + Google Material 3 consistency + Palantir Gotham density.
 */

export const colors = {
  // Background surfaces
  background: {
    base: '#080c14',       // Deep Matte Obsidian Slate
    surface: '#0d131f',    // Midnight Graphite Panel
    surfaceHover: '#131b2e',
    card: '#111827',       // Elevated Card Background
    cardElevated: '#172033',
    backdrop: 'rgba(8, 12, 20, 0.85)',
  },
  // Hairline borders
  border: {
    subtle: 'rgba(51, 65, 85, 0.4)',
    default: 'rgba(51, 65, 85, 0.65)',
    focus: 'rgba(56, 189, 248, 0.6)',
    active: 'rgba(56, 189, 248, 0.9)',
  },
  // Text hierarchy
  text: {
    primary: '#f8fafc',    // Pure Diamond Ice White
    secondary: '#94a3b8',  // Cool Titanium Slate
    muted: '#64748b',      // Muted Monospace Slate
    inverted: '#080c14',
  },
  // Semantic status colors
  status: {
    primary: '#38bdf8',    // Electric Sky Cyan
    success: '#10b981',    // Mint Emerald
    warning: '#f59e0b',    // Warm Topaz Amber
    danger: '#f43f5e',     // Crimson Ruby
    info: '#6366f1',       // Deep Sapphire Indigo
  },
  // Brand gradient
  brand: {
    gradient: 'linear-gradient(135deg, #38bdf8 0%, #6366f1 100%)',
    shadow: '0 4px 20px rgba(56, 189, 248, 0.15)',
  }
} as const;

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  '2xl': '32px',
} as const;

export const radii = {
  sm: '4px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  full: '9999px',
} as const;

export const elevation = {
  flat: 'none',
  low: '0 1px 3px rgba(0, 0, 0, 0.3)',
  medium: '0 4px 12px rgba(0, 0, 0, 0.4)',
  high: '0 12px 32px rgba(0, 0, 0, 0.6)',
  glowPrimary: '0 0 16px rgba(56, 189, 248, 0.25)',
  glowSuccess: '0 0 16px rgba(16, 185, 129, 0.25)',
  glowDanger: '0 0 16px rgba(244, 63, 94, 0.35)',
} as const;

export const zIndex = {
  base: 0,
  dock: 10,
  hud: 20,
  overlay: 30,
  modal: 50,
  palette: 100,
} as const;
