import { useEffect, useRef } from 'react';
import { Panel } from '@altaria/ui';
import { useCognitionStore } from '../stores/cognitionStore';
import { cognitionTime } from '../runtime/cognitionClock';

type Node = { id: string; x: number; y: number };
type Edge = { from: string; to: string; w: number };

export function SwarmTopology() {
  const swarm = useCognitionStore((s) => s.envelope?.swarm) as Record<string, unknown> | undefined;
  const emergent = swarm?.emergent as Record<string, unknown> | undefined;
  const graph = swarm?.cognition_graph as {
    nodes?: string[];
    edges?: Array<{ from: string; to: string; risk_coupling: number }>;
  } | undefined;
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef(0);

  const nodeIds = graph?.nodes ?? ['Alpha', 'Bravo', 'Charlie', 'Delta'];
  const edges: Edge[] =
    graph?.edges?.map((e) => ({ from: e.from, to: e.to, w: e.risk_coupling })) ??
    nodeIds.map((n, i) => ({
      from: n,
      to: nodeIds[(i + 1) % nodeIds.length],
      w: 0.3 + Number(emergent?.collective_confidence ?? 0.35) * 0.2,
    }));

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const nodes: Node[] = nodeIds.map((id, i) => {
      const a = (i / nodeIds.length) * Math.PI * 2 - Math.PI / 2;
      return { id: String(id), x: 0.5 + Math.cos(a) * 0.32, y: 0.5 + Math.sin(a) * 0.32 };
    });
    const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));

    const draw = () => {
      const w = canvas.width;
      const h = canvas.height;
      const t = cognitionTime();
      ctx.clearRect(0, 0, w, h);

      ctx.fillStyle = 'rgba(2, 6, 23, 0.85)';
      ctx.fillRect(0, 0, w, h);

      const cx = w / 2;
      const cy = h / 2;
      for (let ring = 0; ring < 3; ring++) {
        const phase = t * 1.8 - ring * 0.6;
        const radius = 28 + ((phase % 1) * 50);
        ctx.strokeStyle = `rgba(34, 211, 238, ${0.12 * (1 - (phase % 1))})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, Math.PI * 2);
        ctx.stroke();
      }

      edges.forEach((e, i) => {
        const a = byId[e.from] ?? nodes[0];
        const b = byId[e.to] ?? nodes[1];
        if (!a || !b) return;
        const pulse = 0.5 + 0.5 * Math.sin(t * 2.5 + i);
        const x1 = a.x * w;
        const y1 = a.y * h;
        const x2 = b.x * w;
        const y2 = b.y * h;
        const mx = (x1 + x2) / 2;
        const my = (y1 + y2) / 2 - 18 * pulse * e.w;

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.quadraticCurveTo(mx, my, x2, y2);
        ctx.strokeStyle = `rgba(34, 211, 238, ${0.15 + e.w * 0.5 * pulse})`;
        ctx.lineWidth = 1 + e.w * 2;
        ctx.stroke();
      });

      nodes.forEach((n, i) => {
        const pulse = 0.5 + 0.5 * Math.sin(t * 3 + i * 0.8);
        const x = n.x * w;
        const y = n.y * h;
        const r = 6 + pulse * 3;
        const g = ctx.createRadialGradient(x, y, 0, x, y, r * 3);
        g.addColorStop(0, 'rgba(34, 211, 238, 0.5)');
        g.addColorStop(1, 'rgba(34, 211, 238, 0)');
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(x, y, r * 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = `rgba(34, 211, 238, ${0.7 + pulse * 0.3})`;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#94a3b8';
        ctx.font = '9px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(n.id.slice(0, 6), x, y + r + 10);
      });

      ctx.strokeStyle = 'rgba(34, 211, 238, 0.25)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(cx, cy, 22 + Math.sin(t) * 4, 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
      ctx.beginPath();
      ctx.arc(cx, cy, 14, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#22d3ee';
      ctx.font = '8px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('CONSENSUS', cx, cy + 3);

      animRef.current = requestAnimationFrame(draw);
    };

    const resize = () => {
      const rect = canvas.parentElement?.getBoundingClientRect();
      if (rect) {
        canvas.width = rect.width * devicePixelRatio;
        canvas.height = rect.height * devicePixelRatio;
      }
    };
    resize();
    draw();
    window.addEventListener('resize', resize);
    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener('resize', resize);
    };
  }, [nodeIds.join(','), edges.length, emergent?.collective_confidence]);

  return (
    <Panel title="Collective Swarm Cognition" className="ops-panel-accent">
      <p className="mb-2 font-mono text-[10px] text-cyan-300">
        {(emergent?.emergent_action as string) ?? 'SYNCHRONIZING'} · conf{' '}
        {Number(emergent?.collective_confidence ?? 0).toFixed(2)}
      </p>
      <div className="relative h-36 w-full overflow-hidden rounded bg-slate-950">
        <canvas ref={canvasRef} className="h-full w-full" />
      </div>
      <ul className="mt-2 max-h-14 space-y-0.5 overflow-y-auto text-[9px] leading-tight text-slate-500">
        {(emergent?.decentralized_reasoning as string[] | undefined)?.slice(0, 4).map((r, i) => (
          <li key={i}>▸ {r}</li>
        ))}
      </ul>
    </Panel>
  );
}
