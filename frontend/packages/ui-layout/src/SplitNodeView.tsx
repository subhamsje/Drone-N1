import React, { useRef } from 'react';
import { SplitNode, LayoutNode } from './layoutTree';
import { useWorkspaceLayoutStore } from './useWorkspaceLayoutStore';
import { LeafNodeView } from './LeafNodeView';

export interface SplitNodeViewProps {
  node: LayoutNode;
  renderTabContent: (tabId: string) => React.ReactNode;
}

export const SplitNodeView: React.FC<SplitNodeViewProps> = ({ node, renderTabContent }) => {
  const { updateSplitRatio } = useWorkspaceLayoutStore();
  const splitRef = useRef<HTMLDivElement>(null);

  if (node.type === 'leaf') {
    return <LeafNodeView node={node} renderTabContent={renderTabContent} />;
  }

  const isHoriz = node.direction === 'horizontal';

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    const startX = e.clientX;
    const startY = e.clientY;
    const startRatio = node.ratio;

    if (!splitRef.current) return;
    const rect = splitRef.current.getBoundingClientRect();
    const totalLength = isHoriz ? rect.width : rect.height;

    let frameId: number | null = null;

    const onMouseMove = (moveEvt: MouseEvent) => {
      if (frameId) cancelAnimationFrame(frameId);

      frameId = requestAnimationFrame(() => {
        const delta = isHoriz ? moveEvt.clientX - startX : moveEvt.clientY - startY;
        const deltaRatio = delta / totalLength;
        updateSplitRatio(node.id, startRatio + deltaRatio);
      });
    };

    const onMouseUp = () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      if (frameId) cancelAnimationFrame(frameId);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  return (
    <div
      ref={splitRef}
      className={`h-full w-full flex ${isHoriz ? 'flex-row' : 'flex-col'} overflow-hidden relative`}
    >
      {/* First Sub-Node */}
      <div style={{ flex: node.ratio }} className="overflow-hidden relative">
        <SplitNodeView node={node.first} renderTabContent={renderTabContent} />
      </div>

      {/* Interactive Resize Splitter Handle */}
      <div
        onMouseDown={handleMouseDown}
        className={`group relative z-30 shrink-0 select-none ${
          isHoriz
            ? 'w-1.5 cursor-col-resize hover:bg-sky-500/80 bg-slate-800/80'
            : 'h-1.5 cursor-row-resize hover:bg-sky-500/80 bg-slate-800/80'
        } transition-colors flex items-center justify-center`}
      >
        <div
          className={`${
            isHoriz ? 'w-0.5 h-6' : 'h-0.5 w-6'
          } rounded-full bg-slate-600 group-hover:bg-white transition-colors`}
        />
      </div>

      {/* Second Sub-Node */}
      <div style={{ flex: 1 - node.ratio }} className="overflow-hidden relative">
        <SplitNodeView node={node.second} renderTabContent={renderTabContent} />
      </div>
    </div>
  );
};
