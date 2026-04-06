/**
 * TopBar - Sticky search and user actions
 * Following Stitch mockup design with glassmorphism
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icon } from './Icon';
import { useAuth } from '../context/AuthContext';

export function TopBar() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  }

  return (
    <header className="w-full sticky top-0 flex justify-between items-center px-8 py-4 z-40 backdrop-blur-xl bg-white/5">
      {/* Search */}
      <div className="flex items-center flex-1 max-w-xl">
        <form onSubmit={handleSearch} className="relative w-full group">
          <Icon
            name="search"
            size="sm"
            className="absolute left-4 top-1/2 -translate-y-1/2 text-purple-200/40 group-focus-within:text-secondary transition-colors"
            decorative
          />
          <input
            type="text"
            className="w-full bg-surface-container-lowest/50 border-none rounded-full py-2.5 pl-12 pr-6 text-sm text-white placeholder-purple-200/30 focus:ring-1 focus:ring-primary-dim transition-all"
            placeholder="Procurar artistas, álbuns ou ritmos..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-6 ml-8">
        <button className="text-purple-200/60 hover:text-cyan-400 transition-colors">
          <Icon name="notifications" size="md" decorative />
        </button>
        <button className="text-purple-200/60 hover:text-cyan-400 transition-colors">
          <Icon name="settings" size="md" decorative />
        </button>
        {user && (
          <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-primary-dim/30 hover:border-primary-dim transition-colors cursor-pointer">
            <div className="w-full h-full bg-gradient-to-br from-primary-dim to-secondary flex items-center justify-center">
              <Icon name="person" size="md" className="text-white" decorative />
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
