/**
 * Sidebar Navigation - Following Stitch Mockup Design
 * Fixed left sidebar with brand, navigation, and user actions
 */

import { Link, useLocation } from 'react-router-dom';
import { Icon } from './Icon';
import { useAuth } from '../context/AuthContext';

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className = '' }: SidebarProps) {
  const location = useLocation();
  const { user, logout } = useAuth();

  const isActive = (path: string) => {
    if (path === '/favorites') {
      return location.pathname === '/favorites' || location.pathname === '/library/favorites';
    }
    return location.pathname === path;
  };

  return (
    <aside
      className={`h-screen w-64 fixed left-0 top-0 bg-background flex flex-col p-6 border-r border-white/5 font-body font-medium z-50 hidden md:flex ${className}`}
    >
      {/* Brand */}
      <div className="flex items-center gap-3 mb-12">
        <div className="w-10 h-10 bg-gradient-to-br from-primary-dim to-secondary rounded-lg flex items-center justify-center">
          <Icon
            name="pulse_alert"
            size="md"
            className="text-on-primary-fixed"
            decorative
          />
        </div>
        <div>
          <h1 className="text-xl font-black text-white leading-none font-headline">
            Sonic
          </h1>
          <p className="text-xs text-purple-300/50 uppercase tracking-widest">
            Immersive Audio
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2">
        <Link
          to="/"
          className={`flex items-center gap-4 p-3 rounded-lg group transition-all ${
            isActive('/')
              ? 'text-white bg-white/10 translate-x-1'
              : 'text-purple-300/50 hover:bg-white/5 hover:text-white'
          }`}
        >
          <Icon
            name="home"
            size="md"
            className="transition-transform group-hover:translate-x-1"
            decorative
          />
          <span>Home</span>
        </Link>

        <Link
          to="/explore"
          className={`flex items-center gap-4 p-3 rounded-lg group transition-all ${
            isActive('/explore')
              ? 'text-white bg-white/10 translate-x-1'
              : 'text-purple-300/50 hover:bg-white/5 hover:text-white'
          }`}
        >
          <Icon
            name="explore"
            size="md"
            className="transition-transform group-hover:translate-x-1"
            decorative
          />
          <span>Explorar</span>
        </Link>

        <Link
          to="/library"
          className={`flex items-center gap-4 p-3 rounded-lg group transition-all ${
            isActive('/library')
              ? 'text-white bg-white/10 translate-x-1'
              : 'text-purple-300/50 hover:bg-white/5 hover:text-white'
          }`}
        >
          <Icon
            name="library_music"
            size="md"
            className="transition-transform group-hover:translate-x-1"
            decorative
          />
          <span>Biblioteca</span>
        </Link>

        {user && (
          <>
            <Link
              to="/favorites"
              className={`flex items-center gap-4 p-3 rounded-lg group transition-all ${
                isActive('/favorites')
                  ? 'text-white bg-white/10 translate-x-1'
                  : 'text-purple-300/50 hover:bg-white/5 hover:text-white'
              }`}
            >
              <Icon
                name="favorite"
                size="md"
                className="transition-transform group-hover:translate-x-1"
                decorative
              />
              <span>Favoritos</span>
            </Link>

            <Link
              to="/playlists"
              className={`flex items-center gap-4 p-3 rounded-lg group transition-all ${
                isActive('/playlists')
                  ? 'text-white bg-white/10 translate-x-1'
                  : 'text-purple-300/50 hover:bg-white/5 hover:text-white'
              }`}
            >
              <Icon
                name="queue_music"
                size="md"
                className="transition-transform group-hover:translate-x-1"
                decorative
              />
              <span>Playlists</span>
            </Link>
          </>
        )}
      </nav>

      {/* Bottom Actions */}
      <div className="mt-auto pt-6 border-t border-white/5">
        {user ? (
          <>
            <button className="w-full py-3 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed font-bold rounded-full mb-6 hover:scale-105 transition-transform">
              Upgrade VIP
            </button>
            <div className="space-y-2">
              <Link
                to="/settings"
                className="flex items-center gap-4 p-3 text-purple-300/50 hover:text-white transition-colors"
              >
                <Icon name="settings" size="sm" decorative />
                <span className="text-sm">Configurações</span>
              </Link>
              <button
                onClick={logout}
                className="flex items-center gap-4 p-3 text-purple-300/50 hover:text-white transition-colors w-full text-left"
              >
                <Icon name="logout" size="sm" decorative />
                <span className="text-sm">Sair</span>
              </button>
            </div>
          </>
        ) : (
          <Link to="/login">
            <button className="w-full py-3 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed font-bold rounded-full hover:scale-105 transition-transform">
              Entrar / Cadastrar
            </button>
          </Link>
        )}
      </div>
    </aside>
  );
}
