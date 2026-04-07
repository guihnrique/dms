/**
 * Icon Component - Task 6
 * Requirements: 7 (Icon System), 10 (Accessibility)
 */
import React from 'react';

export interface IconProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Material Symbols icon name */
  name: string;

  /** Icon size */
  size?: 'sm' | 'md' | 'lg' | 'xl';

  /** Optional ARIA label for semantic icons */
  'aria-label'?: string;

  /** Mark icon as decorative (hidden from screen readers) */
  decorative?: boolean;
}

export const Icon: React.FC<IconProps> = ({
  name,
  size = 'md',
  'aria-label': ariaLabel,
  decorative = true,
  className = '',
  ...props
}) => {
  const sizeClasses = {
    sm: 'text-base',  // 16px
    md: 'text-2xl',   // 24px
    lg: 'text-4xl',   // 32px
    xl: 'text-6xl',   // 48px
  };

  return (
    <span
      className={`material-symbols-outlined ${sizeClasses[size]} ${className}`.trim()}
      style={{ fontVariationSettings: "'wght' 200" }}
      aria-label={!decorative ? ariaLabel : undefined}
      aria-hidden={decorative ? true : undefined}
      {...props}
    >
      {name}
    </span>
  );
};
