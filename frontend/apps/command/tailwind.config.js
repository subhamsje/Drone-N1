/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['IBM Plex Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        cognition: { DEFAULT: '#22d3a8', dim: '#0d9488' },
        survival: { DEFAULT: '#f5b942', dim: '#b45309' },
      },
    },
  },
  plugins: [],
};
