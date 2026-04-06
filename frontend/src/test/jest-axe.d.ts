declare module 'jest-axe' {
  import { Result } from 'axe-core';

  export interface JestAxeConfigureOptions {
    rules?: Record<string, { enabled: boolean }>;
    globalOptions?: Record<string, any>;
  }

  export function axe(
    html: Element | string,
    options?: any
  ): Promise<{ violations: Result[] }>;

  export function toHaveNoViolations(results: { violations: Result[] }): {
    pass: boolean;
    message(): string;
  };

  export function configureAxe(options?: JestAxeConfigureOptions): typeof axe;
}
