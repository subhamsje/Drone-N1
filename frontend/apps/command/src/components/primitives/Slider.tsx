import React from 'react';

export interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (val: number) => void;
  minLabel?: string;
  maxLabel?: string;
  className?: string;
}

export const Slider: React.FC<SliderProps> = ({
  label,
  value,
  min,
  max,
  step = 1,
  unit = '',
  onChange,
  minLabel,
  maxLabel,
  className = '',
}) => {
  return (
    <div className={`space-y-1.5 font-mono text-xs ${className}`}>
      <div className="flex items-center justify-between text-[11px]">
        <span className="text-slate-400">{label}</span>
        <span className="text-sky-400 font-bold">
          {value} {unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 bg-slate-800 rounded appearance-none cursor-pointer accent-sky-400 transition-all focus:outline-none"
      />
      {(minLabel || maxLabel) && (
        <div className="flex justify-between text-[9px] text-slate-500">
          <span>{minLabel || `${min} ${unit}`}</span>
          <span>{maxLabel || `${max} ${unit}`}</span>
        </div>
      )}
    </div>
  );
};
