import React from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'cyber';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'secondary',
  size = 'md',
  loading = false,
  icon,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-mono font-medium rounded-lg transition-all select-none focus:outline-none focus:ring-1 focus:ring-sky-500/50 disabled:opacity-50 disabled:cursor-not-allowed';

  const sizeStyles = {
    sm: 'px-2.5 py-1 text-[11px] gap-1.5',
    md: 'px-3.5 py-1.5 text-xs gap-2',
    lg: 'px-4 py-2 text-sm gap-2.5',
  }[size];

  const variantStyles = {
    primary: 'bg-sky-600 hover:bg-sky-500 text-white shadow-md shadow-sky-600/20 active:scale-[0.98]',
    secondary: 'bg-slate-900/80 hover:bg-slate-800 text-slate-200 border border-slate-800 hover:border-slate-700 active:scale-[0.98]',
    danger: 'bg-rose-600/20 hover:bg-rose-600/40 text-rose-300 border border-rose-500/40 active:scale-[0.98]',
    ghost: 'bg-transparent hover:bg-slate-800/60 text-slate-400 hover:text-slate-200',
    cyber: 'bg-purple-600/20 hover:bg-purple-600/40 text-purple-200 border border-purple-500/40 active:scale-[0.98]',
  }[variant];

  return (
    <button
      className={`${baseStyles} ${sizeStyles} ${variantStyles} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : icon}
      <span>{children}</span>
    </button>
  );
};
