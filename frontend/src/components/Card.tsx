/**
 * Card Component - Task 4
 * Requirements: 3 (Glassmorphism), 5 (Card Component), 10 (Accessibility), 14 (Performance)
 */
import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Apply glassmorphism effect */
  glass?: boolean;

  /** Enable hover scale effect */
  interactive?: boolean;

  /** Optional image source with lazy loading */
  imageSrc?: string;

  /** Image alt text for accessibility */
  imageAlt?: string;

  /** Card content */
  children: React.ReactNode;
}

interface CardSubComponents {
  Header: React.FC<{ children: React.ReactNode; className?: string }>;
  Content: React.FC<{ children: React.ReactNode; className?: string }>;
  Footer: React.FC<{ children: React.ReactNode; className?: string }>;
}

const CardBase: React.FC<CardProps> = ({
  glass = true,
  interactive = false,
  imageSrc,
  imageAlt,
  children,
  className = '',
  ...props
}) => {
  const glassClass = glass ? 'glass-effect' : 'bg-surface-container';
  const interactiveClass = interactive ? 'hover-scale cursor-pointer' : '';

  return (
    <div
      className={`rounded-xl overflow-hidden ${glassClass} ${interactiveClass} ${className}`.trim()}
      {...props}
    >
      {imageSrc && (
        <img
          src={imageSrc}
          alt={imageAlt || ''}
          loading="lazy"
          className="w-full h-auto"
        />
      )}
      {children}
    </div>
  );
};

const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => <div className={`p-4 ${className}`.trim()}>{children}</div>;

const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => <div className={`p-4 ${className}`.trim()}>{children}</div>;

const CardFooter: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className = '',
}) => <div className={`p-4 ${className}`.trim()}>{children}</div>;

export const Card = Object.assign(CardBase, {
  Header: CardHeader,
  Content: CardContent,
  Footer: CardFooter,
}) as React.FC<CardProps> & CardSubComponents;
