/**
 * Input Component - Task 5
 * Requirements: 6 (Input Component), 10 (Accessibility)
 */
import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /** Input label displayed above field */
  label?: string;

  /** Error message displayed below field */
  error?: string;

  /** Input type */
  type?: 'text' | 'email' | 'password' | 'search';

  /** Optional ARIA label for accessibility */
  'aria-label'?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, type = 'text', className = '', id, ...props }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const errorId = error ? `${inputId}-error` : undefined;

    const focusClass = error
      ? 'border-b-2 border-b-red-500 focus:border-b-red-500'
      : 'border-b-2 border-b-transparent focus:border-b-primary';

    const inputClasses = `
      w-full bg-transparent
      px-4 py-3
      text-on-surface placeholder:text-on-surface-variant/50
      ${focusClass}
      outline-none transition-colors
      disabled:opacity-50 disabled:cursor-not-allowed
      ${className}
    `.trim().replace(/\s+/g, ' ');

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-label text-on-surface-variant mb-2">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          type={type}
          className={inputClasses}
          aria-describedby={errorId}
          aria-invalid={!!error}
          {...props}
        />
        {error && (
          <p id={errorId} className="mt-1 text-sm text-red-500" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
