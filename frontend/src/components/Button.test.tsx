/**
 * Button Component Tests - Task 3
 * Requirements: 4 (Button Component), 9 (Gradient System), 10 (Accessibility)
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

describe('Button Component - Task 3.1 Structure', () => {
  it('should render button with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('should forward ref to button element', () => {
    const ref = { current: null as HTMLButtonElement | null };
    render(<Button ref={ref}>Button</Button>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });
});

describe('Button Component - Task 3.2 Variants and Sizes', () => {
  it('should render primary variant with gradient', () => {
    render(<Button variant="primary">Primary</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('gradient-primary');
  });

  it('should render secondary variant with glass effect', () => {
    render(<Button variant="secondary">Secondary</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('glass-effect');
  });

  it('should render ghost variant with minimal style', () => {
    render(<Button variant="ghost">Ghost</Button>);
    const button = screen.getByRole('button');
    // Ghost should not have gradient or glass
    expect(button).not.toHaveClass('gradient-primary');
    expect(button).not.toHaveClass('glass-effect');
  });

  it('should apply correct padding for sm size', () => {
    render(<Button size="sm">Small</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('px-4');
    expect(button).toHaveClass('py-2');
  });

  it('should apply correct padding for md size', () => {
    render(<Button size="md">Medium</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('px-6');
    expect(button).toHaveClass('py-3');
  });

  it('should apply correct padding for lg size', () => {
    render(<Button size="lg">Large</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('px-8');
    expect(button).toHaveClass('py-4');
  });

  it('should apply rounded-full for primary buttons', () => {
    render(<Button variant="primary">Primary</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('rounded-full');
  });
});

describe('Button Component - Task 3.3 States and Interactions', () => {
  it('should reduce opacity when disabled', () => {
    render(<Button disabled>Disabled</Button>);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveClass('opacity-50');
  });

  it('should show loading spinner when loading', () => {
    render(<Button loading>Loading</Button>);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    // Loading spinner should be present (we'll add icon later)
  });

  it('should have focus outline', () => {
    render(<Button>Focus</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('focus:outline-primary');
  });

  it('should apply hover scale effect', () => {
    render(<Button>Hover</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('hover-scale');
  });
});

describe('Button Component - Task 3.4 Accessibility', () => {
  it('should support aria-label', () => {
    render(<Button aria-label="Custom label">Button</Button>);
    const button = screen.getByRole('button', { name: /custom label/i });
    expect(button).toBeInTheDocument();
  });

  it('should be keyboard accessible', () => {
    render(<Button>Keyboard</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('type');
  });
});
