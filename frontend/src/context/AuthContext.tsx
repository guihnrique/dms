/**
 * AuthContext - Global authentication state management
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from 'react';
import { authAPI } from '../api/services';
import type { User, LoginRequest, RegisterRequest } from '../api/types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load user on mount
  useEffect(() => {
    loadUser();
  }, []);

  async function loadUser() {
    try {
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      // User not authenticated
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  async function login(data: LoginRequest) {
    try {
      setLoading(true);
      setError(null);
      await authAPI.login(data);
      // After login, load user data from /me endpoint
      await loadUser();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function register(data: RegisterRequest) {
    try {
      setLoading(true);
      setError(null);
      const user = await authAPI.register(data);
      // Backend returns user directly on registration
      setUser(user);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    try {
      setLoading(true);
      await authAPI.logout();
      setUser(null);
      // Redirect to home page after logout
      window.location.href = '/';
    } catch (err) {
      console.error('Logout failed:', err);
      // Even if API call fails, clear local state and redirect
      setUser(null);
      window.location.href = '/';
    } finally {
      setLoading(false);
    }
  }

  function clearError() {
    setError(null);
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, error, login, register, logout, clearError }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
