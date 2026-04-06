/**
 * Search Page - Multi-entity search with filtering
 * Following Stitch Design System
 */

import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { searchAPI } from '../api/services';
import type { SearchResponse } from '../api/types';

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlQuery = searchParams.get('q') || '';

  const [query, setQuery] = useState(urlQuery);
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Execute search when URL query changes
  useEffect(() => {
    if (urlQuery && urlQuery.length >= 2) {
      setQuery(urlQuery);
      performSearch(urlQuery);
    }
  }, [urlQuery]);

  async function performSearch(searchQuery: string) {
    setLoading(true);
    setError('');

    try {
      const data = await searchAPI.search(searchQuery);
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setResults(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (query.length < 2) {
      setError('Search query must be at least 2 characters');
      return;
    }

    // Update URL with query
    setSearchParams({ q: query });
  }

  return (
    <>
      <TopBar />

      <main className="pb-32">
        {/* Page Header */}
        <section className="px-8 py-12">
          <h1 className="font-headline text-6xl font-bold text-white tracking-tighter mb-4">
            Buscar
          </h1>
          <p className="text-on-surface-variant text-lg">
            Encontre artistas, álbuns e músicas
          </p>
        </section>

        {/* Search Form */}
        <section className="px-8 mb-8">
          <form onSubmit={handleSearch} className="max-w-3xl">
            <div className="relative">
              <input
                type="search"
                placeholder="Pesquisar músicas, artistas, álbuns..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full px-6 py-4 bg-surface-container rounded-2xl text-white placeholder-on-surface-variant focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button
                type="submit"
                disabled={loading}
                className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed rounded-xl font-bold hover:scale-105 transition-transform disabled:opacity-50"
              >
                {loading ? 'Buscando...' : 'Buscar'}
              </button>
            </div>
            {error && (
              <p className="text-error mt-2 text-sm">{error}</p>
            )}
          </form>
        </section>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Icon
              name="refresh"
              size="lg"
              className="animate-spin text-on-surface-variant"
              decorative
            />
          </div>
        )}

        {/* Empty State - No search yet */}
        {!results && !loading && !urlQuery && (
          <div className="text-center py-20 px-8">
            <div className="w-24 h-24 rounded-3xl bg-surface-container mx-auto mb-6 flex items-center justify-center">
              <Icon
                name="search"
                size="xl"
                className="text-on-surface-variant/40"
                decorative
              />
            </div>
            <h3 className="font-headline text-2xl font-bold text-white mb-2">
              Comece a buscar
            </h3>
            <p className="text-on-surface-variant">
              Digite no campo acima para encontrar músicas, artistas e álbuns
            </p>
          </div>
        )}

        {/* Results */}
        {results && !loading && (
          <div className="px-8">
            <p className="text-on-surface-variant mb-8">
              {results.total_count} resultados para "{query}"
            </p>

            {/* Artists */}
            {results.artists.length > 0 && (
              <section className="mb-12">
                <h2 className="font-headline text-3xl font-bold text-white mb-6">
                  Artistas
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                  {results.artists.map((artist) => (
                    <Link
                      key={artist.id}
                      to={`/artists/${artist.id}`}
                      className="group"
                    >
                      <div className="aspect-square rounded-2xl bg-surface-container overflow-hidden mb-3 group-hover:scale-105 transition-transform">
                        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-dim/20 to-secondary/20">
                          <Icon
                            name="person"
                            size="xl"
                            className="text-primary"
                            decorative
                          />
                        </div>
                      </div>
                      <h3 className="font-bold text-white truncate">
                        {artist.name}
                      </h3>
                      <p className="text-sm text-on-surface-variant">
                        {artist.albums_count} álbuns
                      </p>
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* Albums */}
            {results.albums.length > 0 && (
              <section className="mb-12">
                <h2 className="font-headline text-3xl font-bold text-white mb-6">
                  Álbuns
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
                  {results.albums.map((album) => (
                    <Link
                      key={album.id}
                      to={`/albums/${album.id}`}
                      className="group"
                    >
                      <div className="aspect-square rounded-2xl bg-surface-container overflow-hidden mb-3 group-hover:scale-105 transition-transform">
                        {album.cover_art_url ? (
                          <img
                            src={album.cover_art_url}
                            alt={album.title}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-dim/20 to-secondary/20">
                            <Icon
                              name="album"
                              size="xl"
                              className="text-primary"
                              decorative
                            />
                          </div>
                        )}
                      </div>
                      <h3 className="font-bold text-white truncate">
                        {album.title}
                      </h3>
                      <p className="text-sm text-on-surface-variant truncate">
                        {album.artist_name}
                      </p>
                      {album.release_year && (
                        <p className="text-xs text-on-surface-variant/70">
                          {album.release_year}
                          {album.genre && ` · ${album.genre}`}
                        </p>
                      )}
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* Songs */}
            {results.songs.length > 0 && (
              <section className="mb-12">
                <h2 className="font-headline text-3xl font-bold text-white mb-6">
                  Músicas
                </h2>
                <div className="bg-surface-container rounded-2xl overflow-hidden">
                  {results.songs.map((song, index) => (
                    <div
                      key={song.id}
                      className={`flex items-center gap-4 p-4 hover:bg-surface-bright transition-colors group ${
                        index !== 0 ? 'border-t border-white/5' : ''
                      }`}
                    >
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-dim/20 to-secondary/20 flex items-center justify-center flex-shrink-0">
                        <Icon
                          name="music_note"
                          size="sm"
                          className="text-primary"
                          decorative
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-bold text-white truncate">
                          {song.title}
                        </p>
                        <p className="text-sm text-on-surface-variant truncate">
                          {song.artist_name} · {song.album_title}
                        </p>
                      </div>
                      {song.average_rating && (
                        <div className="flex items-center gap-1 text-on-surface-variant">
                          <Icon name="star" size="sm" decorative />
                          <span className="text-sm">
                            {typeof song.average_rating === 'string'
                              ? parseFloat(song.average_rating).toFixed(1)
                              : song.average_rating.toFixed(1)
                            }
                          </span>
                        </div>
                      )}
                      <button className="opacity-0 group-hover:opacity-100 w-10 h-10 rounded-full bg-primary flex items-center justify-center hover:scale-110 transition-all">
                        <Icon
                          name="play_arrow"
                          size="sm"
                          className="text-on-primary"
                          decorative
                        />
                      </button>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* No Results */}
            {results.total_count === 0 && (
              <div className="text-center py-20">
                <div className="w-24 h-24 rounded-3xl bg-surface-container mx-auto mb-6 flex items-center justify-center">
                  <Icon
                    name="search_off"
                    size="xl"
                    className="text-on-surface-variant/40"
                    decorative
                  />
                </div>
                <h3 className="font-headline text-2xl font-bold text-white mb-2">
                  Nenhum resultado encontrado
                </h3>
                <p className="text-on-surface-variant">
                  Tente buscar por outro termo: "{query}"
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </>
  );
}
