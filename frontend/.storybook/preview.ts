import type { Preview } from '@storybook/react-vite'
import '../src/index.css' // Import Tailwind and utilities

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
       color: /(background|color)$/i,
       date: /Date$/i,
      },
    },
    backgrounds: {
      default: 'neon-groove',
      values: [
        {
          name: 'neon-groove',
          value: '#1b0424', // Deep violet background
        },
        {
          name: 'light',
          value: '#ffffff',
        },
      ],
    },
    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: 'todo'
    }
  },
};

export default preview;