# Neon Groove Design System

A modern, immersive React component library featuring glassmorphism UI, neon gradients, and accessibility-first design.

## Features

- 🎨 **Glassmorphism UI** - Translucent components with backdrop blur effects
- 🌈 **Neon Gradients** - Vibrant purple-to-cyan gradient system (#a533ff → #00d2fd)
- ♿ **Accessibility First** - WCAG AA compliant with keyboard navigation and screen reader support
- 📱 **Mobile-First Responsive** - Optimized touch targets and responsive layouts
- ⚡ **Performance Optimized** - Lazy loading, code splitting, and optimized builds
- 🎭 **Material Symbols Icons** - 2500+ outlined icons with customizable weights
- 🔧 **TypeScript** - Full type safety and IntelliSense support

## Tech Stack

- **React 18.x** - Component library
- **TypeScript 5.x** - Type safety
- **Tailwind CSS 3.4** - Utility-first styling
- **Vite 8.x** - Fast build tool
- **Vitest + Testing Library** - Comprehensive testing

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Runs the development server at http://localhost:5173

### Build

```bash
npm run build
```

Builds production-optimized bundle in `dist/` directory.

### Testing

```bash
npm test           # Run all tests
npm test -- --watch # Watch mode
npm test -- Button  # Run specific test file
```

## Components

### Button

Primary, secondary, and ghost button variants with loading states.

```tsx
import { Button } from './components';

<Button variant="primary" size="md">
  Click me
</Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'ghost'
- `size`: 'sm' | 'md' | 'lg'
- `loading`: boolean
- All HTML button attributes

### Card

Glassmorphism card with compound components for Header, Content, and Footer.

```tsx
import { Card } from './components';

<Card glass interactive>
  <Card.Header>Title</Card.Header>
  <Card.Content>Body content</Card.Content>
  <Card.Footer>Actions</Card.Footer>
</Card>
```

**Props:**
- `glass`: boolean - Apply glassmorphism effect
- `interactive`: boolean - Enable hover scale
- `imageSrc`: string - Optional header image
- `imageAlt`: string - Image alt text

### Input

Form input with label, error states, and accessibility features.

```tsx
import { Input } from './components';

<Input
  label="Email"
  type="email"
  error="Invalid email"
  placeholder="Enter your email"
/>
```

**Props:**
- `label`: string - Input label
- `error`: string - Error message
- `type`: 'text' | 'email' | 'password' | 'search'
- All HTML input attributes

### Icon

Material Symbols Outlined icons with size variants and accessibility support.

```tsx
import { Icon } from './components';

<Icon name="home" size="md" decorative={false} aria-label="Home icon" />
```

**Props:**
- `name`: string - Material Symbols icon name
- `size`: 'sm' | 'md' | 'lg'
- `decorative`: boolean - Mark as decorative (default: true)
- `aria-label`: string - ARIA label for semantic icons

### Navigation

Responsive navigation bar with glassmorphism and mobile menu.

```tsx
import { Navigation } from './components';

<Navigation>
  <Navigation.Item href="/" active>Home</Navigation.Item>
  <Navigation.Item href="/about">About</Navigation.Item>
</Navigation>
```

**Props:**
- `NavigationItemProps`:
  - `href`: string - Link destination
  - `active`: boolean - Highlight as active
  - All HTML anchor attributes

### Layout

Container and Grid utilities for responsive layouts.

```tsx
import { Layout } from './components';

<Layout.Container>
  <Layout.Grid cols={3} gap={6}>
    <div>Column 1</div>
    <div>Column 2</div>
    <div>Column 3</div>
  </Layout.Grid>
</Layout.Container>
```

**Props:**
- `Container`: Standard centered container with responsive padding
- `Grid`:
  - `cols`: number - Desktop columns (default: 12)
  - `gap`: number - Gap size (default: 6)

## Design System

### Colors

**Base:**
- Background: `#1b0424` (Deep violet)
- Surface: `#2a0b35` to `#48266b` (Surface hierarchy)

**Primary:**
- Primary Dim: `#a533ff` (Neon purple)
- Primary: `#bf5cff` (Bright purple)
- Primary Bright: `#d998ff` (Light purple)

**Secondary:**
- Secondary: `#00d2fd` (Neon cyan)
- Secondary Container: `#004c62`

**Text:**
- On Surface: `#fbdbff` (High contrast - 10.5:1)
- On Surface Variant: `#c39fca` (Medium contrast - 5.8:1)

### Typography

**Fonts:**
- Headlines: Space Grotesk (500 weight)
- Body/UI: Manrope (400, 500, 600 weights)

**Sizes:**
- Display: 57px / 64px line height
- Headline: 32px / 40px
- Title: 22px / 28px
- Body: 16px / 24px
- Label: 14px / 20px

### Spacing

Scale: 0.25rem increments (4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px)

### Border Radius

Minimum: 0.75rem (12px) - No 90-degree corners throughout the system

## Accessibility

- ✅ WCAG AA compliant contrast ratios (4.5:1 minimum)
- ✅ Keyboard navigation support (Tab, Enter, Space, Escape)
- ✅ Screen reader compatibility with ARIA labels
- ✅ Reduced motion support via `prefers-reduced-motion`
- ✅ Minimum 44x44px touch targets on mobile
- ✅ Focus indicators on all interactive elements

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile Safari 14+
- Chrome Android 90+

Fallbacks provided for:
- `backdrop-filter` (solid background)
- CSS Grid (flexbox fallback where needed)

## Performance

**Bundle Size:**
- CSS: ~12.86 KB gzipped
- JS: ~60 KB gzipped (vendor chunk with React)

**Optimizations:**
- Image lazy loading with `loading="lazy"`
- Code splitting for vendor chunks
- Tree-shakeable component exports
- Tailwind JIT for minimal CSS

## License

MIT
