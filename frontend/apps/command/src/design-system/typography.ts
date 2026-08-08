/**
 * Design System Typography Scale.
 * JetBrains Mono + Inter for maximum tabular precision and density.
 */

export const typography = {
  fonts: {
    sans: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    mono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
  },
  sizes: {
    micro: '9px',
    caption: '10px',
    xs: '11px',
    sm: '12px',
    base: '13px',
    md: '14px',
    lg: '16px',
    xl: '20px',
    '2xl': '24px',
    stat: '32px',
  },
  weights: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },
  lineHeights: {
    tight: '1.15',
    snug: '1.25',
    normal: '1.4',
    relaxed: '1.6',
  },
} as const;
