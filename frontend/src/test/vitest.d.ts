import type { TestingLibraryMatchers } from '@testing-library/jest-dom/matchers';

declare module 'vitest' {
  interface Assertion<T = any> extends TestingLibraryMatchers<typeof expect.stringContaining, T> {
    toHaveNoViolations(): void;
  }
  interface AsymmetricMatchersContaining extends TestingLibraryMatchers {
    toHaveNoViolations(): void;
  }
}
