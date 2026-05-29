import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import cesium from 'vite-plugin-cesium';
import path from 'path';

const cesiumRoot = path.resolve(__dirname, '../../node_modules/cesium/Build');

export default defineConfig({
  plugins: [
    react(),
    cesium({
      cesiumBuildRootPath: cesiumRoot,
      cesiumBuildPath: path.join(cesiumRoot, 'Cesium'),
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/ws': {
        target: 'ws://127.0.0.1:8080',
        ws: true,
        changeOrigin: true,
        timeout: 60000,
      },
    },
  },
});
