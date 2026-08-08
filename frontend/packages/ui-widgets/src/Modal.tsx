import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { IconButton } from '../../ui-core/src/IconButton';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  maxWidth = 'lg',
}) => {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const widthClass = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
  }[maxWidth];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div
        className={`w-full ${widthClass} rounded-2xl bg-[#0d131f] border border-slate-800 shadow-2xl overflow-hidden flex flex-col font-mono text-xs select-none`}
      >
        <div className="h-12 px-5 bg-[#111827] border-b border-slate-800 flex items-center justify-between">
          <h3 className="font-bold text-slate-100 text-sm tracking-tight">{title}</h3>
          <IconButton icon={<X className="w-4 h-4" />} variant="ghost" size="sm" onClick={onClose} />
        </div>
        <div className="p-5 overflow-y-auto max-h-[80vh]">{children}</div>
      </div>
    </div>
  );
};
