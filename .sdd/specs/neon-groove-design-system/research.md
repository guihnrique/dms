# Research & Design Decisions

## Summary
- **Feature**: `neon-groove-design-system`
- **Discovery Scope**: New Feature (Greenfield React Component Library)
- **Key Findings**:
  - React component composition pattern with TypeScript provides type-safe props and reduces prop drilling
  - Tailwind CSS JIT mode with custom theme configuration supports design tokens efficiently
  - Glassmorphism with backdrop-filter requires fallback for older browsers (progressive enhancement)
  - Vite build tool provides Fast Refresh for component development and optimized production bundles
  - WCAG AA requires 4.5:1 contrast ratio for normal text, 3:1 for large text on dark backgrounds
  - Material Symbols icons loaded via CSS subset reduces bundle size compared to full icon font

## Research Log

### React Component Library Architecture
- **Context**: Need reusable, type-safe component library aligned with "Neon Groove" design system
- **Sources Consulted**:
  - React documentation (hooks, functional components, composition patterns)
  - TypeScript handbook (interface definitions, generics, type narrowing)
  - Component library patterns (Radix UI, Headless UI, shadcn/ui)
- **Findings**:
  - **Composition over inheritance**: React favors composable components (e.g., `<Card><Card.Header><Card.Content>`)
  - **TypeScript interfaces**: Define clear props contracts (`interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>`)
  - **Controlled vs uncontrolled components**: Forms should support both patterns for flexibility
  - **Children prop**: `React.ReactNode` type accepts JSX, strings, fragments for maximum composability
  - **Ref forwarding**: Use `React.forwardRef` for components that need DOM access (inputs, buttons)
  - **Compound components**: Share state between parent and children via Context API (e.g., `<Tabs>` with `<Tab>` children)
- **Implications**:
  - All components use functional components with TypeScript interfaces
  - Button, Card, Input components export typed props interfaces
  - Compound components (Card with Card.Header/Card.Content) for layout flexibility
  - Ref forwarding for all interactive components (buttons, inputs)

### Tailwind CSS Design Tokens Configuration
- **Context**: Requirements specify custom color system, typography, spacing aligned with "Neon Groove" design
- **Sources Consulted**:
  - Tailwind CSS documentation (theme extension, custom utilities)
  - Design token patterns (Style Dictionary, Tailwind Preset)
  - JIT mode performance benchmarks
- **Findings**:
  - **Theme extension**: `tailwind.config.js` extends default theme with custom colors, fonts, spacing
  - **Design tokens as CSS variables**: Alternative approach uses CSS custom properties for runtime theming
  - **JIT mode**: Just-In-Time compilation generates only used utilities (faster builds, smaller bundles)
  - **Custom utilities**: `@layer utilities` for reusable patterns (e.g., `.glass-effect`, `.gradient-primary`)
  - **Safelist**: Specify dynamic classes to ensure JIT includes them in production build
  - **Content paths**: Configure `content: ['./src/**/*.{js,ts,jsx,tsx}']` to scan all components
- **Implications**:
  - Use `tailwind.config.js` with extended theme for all design tokens (colors, fonts, spacing)
  - Define custom utilities for glassmorphism and gradient patterns in `@layer utilities`
  - Enable JIT mode for optimal build performance
  - Safelist dynamic classes generated in components (e.g., `bg-${color}-500`)

### Glassmorphism Browser Support and Fallbacks
- **Context**: Requirement 3 specifies backdrop-blur effects for glassmorphism on navigation, modals, cards
- **Sources Consulted**:
  - MDN Web Docs (backdrop-filter property, browser support)
  - Can I Use (backdrop-filter compatibility data)
  - Progressive enhancement strategies
- **Findings**:
  - **Browser support**: Chrome/Edge 76+, Safari 9+, Firefox 103+ (widely supported in 2026)
  - **Fallback strategy**: Use `@supports (backdrop-filter: blur())` to detect support
  - **Progressive enhancement**: Provide solid background fallback when backdrop-filter unsupported
  - **Performance**: backdrop-filter GPU-accelerated but can cause repaint performance issues on complex layouts
  - **Accessibility**: Glass effects must maintain WCAG AA contrast ratios (4.5:1 for text)
