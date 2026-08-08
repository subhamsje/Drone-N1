import React from 'react';

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
}

export const Select: React.FC<SelectProps> = ({
  label,
  options,
  className = '',
  ...props
}) => {
  return (
    <div className="space-y-1 font-mono text-xs">
      {label && <label className="block text-[10px] uppercase font-semibold text-slate-400">{label}</label>}
      <select
        className={`w-full bg-[#050811] border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 text-xs focus:border-sky-500/80 focus:outline-none transition-colors cursor-pointer ${className}`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} className="bg-[#0b1220] text-slate-200">
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
};
