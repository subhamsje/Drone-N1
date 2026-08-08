import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  unitSuffix?: string;
}

export const Input: React.FC<InputProps> = ({
  label,
  unitSuffix,
  className = '',
  ...props
}) => {
  return (
    <div className="space-y-1 font-mono text-xs">
      {label && <label className="block text-[10px] uppercase font-semibold text-slate-400">{label}</label>}
      <div className="relative flex items-center">
        <input
          className={`w-full bg-[#050811] border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 text-xs focus:border-sky-500/80 focus:outline-none transition-colors ${
            unitSuffix ? 'pr-10' : ''
          } ${className}`}
          {...props}
        />
        {unitSuffix && (
          <span className="absolute right-2.5 text-[10px] text-slate-500 pointer-events-none">
            {unitSuffix}
          </span>
        )}
      </div>
    </div>
  );
};