- **Implications**:
  - Apply glassmorphism with `backdrop-blur-xl bg-white/5` classes
  - Fallback CSS: `@supports not (backdrop-filter: blur()) { .glass-effect { background: rgba(42, 11, 53, 0.95); } }`
  - Test contrast ratios for all glass surfaces with text content
  - Monitor performance on mobile devices (limit backdrop-blur layers)

### Vite for Component Library Development
- **Context**: Requirements specify Vite for Fast Refresh and optimized production bundles
- **Sources Consulted**:
  - Vite documentation (library mode, build optimization)
  - React Fast Refresh integration
  - Bundle size optimization techniques
- **Findings**:
  - **Fast Refresh**: Vite provides instant HMR (Hot Module Replacement) for React components
  - **Library mode**: `vite build --mode lib` generates ESM and UMD bundles for distribution
  - **Tree shaking**: Vite uses Rollup for production builds with automatic dead code elimination
  - **Code splitting**: Dynamic imports (`React.lazy`) enable route-based and component-based splitting
  - **Asset optimization**: Vite automatically optimizes images, fonts, CSS during build
  - **Development server**: Serves unbundled ESM modules for instant startup (<300ms)
- **Implications**:
  - Use Vite as build tool with React plugin for Fast Refresh
  - Configure library mode for component library distribution (future)
  - Implement code splitting for heavy components (future enhancement)
  - Development environment provides instant feedback for component changes

### WCAG AA Contrast Requirements for Dark Themes
- **Context**: Requirement 10 specifies WCAG AA compliance with high contrast ratios on dark backgrounds
- **Sources Consulted**:
  - WCAG 2.1 guidelines (contrast requirements, Level AA)
  - WebAIM contrast checker
  - Dark mode accessibility patterns
