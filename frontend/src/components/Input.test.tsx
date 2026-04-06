/**
 * Input Component Tests - Task 5
 * Requirements: 6 (Input Component), 10 (Accessibility)
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from './Input';

describe('Input Component - Task 5.1: Basic Rendering', () => {
  it('should render input element', () => {
    render(<Input placeholder="Enter text" />);

    const input = screen.getByPlaceholderText('Enter text');
    expect(input).toBeInTheDocument();
  });

  it('should render with label when provided', () => {
    render(<Input label="Email Address" />);

    expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
  });

  it('should render without label by default', () => {
    const { container } = render(<Input placeholder="No label" />);

    const label = container.querySelector('label');
    expect(label).not.toBeInTheDocument();
  });

  it('should have text type by default', () => {
    render(<Input placeholder="Default type" />);

    const input = screen.getByPlaceholderText('Default type');
    expect(input).toHaveAttribute('type', 'text');
  });

  it('should support email type', () => {
    render(<Input type="email" placeholder="Email" />);

    const input = screen.getByPlaceholderText('Email');
    expect(input).toHaveAttribute('type', 'email');
  });

  it('should support password type', () => {
    render(<Input type="password" placeholder="Password" />);

    const input = screen.getByPlaceholderText('Password');
    expect(input).toHaveAttribute('type', 'password');
  });

  it('should support search type', () => {
    render(<Input type="search" placeholder="Search" />);

    const input = screen.getByPlaceholderText('Search');
    expect(input).toHaveAttribute('type', 'search');
  });
});

describe('Input Component - Task 5.2: Error State', () => {
  it('should not show error message by default', () => {
    const { container } = render(<Input placeholder="No error" />);

    const error = container.querySelector('[role="alert"]');
    expect(error).not.toBeInTheDocument();
  });

  it('should display error message when provided', () => {
    render(<Input error="This field is required" placeholder="With error" />);

    expect(screen.getByRole('alert')).toHaveTextContent('This field is required');
  });

  it('should apply error border class when error exists', () => {
    render(<Input error="Error message" placeholder="Error input" />);

    const input = screen.getByPlaceholderText('Error input');
    expect(input).toHaveClass('border-b-red-500');
  });

  it('should apply primary border class when no error', () => {
    render(<Input placeholder="Normal input" />);

    const input = screen.getByPlaceholderText('Normal input');
    expect(input).toHaveClass('focus:border-b-primary');
  });

  it('should set aria-invalid to true when error exists', () => {
    render(<Input error="Invalid input" placeholder="Invalid" />);

    const input = screen.getByPlaceholderText('Invalid');
    expect(input).toHaveAttribute('aria-invalid', 'true');
  });

  it('should set aria-invalid to false when no error', () => {
    render(<Input placeholder="Valid" />);

    const input = screen.getByPlaceholderText('Valid');
    expect(input).toHaveAttribute('aria-invalid', 'false');
  });

  it('should link error message with aria-describedby', () => {
    render(<Input error="Error text" placeholder="Linked error" id="test-input" />);

    const input = screen.getByPlaceholderText('Linked error');
    const errorId = input.getAttribute('aria-describedby');

    expect(errorId).toBeTruthy();
    expect(screen.getByRole('alert')).toHaveAttribute('id', errorId!);
  });
});

describe('Input Component - Task 5.3: Accessibility & Interaction', () => {
  it('should generate unique ID when not provided', () => {
    const { container } = render(<Input label="Auto ID" />);

    const input = container.querySelector('input');
    const id = input?.getAttribute('id');

    expect(id).toBeTruthy();
    expect(id).toMatch(/^input-/);
  });

  it('should use provided ID', () => {
    render(<Input label="Custom ID" id="custom-input" />);

    const input = screen.getByLabelText('Custom ID');
    expect(input).toHaveAttribute('id', 'custom-input');
  });

  it('should associate label with input using htmlFor', () => {
    const { container } = render(<Input label="Associated Label" id="associated-input" />);

    const label = container.querySelector('label');
    expect(label).toHaveAttribute('for', 'associated-input');
  });

  it('should accept custom aria-label', () => {
    render(<Input aria-label="Custom ARIA label" placeholder="ARIA input" />);

    const input = screen.getByLabelText('Custom ARIA label');
    expect(input).toBeInTheDocument();
  });

  it('should accept custom className', () => {
    render(<Input className="custom-input" placeholder="Custom class" />);

    const input = screen.getByPlaceholderText('Custom class');
    expect(input).toHaveClass('custom-input');
  });

  it('should forward ref to input element', () => {
    const ref = { current: null as HTMLInputElement | null };
    render(<Input ref={ref} placeholder="Ref input" />);

    expect(ref.current).toBeInstanceOf(HTMLInputElement);
    expect(ref.current).toHaveAttribute('placeholder', 'Ref input');
  });

  it('should handle onChange event', async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();

    render(<Input onChange={handleChange} placeholder="Change test" />);

    const input = screen.getByPlaceholderText('Change test');
    await user.type(input, 'Hello');

    expect(handleChange).toHaveBeenCalled();
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Input disabled placeholder="Disabled input" />);

    const input = screen.getByPlaceholderText('Disabled input');
    expect(input).toBeDisabled();
    expect(input).toHaveClass('disabled:opacity-50');
  });

  it('should support placeholder text', () => {
    render(<Input placeholder="Enter your name" />);

    expect(screen.getByPlaceholderText('Enter your name')).toBeInTheDocument();
  });

  it('should have transparent background', () => {
    render(<Input placeholder="Transparent" />);

    const input = screen.getByPlaceholderText('Transparent');
    expect(input).toHaveClass('bg-transparent');
  });

  it('should have full width', () => {
    render(<Input placeholder="Full width" />);

    const input = screen.getByPlaceholderText('Full width');
    expect(input).toHaveClass('w-full');
  });
});
