/**
 * Login/Register Page
 */

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, Button, Input } from '../components';
import { useAuth } from '../context/AuthContext';

export function LoginPage() {
  const navigate = useNavigate();
  const { login, register, error, clearError, loading } = useAuth();

  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    clearError();

    try {
      if (mode === 'login') {
        await login({ email, password });
      } else {
        await register({ email, password });
      }
      navigate('/');
    } catch (err) {
      // Error is handled by AuthContext
    }
  }

  function toggleMode() {
    setMode(mode === 'login' ? 'register' : 'login');
    clearError();
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="font-headline text-4xl font-medium mb-2 text-gradient">
            {mode === 'login' ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-on-surface-variant">
            {mode === 'login'
              ? 'Sign in to access your playlists and recommendations'
              : 'Join The Sonic Immersive to discover new music'}
          </p>
        </div>

        <Card glass>
          <Card.Content>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <Input
                label="Password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              {error && (
                <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                loading={loading}
              >
                {mode === 'login' ? 'Sign In' : 'Create Account'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <button
                type="button"
                onClick={toggleMode}
                className="text-sm text-on-surface-variant hover:text-on-surface transition-colors"
              >
                {mode === 'login' ? (
                  <>
                    Don't have an account?{' '}
                    <span className="text-primary">Create one</span>
                  </>
                ) : (
                  <>
                    Already have an account?{' '}
                    <span className="text-primary">Sign in</span>
                  </>
                )}
              </button>
            </div>

            <div className="mt-4 text-center">
              <Link
                to="/"
                className="text-sm text-on-surface-variant hover:text-on-surface transition-colors"
              >
                Continue as guest →
              </Link>
            </div>
          </Card.Content>
        </Card>
      </div>
    </div>
  );
}
