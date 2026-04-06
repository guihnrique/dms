import type { Meta, StoryObj } from '@storybook/react';
import { Icon } from './Icon';

const meta = {
  title: 'Components/Icon',
  component: Icon,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    name: {
      control: 'text',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
    },
    decorative: {
      control: 'boolean',
    },
  },
} satisfies Meta<typeof Icon>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Home: Story = {
  args: {
    name: 'home',
    size: 'md',
  },
};

export const Small: Story = {
  args: {
    name: 'star',
    size: 'sm',
  },
};

export const Large: Story = {
  args: {
    name: 'favorite',
    size: 'lg',
  },
};

export const SemanticIcon: Story = {
  args: {
    name: 'warning',
    decorative: false,
    'aria-label': 'Warning message',
  },
};

export const IconGallery: Story = {
  args: { name: 'home' },
  render: () => (
    <div className="grid grid-cols-4 gap-8">
      <div className="flex flex-col items-center gap-2">
        <Icon name="home" size="lg" />
        <span className="text-xs">home</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="search" size="lg" />
        <span className="text-xs">search</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="favorite" size="lg" />
        <span className="text-xs">favorite</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="settings" size="lg" />
        <span className="text-xs">settings</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="person" size="lg" />
        <span className="text-xs">person</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="shopping_cart" size="lg" />
        <span className="text-xs">shopping_cart</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="notifications" size="lg" />
        <span className="text-xs">notifications</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="menu" size="lg" />
        <span className="text-xs">menu</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="close" size="lg" />
        <span className="text-xs">close</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="arrow_forward" size="lg" />
        <span className="text-xs">arrow_forward</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="arrow_back" size="lg" />
        <span className="text-xs">arrow_back</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <Icon name="star" size="lg" />
        <span className="text-xs">star</span>
      </div>
    </div>
  ),
};
