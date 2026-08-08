/**
 * Altaria UI Design System Tokens
 */

export const colors = {
  bg: "#010409",
  surface: "#0b1220",
  surfaceCard: "#111827",
  glass: "rgba(255,255,255,0.05)",

  primary: "#38bdf8",
  success: "#10b981",
  danger: "#f43f5e",
  warning: "#f59e0b",
  info: "#6366f1",

  border: "rgba(51, 65, 85, 0.6)",
  borderSubtle: "rgba(51, 65, 85, 0.3)",

  text: "#e5e7eb",
  textMuted: "#94a3b8",
  textDim: "#64748b",
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  "2xl": 32,
} as const;

export const radius = {
  sm: 6,
  md: 10,
  lg: 16,
  full: 9999,
} as const;

export const motion = {
  fast: 150,
  base: 220,
  slow: 320,
} as const;
