/**
 * Icon Component Tests - Task 6
 * Requirements: 7 (Icon System), 10 (Accessibility)
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Icon } from './Icon';

describe('Icon Component - Task 6.1: Basic Rendering', () => {
  it('should render icon with Material Symbols class', () => {
    const { container } = render(<Icon name="home" />);

    const icon = container.firstChild as HTMLElement;
    expect(icon).toHaveClass('material-symbols-outlined');
  });

  it('should render icon name as text content', () => {
    render(<Icon name="search" />);

    expect(screen.getByText('search')).toBeInTheDocument();
  });

  it('should apply medium size by default', () => {
    const { container } = render(<Icon name="menu" />);

    const icon = container.firstChild as HTMLElement;
    expect(icon).toHaveClass('text-2xl'); // md = 24px
  });

  it('should apply small size when specified', () => {
    const { container } = render(<Icon name="close" size="sm" />);

    const icon = container.firstChild as HTMLElement;
    expect(icon).toHaveClass('text-base'); // sm = 16px
  });

  it('should apply large size when specified', () => {
    const { container } = render(<Icon name="settings" size="lg" />);

    const icon = container.firstChild as HTMLElement;
    expect(icon).toHaveClass('text-4xl'); // lg = 32px
  });

  it('should apply thin stroke weight (200)', () => {
    const { container } = render(<Icon name="star" />);

    const icon = container.firstChild as HTMLElement;
    const style = icon.getAttribute('style');
    expect(style).toContain("'wght' 200");
  });

  it('should accept custom className', () => {
    const { container } = render(<Icon name="favorite" className="custom-icon" />);

    const icon = container.firstChild as HTMLElement;
    expect(icon).toHaveClass('custom-icon');
    expect(icon).toHaveClass('material-symbols-outlined');
  });

  it('should render as span element', () => {
    const { container } = render(<Icon name="check" />);

    expect(container.firstChild?.nodeName).toBe('SPAN');
  });
});

describe('Icon Component - Task 6.2: Accessibility', () => {
  it('should be decorative (aria-hidden) by default', () => {
    const { container } = render(<Icon name="arrow_forward" />);

    const icon = container.firstChild as HTMLElement;
    // decorative=true by default, so aria-hidden should be true and no aria-label
    const ariaHidden = icon.getAttribute('aria-hidden');
    expect(ariaHidden).toBe('true');
    expect(icon).not.toHaveAttribute('aria-label');
  });

  it('should apply aria-label when decorative is false', () => {
    const { container } = render(
      <Icon name="delete" decorative={false} aria-label="Delete item" />
    );

    const icon = container.firstChild as HTMLElement;
    expect(icon).toHaveAttribute('aria-label', 'Delete item');
    expect(icon).not.toHaveAttribute('aria-hidden');
  });

  it('should remain decorative when decorative is explicitly true', () => {
    const { container } = render(
      <Icon name="info" decorative={true} aria-label="Should be ignored" />
    );

    const icon = container.firstChild as HTMLElement;
    expect(icon).toHaveAttribute('aria-hidden', 'true');
    expect(icon).not.toHaveAttribute('aria-label');
  });

  it('should support semantic icons with aria-label', () => {
    const { container } = render(
      <Icon name="warning" decorative={false} aria-label="Warning message" />
    );

    const icon = container.firstChild as HTMLElement;
    expect(icon).toHaveAttribute('aria-label', 'Warning message');
  });

  it('should accept additional HTML attributes', () => {
    const { container } = render(
      <Icon name="help" data-testid="help-icon" title="Help" />
    );

    const icon = container.firstChild as HTMLElement;
    expect(icon).toHaveAttribute('data-testid', 'help-icon');
    expect(icon).toHaveAttribute('title', 'Help');
  });
});

describe('Icon Component - Integration', () => {
  it('should combine size and custom className', () => {
    const { container } = render(
      <Icon name="notifications" size="lg" className="text-primary-dim" />
    );

    const icon = container.firstChild as HTMLElement;
    expect(icon).toHaveClass('text-4xl');
    expect(icon).toHaveClass('text-primary-dim');
  });

  it('should work with all Material Symbols icon names', () => {
    const iconNames = ['home', 'search', 'menu', 'close', 'arrow_forward'];

    iconNames.forEach(name => {
      const { container } = render(<Icon name={name} />);
      expect(container.firstChild).toHaveTextContent(name);
    });
  });

  it('should maintain consistent styling across sizes', () => {
    const sizes: Array<'sm' | 'md' | 'lg'> = ['sm', 'md', 'lg'];
    const expectedClasses = ['text-base', 'text-2xl', 'text-4xl'];

    sizes.forEach((size, index) => {
      const { container } = render(<Icon name="star" size={size} />);
      const icon = container.firstChild as HTMLElement;

      expect(icon).toHaveClass('material-symbols-outlined');
      expect(icon).toHaveClass(expectedClasses[index]);
      expect(icon.getAttribute('style')).toContain("'wght' 200");
    });
  });
});
