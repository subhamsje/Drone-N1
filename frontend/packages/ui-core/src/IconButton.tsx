import React from 'react';

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  variant = 'secondary',
  size = 'md',
  className = '',
  ...props
}) => {
  const sizeClasses = {
    sm: 'p-1 text-xs rounded-md',
    md: 'p-1.5 text-sm rounded-lg',
    lg: 'p-2 text-base rounded-xl',
  }[size];

  const variantClasses = {
    primary: 'bg-sky-600 hover:bg-sky-500 text-white',
    secondary: 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border border-slate-800',
    danger: 'bg-rose-500/20 hover:bg-rose-500/40 text-rose-300 border border-rose-500/30',
    ghost: 'hover:bg-slate-800/60 text-slate-400 hover:text-slate-200',
  }[variant];

  return (
    <button
      className={`inline-flex items-center justify-center transition-all select-none active:scale-95 ${sizeClasses} ${variantClasses} ${className}`}
      {...props}
    >
      {icon}
    </button>
  );
};
