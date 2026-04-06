/**
 * Layout Component Tests - Task 8
 * Requirements: 11 (Responsive Design), 14 (Performance)
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Layout } from './Layout';

describe('Layout Component - Task 8.1: Container & Grid', () => {
  it('should render container with content', () => {
    render(
      <Layout.Container>
        <div>Test Content</div>
      </Layout.Container>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should apply container max-width classes', () => {
    const { container } = render(
      <Layout.Container>Content</Layout.Container>
    );

    const containerElement = container.firstChild as HTMLElement;
    expect(containerElement).toHaveClass('container');
    expect(containerElement).toHaveClass('mx-auto');
  });

  it('should apply horizontal padding to container', () => {
    const { container } = render(
      <Layout.Container>Content</Layout.Container>
    );

    const containerElement = container.firstChild as HTMLElement;
    expect(containerElement).toHaveClass('px-4');
  });

  it('should accept custom className on Container', () => {
    const { container } = render(
      <Layout.Container className="custom-container">Content</Layout.Container>
    );

    const containerElement = container.firstChild as HTMLElement;
    expect(containerElement).toHaveClass('custom-container');
    expect(containerElement).toHaveClass('container');
  });

  it('should render grid with content', () => {
    render(
      <Layout.Grid>
        <div>Item 1</div>
        <div>Item 2</div>
      </Layout.Grid>
    );

    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();
  });

  it('should apply CSS grid classes', () => {
    const { container } = render(
      <Layout.Grid>Content</Layout.Grid>
    );

    const gridElement = container.firstChild as HTMLElement;
    expect(gridElement).toHaveClass('grid');
  });

  it('should apply default grid columns (12 columns)', () => {
    const { container } = render(
      <Layout.Grid>Content</Layout.Grid>
    );

    const gridElement = container.firstChild as HTMLElement;
    expect(gridElement).toHaveClass('grid-cols-1');
    expect(gridElement).toHaveClass('md:grid-cols-12');
  });

  it('should apply custom grid columns', () => {
    const { container } = render(
      <Layout.Grid cols={4}>Content</Layout.Grid>
    );

    const gridElement = container.firstChild as HTMLElement;
    expect(gridElement).toHaveClass('grid-cols-1');
    expect(gridElement).toHaveClass('md:grid-cols-4');
  });

  it('should apply gap between grid items', () => {
    const { container } = render(
      <Layout.Grid>Content</Layout.Grid>
    );

    const gridElement = container.firstChild as HTMLElement;
    expect(gridElement).toHaveClass('gap-6');
  });

  it('should apply custom gap', () => {
    const { container } = render(
      <Layout.Grid gap={8}>Content</Layout.Grid>
    );

    const gridElement = container.firstChild as HTMLElement;
    expect(gridElement).toHaveClass('gap-8');
  });

  it('should accept custom className on Grid', () => {
    const { container } = render(
      <Layout.Grid className="custom-grid">Content</Layout.Grid>
    );

    const gridElement = container.firstChild as HTMLElement;
    expect(gridElement).toHaveClass('custom-grid');
    expect(gridElement).toHaveClass('grid');
  });
});

describe('Layout Component - Task 8.2: Responsive Utilities', () => {
  it('should support mobile-first responsive columns', () => {
    const { container } = render(
      <Layout.Grid cols={6}>Content</Layout.Grid>
    );

    const gridElement = container.firstChild as HTMLElement;
    // Mobile: 1 column
    expect(gridElement).toHaveClass('grid-cols-1');
    // Desktop: specified columns
    expect(gridElement).toHaveClass('md:grid-cols-6');
  });

  it('should combine Container and Grid', () => {
    render(
      <Layout.Container>
        <Layout.Grid>
          <div>Grid Item</div>
        </Layout.Grid>
      </Layout.Container>
    );

    expect(screen.getByText('Grid Item')).toBeInTheDocument();
  });

  it('should nest multiple Grid components', () => {
    render(
      <Layout.Grid>
        <Layout.Grid cols={2}>
          <div>Nested Item</div>
        </Layout.Grid>
      </Layout.Grid>
    );

    expect(screen.getByText('Nested Item')).toBeInTheDocument();
  });

  it('should apply responsive padding to Container', () => {
    const { container } = render(
      <Layout.Container>Content</Layout.Container>
    );

    const containerElement = container.firstChild as HTMLElement;
    // Base padding
    expect(containerElement).toHaveClass('px-4');
  });

  it('should support full-width layout within Container', () => {
    render(
      <Layout.Container>
        <div className="w-full">Full Width Content</div>
      </Layout.Container>
    );

    const content = screen.getByText('Full Width Content');
    expect(content).toHaveClass('w-full');
  });
});

describe('Layout Component - Integration', () => {
  it('should create typical page layout', () => {
    render(
      <Layout.Container>
        <Layout.Grid cols={3}>
          <div>Column 1</div>
          <div>Column 2</div>
          <div>Column 3</div>
        </Layout.Grid>
      </Layout.Container>
    );

    expect(screen.getByText('Column 1')).toBeInTheDocument();
    expect(screen.getByText('Column 2')).toBeInTheDocument();
    expect(screen.getByText('Column 3')).toBeInTheDocument();
  });

  it('should support complex nested layouts', () => {
    render(
      <Layout.Container>
        <Layout.Grid cols={2}>
          <div>
            <Layout.Grid cols={4}>
              <div>Nested Grid Item</div>
            </Layout.Grid>
          </div>
          <div>Main Content</div>
        </Layout.Grid>
      </Layout.Container>
    );

    expect(screen.getByText('Nested Grid Item')).toBeInTheDocument();
    expect(screen.getByText('Main Content')).toBeInTheDocument();
  });

  it('should maintain consistent spacing', () => {
    const { container } = render(
      <Layout.Container>
        <Layout.Grid>
          <div>Item 1</div>
          <div>Item 2</div>
        </Layout.Grid>
      </Layout.Container>
    );

    const containerElement = container.firstChild as HTMLElement;
    const gridElement = containerElement.firstChild as HTMLElement;

    expect(containerElement).toHaveClass('px-4');
    expect(gridElement).toHaveClass('gap-6');
  });
});