- **Findings**:
  - **Normal text (< 18pt)**: Minimum 4.5:1 contrast ratio
  - **Large text (≥ 18pt or 14pt bold)**: Minimum 3:1 contrast ratio
  - **UI components**: 3:1 contrast for interactive elements (buttons, form inputs)
  - **Deep violet base (#1b0424)**: White text (#fbdbff) achieves 10.5:1 contrast (exceeds AA)
  - **Surface hierarchy**: Lighter surfaces reduce contrast (test each level)
  - **Neon gradients**: Gradient text may fail contrast on certain stops (test both ends)
- **Implications**:
  - Verify all text colors against background surfaces with contrast checker
  - Use on_surface (#fbdbff) for primary text on dark backgrounds
  - Use on_surface_variant (#c39fca) for secondary text (test contrast)
  - Gradient text must maintain 4.5:1 contrast on lightest gradient stop
  - Document contrast ratios in component documentation

### Material Symbols Icons Integration
- **Context**: Requirement 7 specifies Material Symbols Outlined with thin stroke weight (1.5px)
- **Sources Consulted**:
  - Material Symbols documentation (icon variants, loading strategies)
  - Icon font performance optimization
  - SVG vs icon font trade-offs
- **Findings**:
  - **Icon variants**: Outlined, Filled, Rounded, Sharp (use Outlined)
  - **Weight**: 100-700 range (use 200 for thin stroke ~1.5px visual weight)
  - **Loading strategies**:
    1. Full icon font (400KB+ for all icons) - slow initial load
    2. CSS subset (10-20KB for selected icons) - faster, recommended
    3. SVG sprites (smallest, requires build step) - best for production
  - **Font variation settings**: `font-variation-settings: 'FILL' 0, 'wght' 200` for outlined thin
  - **Accessibility**: Icons must have aria-label or be decorative (aria-hidden)
- **Implications**:
  - Load Material Symbols via CSS subset for MVP (specify icons in build)
  - Configure font-variation-settings: 'wght' 200 for thin stroke weight
  - Wrap icons in React components with optional aria-label prop
  - Future optimization: Migrate to SVG sprite system for production

### Mobile-First Responsive Design Strategy
- **Context**: Requirement 8 and 13 specify mobile-first approach with touch-friendly interactions
- **Sources Consulted**:
  - Responsive design patterns (mobile-first vs desktop-first)
  - Touch target size guidelines (Apple HIG, Material Design)
  - Viewport breakpoint strategies
- **Findings**:
  - **Mobile-first**: Default styles for 320px viewport, enhance with media queries
  - **Touch targets**: Minimum 44x44px for interactive elements on mobile (WCAG 2.5.5)
  - **Tailwind breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
  - **Viewport meta tag**: `width=device-width, initial-scale=1.0` required for responsive behavior
  - **Hover states**: Use `@media (hover: hover)` to prevent sticky hover on touch devices
  - **Stack vs grid**: Vertical stacking default on mobile, grid/flexbox layouts on tablet+
- **Implications**:
  - Write base styles for mobile viewport (320px min-width)
  - Buttons minimum 44x44px on mobile (`min-h-11 min-w-11`)
  - Apply `md:` prefix for tablet/desktop enhancements (grid layouts, multi-column)
  - Disable hover effects on touch devices with `@media (hover: hover)`

### Component State Management Patterns
- **Context**: Need consistent state management for interactive components (Button, Input, Card)
- **Sources Consulted**:
  - React state management (useState, useReducer, Context API)
  - Controlled vs uncontrolled component patterns
  - Form state libraries (React Hook Form, Formik)
- **Findings**:
  - **Local state**: Use `useState` for isolated component state (button loading, input value)
  - **Controlled components**: Parent manages state, component receives value + onChange props
  - **Uncontrolled components**: Component manages internal state, exposes value via ref
  - **Form state**: React Hook Form recommended for complex forms (validation, submission)
  - **Global state**: Not needed for design system components (each component stateless or local state)
- **Implications**:
  - All form components (Input, Button) support both controlled and uncontrolled patterns
  - No global state dependencies (components usable in any state management context)
  - Expose callback props (onClick, onChange) for parent state management
  - Future: Provide React Hook Form integration utilities

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| **Component Composition (Selected)** | React functional components with TypeScript, composable via children prop | Type-safe, reusable, follows React best practices | Requires TypeScript knowledge | Aligns with React community standard |
| Atomic Design | Components organized as Atoms, Molecules, Organisms, Templates, Pages | Clear hierarchy, design system alignment | Rigid structure, naming overhead | Too formal for small component library |
| Utility-First | Pure Tailwind classes without abstraction, no custom components | Fast development, no JS overhead | Inconsistent patterns, poor DX | Not suitable for design system distribution |

**Selected**: Component Composition Pattern
- TypeScript interfaces provide type safety and IDE autocomplete
- Composition via children prop enables flexible layouts
- Matches React community best practices
- Enables component distribution as npm package (future)

## Design Decisions

### Decision: Tailwind CSS Theme Extension (Not CSS Variables)
- **Context**: Need design token system for colors, typography, spacing aligned with "Neon Groove" design
- **Alternatives Considered**:
  1. **Tailwind theme extension** - Extend default theme in tailwind.config.js
  2. **CSS variables** - Define design tokens as CSS custom properties
  3. **Style Dictionary** - Separate design token JSON compiled to multiple formats
- **Selected Approach**: Tailwind theme extension in tailwind.config.js
  ```javascript
  module.exports = {
    theme: {
      extend: {
        colors: {
          'primary-dim': '#a533ff',
          'secondary': '#00d2fd',
          'background': '#1b0424',
          // ... all design tokens
        },
        fontFamily: {
          headline: ['Space Grotesk'],
          body: ['Manrope'],
        },
        spacing: {
          '12': '3rem',  // 48px
          '16': '4rem',  // 64px
        }
      }
    }
  }
  ```
- **Rationale**:
  - Tailwind utilities automatically generated for all extended theme values
  - Type-safe autocomplete in IDE (via Tailwind IntelliSense)
  - Simpler than CSS variables for static design tokens
  - Consistent with Tailwind best practices
- **Trade-offs**:
  - **Benefit**: Automatic utility class generation, type safety
  - **Compromise**: Cannot change theme at runtime (no dark mode toggle)
- **Follow-up**: Future enhancement for runtime theming via CSS variables

### Decision: Glassmorphism Utility Classes (Not Inline Styles)
- **Context**: Requirement 3 specifies standardized glassmorphism effects for navigation, modals, cards
- **Alternatives Considered**:
  1. **Utility classes** - Define `.glass-effect` in Tailwind utilities layer
  2. **Component props** - Pass glass effect as prop to each component
  3. **Inline styles** - Apply backdrop-blur inline via style prop
- **Selected Approach**: Custom utility class in Tailwind configuration
  ```css
  @layer utilities {
    .glass-effect {
      @apply backdrop-blur-xl bg-white/5;
      border: 1px solid rgba(138, 106, 146, 0.2);
    }
    .glass-fallback {
      @supports not (backdrop-filter: blur()) {
        background: rgba(42, 11, 53, 0.95);
      }
    }
  }
  ```
- **Rationale**:
  - Consistent glass effect across all components
  - Single source of truth for backdrop-blur and opacity values
  - Easy to update design (change one place affects all components)
  - Includes fallback for unsupported browsers
- **Trade-offs**:
  - **Benefit**: Consistency, maintainability, fallback support
  - **Compromise**: Requires custom Tailwind configuration setup
- **Follow-up**: Document glass-effect usage in component documentation

### Decision: Component Composition with TypeScript Interfaces
- **Context**: Requirements specify reusable components (Button, Card, Input) with clear APIs
- **Alternatives Considered**:
  1. **TypeScript interfaces** - Explicit props types with extends pattern
  2. **PropTypes** - Runtime validation (legacy React pattern)
  3. **No types** - Plain JavaScript components
- **Selected Approach**: TypeScript interfaces extending HTML element types
  ```typescript
  interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
    children: React.ReactNode;
  }
  
  export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ variant = 'primary', size = 'md', loading, children, ...props }, ref) => {
      // Implementation
    }
  );
  ```
- **Rationale**:
  - TypeScript provides compile-time type checking (catch errors early)
  - Extending HTML element types inherits all native props (onClick, disabled, etc.)
  - Ref forwarding enables parent components to access DOM elements
  - Clear API surface for component consumers
- **Trade-offs**:
  - **Benefit**: Type safety, IDE autocomplete, better DX
  - **Compromise**: Requires TypeScript setup (additional build step)
- **Follow-up**: Generate type definitions for npm package distribution

### Decision: Mobile-First Responsive Design with Tailwind Breakpoints
- **Context**: Requirement 8 and 13 specify mobile-first approach optimized for small screens
- **Alternatives Considered**:
  1. **Mobile-first** - Base styles for mobile, enhance with `md:` prefixes
  2. **Desktop-first** - Base styles for desktop, reduce with `max-md:` prefixes
  3. **Hybrid** - Mix of mobile and desktop base styles
- **Selected Approach**: Mobile-first with Tailwind responsive prefixes
  ```jsx
  // Base styles for mobile (320px+)
  <button className="w-full px-4 py-3 text-base
                     md:w-auto md:px-6 md:py-4 md:text-lg">
    Click Me
  </button>
  ```
- **Rationale**:
  - Mobile traffic often exceeds desktop (optimize for majority)
  - Smaller CSS bundle (mobile styles without media queries)
  - Progressive enhancement (add features for larger screens)
  - Aligns with steering mobile-first principle
- **Trade-offs**:
  - **Benefit**: Optimized mobile experience, smaller base CSS
  - **Compromise**: Desktop styles require more class names
- **Follow-up**: Test on real mobile devices for touch interaction

### Decision: Material Symbols via CSS Subset (Not Full Icon Font)
- **Context**: Requirement 7 specifies Material Symbols icons with thin stroke weight
- **Alternatives Considered**:
  1. **Full icon font** - Load all Material Symbols icons (400KB+)
  2. **CSS subset** - Load only used icons (10-20KB)
  3. **SVG sprites** - Inline SVG icons in sprite sheet (smallest)
- **Selected Approach**: CSS subset for MVP, SVG migration path documented
  ```html
  <!-- Load only used icons via Google Fonts API -->
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@200&text=home+search+play+pause" rel="stylesheet"/>
  ```
  ```jsx
  // React icon component
  export const Icon = ({ name, 'aria-label': ariaLabel }) => (
    <span className="material-symbols-outlined" aria-label={ariaLabel} style={{ fontVariationSettings: "'wght' 200" }}>
      {name}
    </span>
  );
  ```
- **Rationale**:
  - CSS subset loads only icons used in application (10-20KB vs 400KB)
  - Google Fonts CDN provides caching across sites
  - Simpler than SVG sprite setup for MVP
  - Font variation settings enable thin stroke weight
- **Trade-offs**:
  - **Benefit**: Fast loading, simple implementation
  - **Compromise**: Google Fonts dependency (external request)
- **Follow-up**: Migrate to self-hosted SVG sprites for production

### Decision: ARIA Labels and Semantic HTML for Accessibility
- **Context**: Requirement 10 specifies WCAG AA compliance with keyboard navigation and screen reader support
- **Alternatives Considered**:
  1. **Semantic HTML + ARIA** - Use semantic elements (button, nav) with ARIA labels
  2. **Divs + ARIA roles** - Use divs with role attributes
  3. **JavaScript keyboard handling** - Manual focus management
- **Selected Approach**: Semantic HTML with optional ARIA labels
  ```jsx
  <button type="button" aria-label="Play track" onClick={handlePlay}>
    <Icon name="play" />
  </button>
  
  <nav aria-label="Main navigation">
    <ul>
      <li><a href="/explore">Explore</a></li>
    </ul>
  </nav>
  ```
- **Rationale**:
  - Semantic HTML provides built-in accessibility (keyboard navigation, focus management)
  - ARIA labels clarify purpose for screen readers
  - Native elements support keyboard shortcuts automatically
  - Follows WCAG best practices
- **Trade-offs**:
  - **Benefit**: Strong accessibility, minimal code
  - **Compromise**: Requires careful testing with screen readers
- **Follow-up**: Test all components with NVDA, JAWS, VoiceOver

## Risks & Mitigations

### Risk 1: Glassmorphism Performance on Low-End Mobile Devices
- **Description**: backdrop-filter is GPU-intensive and may cause frame drops on low-end Android devices
- **Impact**: Janky scrolling, poor user experience on mobile
- **Mitigation**:
  - Test performance on real devices (iPhone SE, low-end Android)
  - Limit glass effect layers (max 2-3 overlapping backdrop-blur elements)
  - Provide fallback solid background on performance detection
  - Use `will-change: backdrop-filter` sparingly (GPU compositing hint)
  - Monitor Core Web Vitals (CLS, FID, LCP)

### Risk 2: WCAG Contrast Failures on Surface Hierarchy Levels
- **Description**: Lighter surface levels (surface_bright, surface_container_high) may reduce text contrast below 4.5:1
- **Impact**: WCAG AA compliance failure, poor readability
- **Mitigation**:
  - Test all text colors against all surface levels with contrast checker
  - Adjust on_surface_variant (#c39fca) if contrast fails
  - Document approved color combinations in component documentation
  - Automated contrast testing in CI/CD pipeline (axe-core, lighthouse)

### Risk 3: TypeScript Type Complexity for Component Consumers
- **Description**: Complex TypeScript interfaces may confuse developers unfamiliar with TypeScript
- **Impact**: Poor developer experience, reduced adoption
- **Mitigation**:
  - Provide comprehensive TypeScript examples in documentation
  - Export all interfaces for consumer reuse
  - Use simple types for common props (variant: 'primary' | 'secondary')
  - Avoid advanced TypeScript features (conditional types, mapped types)
  - Provide JavaScript usage examples alongside TypeScript

### Risk 4: Tailwind JIT Mode Missing Dynamic Classes
- **Description**: JIT mode only generates classes found in source files; dynamic classes (e.g., `bg-${color}-500`) excluded
- **Impact**: Missing styles in production build
- **Mitigation**:
  - Use safelist in tailwind.config.js for dynamic classes
  - Prefer static class names where possible
  - Test production build thoroughly before deployment
  - Document safelist usage in component development guide

### Risk 5: Icon Font Load Delay (FOIT/FOUT)
- **Description**: Icon font load delay causes flash of invisible text (FOIT) or unstyled text (FOUT)
- **Impact**: Icons missing briefly on page load
- **Mitigation**:
  - Use `font-display: swap` in Google Fonts URL
  - Provide fallback text or emoji for critical icons (e.g., ▶ for play button)
  - Preload icon font in HTML `<head>` for critical icons
  - Future: Migrate to inline SVG for instant rendering

## References

### Official Documentation
- [React Documentation](https://react.dev/) - Hooks, composition patterns
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) - Interfaces, generics
- [Tailwind CSS](https://tailwindcss.com/docs) - Custom configuration, JIT mode
- [Vite](https://vitejs.dev/) - Build tool, library mode
- [Material Symbols](https://fonts.google.com/icons) - Icon variants, loading strategies

### Accessibility Resources
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - Contrast requirements, keyboard navigation
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) - Test color combinations
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility) - ARIA, semantic HTML

### Design Patterns
- Component Composition - React best practices
- Mobile-First Design - Progressive enhancement

### Internal References
- `.sdd/steering/structure.md` - React component organization, import patterns
- `.sdd/steering/tech.md` - Tailwind configuration, React development standards
- `src/stitch/stitch/neon_groove/DESIGN.md` - Complete "Neon Groove" design system specification
