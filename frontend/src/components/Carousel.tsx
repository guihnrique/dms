/**
 * Carousel Component - Task 9.3*
 * Requirements: 13 (Mobile Optimization)
 */
import React, { useState, useRef, Children } from 'react';
import { Icon } from './Icon';

export interface CarouselProps {
  /** Carousel items */
  children: React.ReactNode;

  /** Initial slide index */
  initialSlide?: number;

  /** Auto-play interval in ms (0 to disable) */
  autoPlay?: number;

  /** Show navigation arrows */
  showArrows?: boolean;

  /** Show slide indicators */
  showIndicators?: boolean;

  /** Custom className */
  className?: string;
}

export const Carousel: React.FC<CarouselProps> = ({
  children,
  initialSlide = 0,
  autoPlay = 0,
  showArrows = true,
  showIndicators = true,
  className = '',
}) => {
  const [currentSlide, setCurrentSlide] = useState(initialSlide);
  const [touchStart, setTouchStart] = useState(0);
  const [touchEnd, setTouchEnd] = useState(0);
  const trackRef = useRef<HTMLDivElement>(null);

  const slides = Children.toArray(children);
  const totalSlides = slides.length;

  // Minimum swipe distance to trigger slide change (50px)
  const MIN_SWIPE_DISTANCE = 50;

  const goToSlide = (index: number) => {
    if (index >= 0 && index < totalSlides) {
      setCurrentSlide(index);
    }
  };

  const goToPrevious = () => {
    goToSlide(currentSlide - 1);
  };

  const goToNext = () => {
    goToSlide(currentSlide + 1);
  };

  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(0); // Reset
    if (e.targetTouches && e.targetTouches[0]) {
      setTouchStart(e.targetTouches[0].clientX);
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (e.targetTouches && e.targetTouches[0]) {
      setTouchEnd(e.targetTouches[0].clientX);
    }
  };

  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return;

    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > MIN_SWIPE_DISTANCE;
    const isRightSwipe = distance < -MIN_SWIPE_DISTANCE;

    if (isLeftSwipe) {
      goToNext();
    } else if (isRightSwipe) {
      goToPrevious();
    }

    // Reset
    setTouchStart(0);
    setTouchEnd(0);
  };

  // Auto-play
  React.useEffect(() => {
    if (autoPlay > 0) {
      const interval = setInterval(() => {
        setCurrentSlide((prev) => (prev + 1) % totalSlides);
      }, autoPlay);

      return () => clearInterval(interval);
    }
  }, [autoPlay, totalSlides]);

  return (
    <div className={`relative overflow-hidden ${className}`.trim()}>
      {/* Carousel Track */}
      <div
        ref={trackRef}
        data-carousel="track"
        className="flex transition-transform duration-300 ease-out"
        style={{
          transform: `translateX(-${currentSlide * 100}%)`,
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {slides.map((slide, index) => (
          <div
            key={index}
            className="min-w-full flex-shrink-0"
            role="group"
            aria-roledescription="slide"
            aria-label={`Slide ${index + 1} of ${totalSlides}`}
          >
            {slide}
          </div>
        ))}
      </div>

      {/* Navigation Arrows */}
      {showArrows && (
        <>
          <button
            onClick={goToPrevious}
            disabled={currentSlide === 0}
            className="absolute left-4 top-1/2 -translate-y-1/2 glass-effect p-3 rounded-full disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/10 transition-colors"
            aria-label="Previous slide"
          >
            <Icon name="arrow_back" size="md" />
          </button>

          <button
            onClick={goToNext}
            disabled={currentSlide === totalSlides - 1}
            className="absolute right-4 top-1/2 -translate-y-1/2 glass-effect p-3 rounded-full disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/10 transition-colors"
            aria-label="Next slide"
          >
            <Icon name="arrow_forward" size="md" />
          </button>
        </>
      )}

      {/* Slide Indicators */}
      {showIndicators && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
          {slides.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              data-indicator
              className={`w-2 h-2 rounded-full transition-all ${
                index === currentSlide
                  ? 'bg-primary w-8'
                  : 'bg-white/30 hover:bg-white/50'
              }`}
              aria-label={`Go to slide ${index + 1}`}
              aria-current={index === currentSlide}
              role="button"
            />
          ))}
        </div>
      )}
    </div>
  );
};
