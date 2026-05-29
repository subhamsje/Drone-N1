/** WebGL context loss recovery for cognition render domains */
export function attachGpuLifecycle(canvas: HTMLCanvasElement, onDegraded: () => void): () => void {
  const onLost = (e: Event) => {
    e.preventDefault();
    onDegraded();
  };
  const onRestored = () => {
    /* R3F/Cesium will re-init on next frame */
  };
  canvas.addEventListener('webglcontextlost', onLost, false);
  canvas.addEventListener('webglcontextrestored', onRestored, false);
  return () => {
    canvas.removeEventListener('webglcontextlost', onLost);
    canvas.removeEventListener('webglcontextrestored', onRestored);
  };
}
