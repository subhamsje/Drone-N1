/**
 * Motion & Micro-Interaction System.
 * Apple-grade snappy, purpose-driven 150ms-250ms curves.
 */

export const motion = {
  durations: {
    instant: '75ms',
    fast: '150ms',
    normal: '200ms',
    slow: '300ms',
  },
  easings: {
    standard: 'cubic-bezier(0.16, 1, 0.3, 1)', // Smooth Apple Deceleration
    accelerate: 'cubic-bezier(0.4, 0, 1, 1)',
    decelerate: 'cubic-bezier(0, 0, 0.2, 1)',
    bounce: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
  },
  transitions: {
    default: 'all 150ms cubic-bezier(0.16, 1, 0.3, 1)',
    smooth: 'all 250ms cubic-bezier(0.16, 1, 0.3, 1)',
    transform: 'transform 150ms cubic-bezier(0.16, 1, 0.3, 1)',
    opacity: 'opacity 150ms ease-in-out',
    border: 'border-color 150ms ease-in-out, background-color 150ms ease-in-out',
  }
} as const;
