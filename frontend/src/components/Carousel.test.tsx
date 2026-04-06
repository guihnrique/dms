/**
 * Carousel Component Tests - Task 9.3*
 * Requirements: 13 (Mobile Optimization)
 */
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Carousel } from './Carousel';

describe('Carousel Component - Task 9.3*', () => {
  const items = [
    { id: '1', content: 'Slide 1' },
    { id: '2', content: 'Slide 2' },
    { id: '3', content: 'Slide 3' },
  ];

  describe('Basic Rendering', () => {
    it('should render carousel with items', () => {
      render(
        <Carousel>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      expect(screen.getByText('Slide 1')).toBeInTheDocument();
    });

    it('should show navigation arrows', () => {
      render(
        <Carousel>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      expect(screen.getByLabelText('Previous slide')).toBeInTheDocument();
      expect(screen.getByLabelText('Next slide')).toBeInTheDocument();
    });

    it('should show slide indicators', () => {
      const { container } = render(
        <Carousel>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const indicators = container.querySelectorAll('[role="button"]');
      expect(indicators.length).toBeGreaterThanOrEqual(3);
    });
  });

  describe('Navigation', () => {
    it('should navigate to next slide on arrow click', async () => {
      const { container } = render(
        <Carousel>
          {items.map(item => (
            <div key={item.id} data-testid={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const nextButton = screen.getByLabelText('Next slide');
      fireEvent.click(nextButton);

      // Check if carousel moved to next slide
      const carousel = container.querySelector('[data-carousel="track"]');
      expect(carousel).toHaveStyle({ transform: 'translateX(-100%)' });
    });

    it('should navigate to previous slide on arrow click', () => {
      const { container } = render(
        <Carousel initialSlide={1}>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const prevButton = screen.getByLabelText('Previous slide');
      fireEvent.click(prevButton);

      const carousel = container.querySelector('[data-carousel="track"]');
      expect(carousel).toHaveStyle({ transform: 'translateX(-0%)' });
    });

    it('should navigate to specific slide via indicators', () => {
      const { container } = render(
        <Carousel>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const indicators = container.querySelectorAll('[data-indicator]');
      fireEvent.click(indicators[2] as Element);

      const carousel = container.querySelector('[data-carousel="track"]');
      expect(carousel).toHaveStyle({ transform: 'translateX(-200%)' });
    });
  });

  describe('Swipe Gestures', () => {
    it('should support touch start event', () => {
      const { container } = render(
        <Carousel>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const track = container.querySelector('[data-carousel="track"]');

      fireEvent.touchStart(track!, {
        targetTouches: [{ clientX: 100, clientY: 0 }],
      });

      // Should not throw
      expect(track).toBeInTheDocument();
    });

    it('should swipe to next slide on left swipe', () => {
      const { container } = render(
        <Carousel>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const track = container.querySelector('[data-carousel="track"]');

      // Simulate swipe left (next)
      fireEvent.touchStart(track!, {
        targetTouches: [{ clientX: 100, clientY: 0 }],
      });

      fireEvent.touchMove(track!, {
        targetTouches: [{ clientX: 20, clientY: 0 }],
      });

      fireEvent.touchEnd(track!);

      // Should have moved to next slide
      expect(track).toHaveStyle({ transform: 'translateX(-100%)' });
    });

    it('should swipe to previous slide on right swipe', () => {
      const { container } = render(
        <Carousel initialSlide={1}>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const track = container.querySelector('[data-carousel="track"]');

      // Simulate swipe right (previous)
      fireEvent.touchStart(track!, {
        targetTouches: [{ clientX: 20, clientY: 0 }],
      });

      fireEvent.touchMove(track!, {
        targetTouches: [{ clientX: 100, clientY: 0 }],
      });

      fireEvent.touchEnd(track!);

      // Should have moved to previous slide
      expect(track).toHaveStyle({ transform: 'translateX(-0%)' });
    });

    it('should require minimum swipe distance to trigger', () => {
      const { container } = render(
        <Carousel>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const track = container.querySelector('[data-carousel="track"]');

      // Simulate small swipe (should not trigger - less than 50px)
      fireEvent.touchStart(track!, {
        targetTouches: [{ clientX: 100, clientY: 0 }],
      });

      fireEvent.touchMove(track!, {
        targetTouches: [{ clientX: 95, clientY: 0 }],
      });

      fireEvent.touchEnd(track!);

      // Should stay on first slide
      expect(track).toHaveStyle({ transform: 'translateX(-0%)' });
    });
  });

  describe('Accessibility', () => {
    it('should have accessible navigation buttons', () => {
      render(
        <Carousel>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const prevButton = screen.getByLabelText('Previous slide');
      const nextButton = screen.getByLabelText('Next slide');

      expect(prevButton).toHaveAttribute('aria-label');
      expect(nextButton).toHaveAttribute('aria-label');
    });

    it('should disable prev button on first slide', () => {
      render(
        <Carousel>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const prevButton = screen.getByLabelText('Previous slide');
      expect(prevButton).toBeDisabled();
    });

    it('should disable next button on last slide', () => {
      render(
        <Carousel initialSlide={2}>
          {items.map(item => (
            <div key={item.id}>{item.content}</div>
          ))}
        </Carousel>
      );

      const nextButton = screen.getByLabelText('Next slide');
      expect(nextButton).toBeDisabled();
    });
  });
});
