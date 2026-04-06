/**
 * Navigation Component - Task 7
 * Requirements: 3 (Glassmorphism), 8 (Navigation Component), 10 (Accessibility)
 */
import React, { useState } from 'react';
import { Icon } from './Icon';

export interface NavigationProps extends React.HTMLAttributes<HTMLElement> {
  /** Navigation items */
  children: React.ReactNode;
}

export interface NavigationItemProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  /** Link destination */
  href: string;

  /** Mark as active route */
  active?: boolean;

  /** Link content */
  children: React.ReactNode;
}

const NavigationBase: React.FC<NavigationProps> = ({
  children,
  className = '',
  ...props
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <nav
      className={`glass-effect fixed top-0 left-0 right-0 z-50 ${className}`.trim()}
      {...props}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:gap-2">
            {React.Children.map(children, (child) => {
              if (React.isValidElement(child)) {
                return React.cloneElement(child, { onClick: undefined } as any);
              }
              return child;
            })}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-white/10 transition-colors focus:outline-2 focus:outline-primary"
            onClick={toggleMobileMenu}
            aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={mobileMenuOpen}
          >
            <Icon name={mobileMenuOpen ? 'close' : 'menu'} size="md" />
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div
            className="md:hidden glass-effect rounded-xl mt-2 mb-4 p-4 flex flex-col gap-2"
            data-testid="mobile-menu"
          >
            {React.Children.map(children, (child) => {
              if (React.isValidElement(child)) {
                return React.cloneElement(child, { onClick: closeMobileMenu } as any);
              }
              return child;
            })}
          </div>
        )}
      </div>
    </nav>
  );
};

const NavigationItem: React.FC<NavigationItemProps> = ({
  href,
  active = false,
  children,
  className = '',
  onClick,
  ...props
}) => {
  const activeClass = active ? 'bg-white/10' : '';

  return (
    <a
      href={href}
      className={`
        px-4 py-2 rounded-lg
        text-on-surface font-label
        hover:bg-white/10
        transition-colors
        focus:outline-2 focus:outline-primary focus:outline-offset-2
        ${activeClass}
        ${className}
      `.trim().replace(/\s+/g, ' ')}
      onClick={onClick}
      {...props}
    >
      {children}
    </a>
  );
};

interface NavigationSubComponents {
  Item: React.FC<NavigationItemProps>;
}

export const Navigation = Object.assign(NavigationBase, {
  Item: NavigationItem,
}) as React.FC<NavigationProps> & NavigationSubComponents;
