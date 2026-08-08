import React from 'react';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-3 h-3 border',
    md: 'w-4 h-4 border-2',
    lg: 'w-6 h-6 border-2',
  }[size];

  return (
    <div
      className={`inline-block rounded-full border-sky-400 border-t-transparent animate-spin ${sizeClasses} ${className}`}
    />
  );
};
