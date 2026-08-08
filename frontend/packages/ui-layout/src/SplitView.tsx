import React from 'react';

export interface SplitViewProps {
  direction?: 'horizontal' | 'vertical';
  primary: React.ReactNode;
  secondary: React.ReactNode;
  ratio?: number; // e.g. 0.7 for 70/30 split
  className?: string;
}

export const SplitView: React.FC<SplitViewProps> = ({
  direction = 'horizontal',
  primary,
  secondary,
  ratio = 0.7,
  className = '',
}) => {
  const isHoriz = direction === 'horizontal';

  return (
    <div className={`h-full w-full flex ${isHoriz ? 'flex-row' : 'flex-col'} overflow-hidden ${className}`}>
      <div style={{ flex: ratio }} className="overflow-hidden">
        {primary}
      </div>
      <div className={`${isHoriz ? 'w-px' : 'h-px'} bg-slate-800/80 shrink-0`} />
      <div style={{ flex: 1 - ratio }} className="overflow-hidden">
        {secondary}
      </div>
    </div>
  );
};
