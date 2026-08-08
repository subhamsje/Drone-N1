import React from 'react';
import { useWorkspaceLayoutStore } from './useWorkspaceLayoutStore';
import { X, ArrowDownToLine, Move } from 'lucide-react';

export interface FloatingPanelContainerProps {
  renderTabContent: (tabId: string) => React.ReactNode;
}

export const FloatingPanelContainer: React.FC<FloatingPanelContainerProps> = ({
  renderTabContent,
}) => {
  const {
    floatingPanels,
    bringToFront,
    closeFloatingPanel,
    updateFloatingPosition,
    redockFloatingPanel,
  } = useWorkspaceLayoutStore();

  const handleDragHeader = (e: React.MouseEvent, panelId: string, initialX: number, initialY: number) => {
    e.preventDefault();
    bringToFront(panelId);

    const startClientX = e.clientX;
    const startClientY = e.clientY;

    const onMouseMove = (moveEvt: MouseEvent) => {
      const dx = moveEvt.clientX - startClientX;
      const dy = moveEvt.clientY - startClientY;
      updateFloatingPosition(panelId, initialX + dx, initialY + dy);
    };

    const onMouseUp = () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  return (
    <>
      {floatingPanels.map((panel) => (
        <div
          key={panel.id}
          onMouseDown={() => bringToFront(panel.id)}
          style={{
            left: panel.x,
            top: panel.y,
            width: panel.width,
            height: panel.height,
            zIndex: panel.zIndex,
          }}
          className="fixed rounded-2xl bg-[#0d131f] border border-slate-700/80 shadow-2xl shadow-black/80 flex flex-col overflow-hidden select-none font-mono text-xs backdrop-blur-2xl"
        >
          {/* Draggable Window Titlebar */}
          <div
            onMouseDown={(e) => handleDragHeader(e, panel.id, panel.x, panel.y)}
            className="h-10 px-4 bg-[#111827] border-b border-slate-800 flex items-center justify-between cursor-move shrink-0"
          >
            <div className="flex items-center space-x-2">
              <Move className="w-3.5 h-3.5 text-sky-400" />
              <span className="font-bold text-slate-100">{panel.title}</span>
            </div>

            <div className="flex items-center space-x-1">
              <button
                onClick={() => redockFloatingPanel(panel.id, 'leaf_main_viewport', 'center')}
                title="Re-dock into Workspace"
                className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-sky-300 transition-colors"
              >
                <ArrowDownToLine className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => closeFloatingPanel(panel.id)}
                title="Close Floating Window"
                className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-rose-400 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Floating Content Body */}
          <div className="flex-1 overflow-hidden relative">{renderTabContent(panel.tabId)}</div>
        </div>
      ))}
    </>
  );
};
