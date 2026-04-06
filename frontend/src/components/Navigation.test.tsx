/**
 * Navigation Component Tests - Task 7
 * Requirements: 3 (Glassmorphism), 8 (Navigation Component), 10 (Accessibility)
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Navigation } from './Navigation';

describe('Navigation Component - Task 7.1: Desktop Navigation', () => {
  it('should render navigation with glassmorphism effect', () => {
    const { container } = render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    const nav = container.querySelector('nav');
    expect(nav).toHaveClass('glass-effect');
  });

  it('should render as semantic nav element', () => {
    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  it('should render navigation items as links', () => {
    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
        <Navigation.Item href="/about">About</Navigation.Item>
      </Navigation>
    );

    expect(screen.getByRole('link', { name: 'Home' })).toHaveAttribute('href', '/');
    expect(screen.getByRole('link', { name: 'About' })).toHaveAttribute('href', '/about');
  });

  it('should apply hover effect to navigation items', () => {
    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    const link = screen.getByRole('link', { name: 'Home' });
    expect(link).toHaveClass('hover:bg-white/10');
  });

  it('should highlight active navigation item', () => {
    render(
      <Navigation>
        <Navigation.Item href="/" active>Home</Navigation.Item>
        <Navigation.Item href="/about">About</Navigation.Item>
      </Navigation>
    );

    const activeLink = screen.getByRole('link', { name: 'Home' });
    const inactiveLink = screen.getByRole('link', { name: 'About' });

    expect(activeLink).toHaveClass('bg-white/10');
    expect(inactiveLink).not.toHaveClass('bg-white/10');
  });

  it('should accept custom className on Navigation', () => {
    const { container } = render(
      <Navigation className="custom-nav">
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    const nav = container.querySelector('nav');
    expect(nav).toHaveClass('custom-nav');
  });

  it('should accept custom className on Navigation.Item', () => {
    render(
      <Navigation>
        <Navigation.Item href="/" className="custom-item">Home</Navigation.Item>
      </Navigation>
    );

    const link = screen.getByRole('link', { name: 'Home' });
    expect(link).toHaveClass('custom-item');
  });
});

describe('Navigation Component - Task 7.2: Mobile Menu', () => {
  it('should hide mobile menu by default', () => {
    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    const mobileMenu = screen.queryByTestId('mobile-menu');
    expect(mobileMenu).not.toBeInTheDocument();
  });

  it('should show menu button on mobile viewport', () => {
    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    const menuButton = screen.getByLabelText(/menu/i);
    expect(menuButton).toBeInTheDocument();
  });

  it('should toggle mobile menu when button clicked', async () => {
    const user = userEvent.setup();

    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
        <Navigation.Item href="/about">About</Navigation.Item>
      </Navigation>
    );

    const menuButton = screen.getByLabelText(/menu/i);
    await user.click(menuButton);

    // Menu should be visible
    expect(screen.getByTestId('mobile-menu')).toBeInTheDocument();

    await user.click(menuButton);

    // Menu should be hidden again
    expect(screen.queryByTestId('mobile-menu')).not.toBeInTheDocument();
  });

  it('should apply glassmorphism to mobile menu', async () => {
    const user = userEvent.setup();

    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    const menuButton = screen.getByLabelText(/menu/i);
    await user.click(menuButton);

    const mobileMenu = screen.getByTestId('mobile-menu');
    expect(mobileMenu).toHaveClass('glass-effect');
  });
});

describe('Navigation Component - Task 7.3: Accessibility', () => {
  it('should have accessible menu button with aria-label', () => {
    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    const menuButton = screen.getByLabelText(/menu/i);
    expect(menuButton).toHaveAttribute('aria-label');
  });

  it('should have aria-expanded on menu button', async () => {
    const user = userEvent.setup();

    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    const menuButton = screen.getByLabelText(/menu/i);

    expect(menuButton).toHaveAttribute('aria-expanded', 'false');

    await user.click(menuButton);

    expect(menuButton).toHaveAttribute('aria-expanded', 'true');
  });

  it('should support keyboard navigation', async () => {
    const user = userEvent.setup();

    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
        <Navigation.Item href="/about">About</Navigation.Item>
      </Navigation>
    );

    const firstLink = screen.getByRole('link', { name: 'Home' });
    const secondLink = screen.getByRole('link', { name: 'About' });

    // First tab focuses the first link (desktop nav)
    await user.tab();
    expect(firstLink).toHaveFocus();

    // Second tab focuses the second link
    await user.tab();
    expect(secondLink).toHaveFocus();

    // Third tab focuses the mobile menu button
    await user.tab();
    expect(screen.getByLabelText(/menu/i)).toHaveFocus();
  });

  it('should have focus visible styles', () => {
    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    const link = screen.getByRole('link', { name: 'Home' });
    expect(link).toHaveClass('focus:outline-primary');
  });

  it('should close mobile menu on item click', async () => {
    const user = userEvent.setup();

    render(
      <Navigation>
        <Navigation.Item href="/">Home</Navigation.Item>
      </Navigation>
    );

    const menuButton = screen.getByLabelText(/menu/i);
    await user.click(menuButton);

    expect(screen.getByTestId('mobile-menu')).toBeInTheDocument();

    const homeLink = screen.getAllByRole('link', { name: 'Home' })[1]; // Mobile menu link
    await user.click(homeLink);

    expect(screen.queryByTestId('mobile-menu')).not.toBeInTheDocument();
  });
});
