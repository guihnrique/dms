/**
 * Card Component Tests - Task 4
 * Requirements: 3 (Glassmorphism), 5 (Card Component), 10 (Accessibility), 14 (Performance)
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card } from './Card';

describe('Card Component - Task 4.1: Basic Rendering', () => {
  it('should render children content', () => {
    render(
      <Card>
        <Card.Content>Test Content</Card.Content>
      </Card>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should apply glassmorphism effect by default', () => {
    const { container } = render(
      <Card>
        <Card.Content>Glass Card</Card.Content>
      </Card>
    );

    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass('glass-effect');
  });

  it('should apply solid background when glass prop is false', () => {
    const { container } = render(
      <Card glass={false}>
        <Card.Content>Solid Card</Card.Content>
      </Card>
    );

    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass('bg-surface-container');
    expect(cardElement).not.toHaveClass('glass-effect');
  });

  it('should have rounded-xl corners', () => {
    const { container } = render(
      <Card>
        <Card.Content>Rounded Card</Card.Content>
      </Card>
    );

    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass('rounded-xl');
  });
});

describe('Card Component - Task 4.2: Interactive Features', () => {
  it('should not apply hover effect by default', () => {
    const { container } = render(
      <Card>
        <Card.Content>Non-interactive Card</Card.Content>
      </Card>
    );

    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).not.toHaveClass('hover-scale');
    expect(cardElement).not.toHaveClass('cursor-pointer');
  });

  it('should apply hover scale and pointer when interactive', () => {
    const { container } = render(
      <Card interactive>
        <Card.Content>Interactive Card</Card.Content>
      </Card>
    );

    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass('hover-scale');
    expect(cardElement).toHaveClass('cursor-pointer');
  });

  it('should accept custom className', () => {
    const { container } = render(
      <Card className="custom-class">
        <Card.Content>Custom Card</Card.Content>
      </Card>
    );

    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass('custom-class');
  });
});

describe('Card Component - Task 4.3: Image Support', () => {
  it('should render image with lazy loading', () => {
    render(
      <Card imageSrc="/test-image.jpg" imageAlt="Test Image">
        <Card.Content>Card with Image</Card.Content>
      </Card>
    );

    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('src', '/test-image.jpg');
    expect(image).toHaveAttribute('alt', 'Test Image');
    expect(image).toHaveAttribute('loading', 'lazy');
  });

  it('should render image without alt when not provided', () => {
    const { container } = render(
      <Card imageSrc="/test-image.jpg">
        <Card.Content>Card with Image</Card.Content>
      </Card>
    );

    const image = container.querySelector('img');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('alt', '');
  });

  it('should not render image when imageSrc not provided', () => {
    render(
      <Card>
        <Card.Content>Card without Image</Card.Content>
      </Card>
    );

    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  it('should have full-width responsive image', () => {
    render(
      <Card imageSrc="/test-image.jpg" imageAlt="Responsive">
        <Card.Content>Responsive Card</Card.Content>
      </Card>
    );

    const image = screen.getByRole('img');
    expect(image).toHaveClass('w-full');
    expect(image).toHaveClass('h-auto');
  });
});

describe('Card Component - Task 4.4: Compound Components', () => {
  it('should render Card.Header with content', () => {
    render(
      <Card>
        <Card.Header>Header Content</Card.Header>
      </Card>
    );

    expect(screen.getByText('Header Content')).toBeInTheDocument();
  });

  it('should render Card.Content with content', () => {
    render(
      <Card>
        <Card.Content>Body Content</Card.Content>
      </Card>
    );

    expect(screen.getByText('Body Content')).toBeInTheDocument();
  });

  it('should render Card.Footer with content', () => {
    render(
      <Card>
        <Card.Footer>Footer Content</Card.Footer>
      </Card>
    );

    expect(screen.getByText('Footer Content')).toBeInTheDocument();
  });

  it('should render all sections together', () => {
    render(
      <Card>
        <Card.Header>Header</Card.Header>
        <Card.Content>Content</Card.Content>
        <Card.Footer>Footer</Card.Footer>
      </Card>
    );

    expect(screen.getByText('Header')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
    expect(screen.getByText('Footer')).toBeInTheDocument();
  });

  it('should apply custom className to Header', () => {
    const { container } = render(
      <Card>
        <Card.Header className="custom-header">Header</Card.Header>
      </Card>
    );

    const header = container.querySelector('.custom-header');
    expect(header).toBeInTheDocument();
    expect(header).toHaveClass('p-4');
  });

  it('should apply custom className to Content', () => {
    const { container } = render(
      <Card>
        <Card.Content className="custom-content">Content</Card.Content>
      </Card>
    );

    const content = container.querySelector('.custom-content');
    expect(content).toBeInTheDocument();
    expect(content).toHaveClass('p-4');
  });

  it('should apply custom className to Footer', () => {
    const { container } = render(
      <Card>
        <Card.Footer className="custom-footer">Footer</Card.Footer>
      </Card>
    );

    const footer = container.querySelector('.custom-footer');
    expect(footer).toBeInTheDocument();
    expect(footer).toHaveClass('p-4');
  });
});
