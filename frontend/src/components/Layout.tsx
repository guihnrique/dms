/**
 * Layout Component - Task 8
 * Requirements: 11 (Responsive Design), 14 (Performance)
 */
import React from 'react';

export interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Container content */
  children: React.ReactNode;
}

export interface GridProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Number of columns (desktop) */
  cols?: number;

  /** Gap between grid items */
  gap?: number;

  /** Grid content */
  children: React.ReactNode;
}

const Container: React.FC<ContainerProps> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <div
      className={`container mx-auto px-4 ${className}`.trim()}
      {...props}
    >
      {children}
    </div>
  );
};

const Grid: React.FC<GridProps> = ({
  children,
  cols = 12,
  gap = 6,
  className = '',
  ...props
}) => {
  const colsClass = `grid-cols-1 md:grid-cols-${cols}`;
  const gapClass = `gap-${gap}`;

  return (
    <div
      className={`grid ${colsClass} ${gapClass} ${className}`.trim()}
      {...props}
    >
      {children}
    </div>
  );
};

interface LayoutSubComponents {
  Container: React.FC<ContainerProps>;
  Grid: React.FC<GridProps>;
}

export const Layout = {
  Container,
  Grid,
} as LayoutSubComponents;
