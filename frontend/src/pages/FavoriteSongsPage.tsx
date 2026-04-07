/**
 * Favorite Songs Page - Lista de músicas curtidas
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { useAuth } from '../context/AuthContext';
import { favoritesAPI } from '../api/services';

interface FavoriteSong {
  id: number;
  title: string;
  artist_id: number;
  artist_name: string;
  album_id: number;
  duration_seconds: number;
  genre?: string;
}

export function FavoriteSongsPage() {
  const { user } = useAuth();
  const [songs, setSongs] = useState<FavoriteSong[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadFavorites();
    }
  }, [user]);

  async function loadFavorites() {
    try {
      const data = await favoritesAPI.listFavoriteSongs();
      setSongs(data.items);
    } catch (error) {
      console.error('Failed to load favorites:', error);
    } finally {
      setLoading(false);
    }
  }

  async function removeFavorite(songId: number) {
    try {
      await favoritesAPI.unfavoriteSong(songId);
      setSongs(songs.filter(s => s.id !== songId));
    } catch (error) {
      console.error('Failed to remove favorite:', error);
    }
  }

  function formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  if (!user) {
    return (
      <>
        <TopBar />
        <div className="flex items-center justify-center min-h-screen">
          <p className="text-on-surface-variant">Faça login para ver suas músicas curtidas</p>
        </div>
      </>
    );
  }

  return (
    <>
      <TopBar />

      <main className="pb-32">
        {/* Hero */}
        <section className="px-8 pt-12 pb-8">
          <div className="flex items-end gap-8">
            <div className="w-64 h-64 rounded-2xl bg-gradient-to-br from-[#450074] to-[#a533ff] flex items-center justify-center shadow-2xl">
              <Icon name="favorite" size="xl" className="text-white" decorative />
            </div>

            <div className="flex-1 pb-4">
              <span className="text-xs uppercase tracking-widest text-on-surface-variant mb-2 block">
                Playlist
              </span>
              <h1 className="text-5xl md:text-7xl font-headline font-bold text-white mb-6 tracking-tighter">
                Músicas Curtidas
              </h1>
              <div className="flex items-center gap-4 text-sm">
                <span className="font-bold text-white">{user.username}</span>
                <span className="w-1 h-1 bg-outline-variant rounded-full" />
                <span className="text-on-surface-variant">
                  {songs.length} {songs.length === 1 ? 'música' : 'músicas'}
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* Controls */}
        <section className="px-8 py-6">
          <div className="flex items-center gap-4">
            <button className="w-14 h-14 rounded-full bg-gradient-to-r from-primary-dim to-secondary flex items-center justify-center text-on-primary-fixed shadow-lg hover:scale-105 transition-transform">
              <Icon name="play_arrow" size="lg" decorative />
            </button>
          </div>
        </section>

        {/* Songs List */}
        <section className="px-8">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Icon name="refresh" size="lg" className="animate-spin text-on-surface-variant" decorative />
            </div>
          ) : songs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="w-24 h-24 rounded-full bg-surface-container flex items-center justify-center mb-6">
                <Icon name="favorite_border" size="xl" className="text-on-surface-variant" decorative />
              </div>
              <h3 className="font-headline text-2xl font-bold text-white mb-2">
                Nenhuma música curtida
              </h3>
              <p className="text-on-surface-variant text-center max-w-md mb-8">
                Explore e curta suas músicas favoritas para vê-las aqui
              </p>
              <Link to="/explore">
                <button className="px-6 py-3 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed rounded-full font-bold hover:scale-105 transition-transform">
                  Explorar Música
                </button>
              </Link>
            </div>
          ) : (
            <div className="space-y-1">
              {songs.map((song, index) => (
                <div
                  key={song.id}
                  className="group flex items-center gap-4 p-4 rounded-xl hover:bg-white/5 transition-all border-b border-outline-variant/10"
                >
                  <div className="w-10 flex justify-center">
                    <span className="text-on-surface-variant group-hover:hidden font-mono">
                      {String(index + 1).padStart(2, '0')}
                    </span>
                    <Icon
                      name="play_arrow"
                      size="sm"
                      className="hidden group-hover:block text-primary"
                      decorative
                    />
                  </div>

                  <Link to={`/songs/${song.id}`} className="flex-1">
                    <h4 className="text-white font-bold hover:underline">{song.title}</h4>
                    <Link
                      to={`/artists/${song.artist_id}`}
                      className="text-xs text-on-surface-variant hover:underline"
                    >
                      {song.artist_name}
                    </Link>
                  </Link>

                  {song.genre && (
                    <div className="hidden md:block px-3 py-1 rounded-full bg-surface-container text-xs">
                      {song.genre}
                    </div>
                  )}

                  <div className="hidden md:flex items-center gap-8 text-on-surface-variant text-sm">
                    <button
                      onClick={() => removeFavorite(song.id)}
                      className="opacity-0 group-hover:opacity-100 hover:text-tertiary transition-all"
                    >
                      <Icon name="favorite" size="sm" decorative />
                    </button>
                    <span className="font-mono">{formatDuration(song.duration_seconds)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </>
  );
}
