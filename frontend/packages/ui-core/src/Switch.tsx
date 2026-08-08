import React from 'react';

export interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  className?: string;
}

export const Switch: React.FC<SwitchProps> = ({
  checked,
  onChange,
  label,
  className = '',
}) => {
  return (
    <label className={`inline-flex items-center gap-2 cursor-pointer font-mono text-xs select-none ${className}`}>
      <div
        onClick={() => onChange(!checked)}
        className={`w-8 h-4.5 rounded-full transition-colors relative p-0.5 border ${
          checked ? 'bg-sky-600 border-sky-500' : 'bg-slate-900 border-slate-800'
        }`}
      >
        <div
          className={`w-3.5 h-3.5 rounded-full bg-white transition-transform ${
            checked ? 'translate-x-3.5' : 'translate-x-0'
          }`}
        />
      </div>
      {label && <span className="text-slate-300 text-[11px]">{label}</span>}
    </label>
  );
};
