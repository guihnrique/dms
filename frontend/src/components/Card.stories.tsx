import type { Meta, StoryObj } from '@storybook/react';
import { Card } from './Card';
import { Button } from './Button';
import { Icon } from './Icon';

const meta = {
  title: 'Components/Card',
  component: Card,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Basic: Story = {
  args: {},
  render: () => (
    <Card>
      <Card.Content>
        <p>Basic card with glassmorphism effect</p>
      </Card.Content>
    </Card>
  ),
};

export const WithHeader: Story = {
  args: {},
  render: () => (
    <Card glass>
      <Card.Header>
        <h3 className="font-headline text-2xl">Card Title</h3>
      </Card.Header>
      <Card.Content>
        <p className="text-on-surface-variant">Card content goes here</p>
      </Card.Content>
    </Card>
  ),
};

export const WithFooter: Story = {
  args: {},
  render: () => (
    <Card>
      <Card.Header>
        <h3 className="font-headline text-2xl">Complete Card</h3>
      </Card.Header>
      <Card.Content>
        <p className="text-on-surface-variant mb-4">
          This card has all sections: header, content, and footer
        </p>
      </Card.Content>
      <Card.Footer>
        <div className="flex gap-4">
          <Button variant="primary" size="sm">Action</Button>
          <Button variant="ghost" size="sm">Cancel</Button>
        </div>
      </Card.Footer>
    </Card>
  ),
};

export const WithImage: Story = {
  args: {},
  render: () => (
    <Card imageSrc="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&h=400&fit=crop" imageAlt="Neon lights">
      <Card.Header>
        <h3 className="font-headline text-2xl">Featured Content</h3>
      </Card.Header>
      <Card.Content>
        <p className="text-on-surface-variant">Card with lazy-loaded image</p>
      </Card.Content>
    </Card>
  ),
};

export const Interactive: Story = {
  args: {},
  render: () => (
    <Card interactive>
      <Card.Content>
        <div className="flex items-center gap-3 mb-4">
          <Icon name="star" size="lg" decorative={false} aria-label="Featured" />
          <h3 className="font-headline text-xl">Interactive Card</h3>
        </div>
        <p className="text-on-surface-variant">
          Hover to see the scale effect
        </p>
      </Card.Content>
    </Card>
  ),
};

export const SolidBackground: Story = {
  args: {},
  render: () => (
    <Card glass={false}>
      <Card.Content>
        <p>Card with solid background instead of glassmorphism</p>
      </Card.Content>
    </Card>
  ),
};
