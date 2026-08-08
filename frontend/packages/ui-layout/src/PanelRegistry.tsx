import React, { lazy, Suspense } from 'react';
import { Globe2, Video, Box, GitMerge, LayoutDashboard, Gauge, Terminal, Clock } from 'lucide-react';

export interface TabMeta {
  id: string;
  title: string;
  icon: any;
}

export const TAB_REGISTRY: Record<string, TabMeta> = {
  globe: { id: 'globe', title: 'Planetary 3D', icon: Globe2 },
  fpv: { id: 'fpv', title: 'H.264 FPV HUD', icon: Video },
  twin: { id: 'twin', title: 'Digital Twin Sandbox', icon: Box },
  studio: { id: 'studio', title: 'Node Mission Studio', icon: GitMerge },
  ops: { id: 'ops', title: 'Operations Dashboard', icon: LayoutDashboard },
  pfd: { id: 'pfd', title: 'Primary Flight Display', icon: Gauge },
  telemetry: { id: 'telemetry', title: '50Hz MAVLink Console', icon: Terminal },
  timeline: { id: 'timeline', title: 'Cognitive Event Timeline', icon: Clock },
};
