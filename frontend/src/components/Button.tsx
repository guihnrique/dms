/**
 * Button Component - Task 3
 * Requirements: 4 (Button Component), 9 (Gradient System), 10 (Accessibility)
 */
import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button visual variant */
  variant?: 'primary' | 'secondary' | 'ghost';

  /** Button size */
  size?: 'sm' | 'md' | 'lg';

  /** Display loading spinner and disable interaction */
  loading?: boolean;

  /** Button label or content */
  children: React.ReactNode;

  /** Optional ARIA label for accessibility */
  'aria-label'?: string;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      children,
      className = '',
      disabled,
      type = 'button',
      ...props
    },
    ref
  ) => {
    // Variant styles
    const variantClasses = {
      primary: 'gradient-primary text-on-primary-fixed rounded-full',
      secondary: 'glass-effect text-on-surface border border-outline-variant/20',
      ghost: 'bg-transparent text-on-surface hover:bg-white/5',
    };

    // Size styles with mobile-first approach (Task 9.1)
    const sizeClasses = {
      sm: 'px-4 py-2 text-sm mobile-touch-target',
      md: 'px-6 py-3 text-base mobile-touch-target sm:w-auto mobile-button-full',
      lg: 'px-8 py-4 text-lg mobile-touch-target sm:w-auto mobile-button-full',
    };

    // State styles
    const stateClasses = loading || disabled ? 'opacity-50 cursor-not-allowed' : '';
    const interactionClasses = !(loading || disabled) ? 'hover-scale' : '';
    const focusClasses = 'focus:outline-2 focus:outline-primary focus:outline-offset-2';

    const buttonClasses = `
      ${variantClasses[variant]}
      ${sizeClasses[size]}
      ${stateClasses}
      ${interactionClasses}
      ${focusClasses}
      font-label font-medium
      transition-all duration-200
      ${className}
    `.trim().replace(/\s+/g, ' ');

    return (
      <button
        ref={ref}
        type={type}
        disabled={loading || disabled}
        className={buttonClasses}
        {...props}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            {children}
          </span>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
