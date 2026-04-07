/**
 * Confirm Modal - Reusable confirmation dialog
 */

import { Icon } from './Icon';

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmButtonClass?: string;
  loading?: boolean;
}

export function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  confirmButtonClass = 'bg-error text-on-error',
  loading = false,
}: ConfirmModalProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-surface-container rounded-3xl shadow-2xl max-w-md w-full overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-outline-variant/10">
          <h3 className="font-headline text-2xl font-bold text-white">
            {title}
          </h3>
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="text-on-surface-variant">{message}</p>
        </div>

        {/* Actions */}
        <div className="flex gap-3 p-6 border-t border-outline-variant/10">
          <button
            onClick={onClose}
            disabled={loading}
            className="flex-1 px-6 py-3 rounded-full bg-surface-bright hover:bg-surface-container-highest text-white font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className={`flex-1 px-6 py-3 rounded-full font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed ${confirmButtonClass} hover:scale-105`}
          >
            {loading ? (
              <div className="flex items-center justify-center gap-2">
                <Icon
                  name="refresh"
                  size="sm"
                  className="animate-spin"
                  decorative
                />
                Processando...
              </div>
            ) : (
              confirmText
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
