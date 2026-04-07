/**
 * Artists List Page - Browse all artists
 * Following Stitch Design System
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { artistsAPI } from '../api/services';
import type { Artist } from '../api/types';

export function ArtistsListPage() {
  const [artists, setArtists] = useState<Artist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 24;

  useEffect(() => {
    loadArtists();
  }, [page]);

  async function loadArtists() {
    try {
      setLoading(true);
      const data = await artistsAPI.list(page, pageSize);
      setArtists(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load artists');
    } finally {
      setLoading(false);
    }
  }

  const totalPages = Math.ceil(total / pageSize);

  return (
    <>
      <TopBar />

      <main className="pb-32">
        {/* Page Header */}
        <section className="px-8 py-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <span className="text-secondary font-headline tracking-[0.2em] text-xs uppercase mb-2 block">
                Catálogo Completo
              </span>
              <h1 className="font-headline text-6xl font-bold text-white tracking-tighter">
                Artistas
              </h1>
              <p className="text-on-surface-variant text-lg mt-2">
                {total} artistas disponíveis
              </p>
            </div>
          </div>
        </section>

        {/* Error State */}
        {error && (
          <section className="px-8">
            <div className="bg-error-container/20 border border-error/30 rounded-2xl p-6 text-center">
              <Icon
                name="error"
                size="lg"
                className="mx-auto mb-4 text-error"
                decorative
              />
              <p className="text-error">{error}</p>
              <button
                onClick={loadArtists}
                className="mt-4 px-6 py-2 bg-error text-on-error rounded-full font-bold hover:scale-105 transition-transform"
              >
                Tentar Novamente
              </button>
            </div>
          </section>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Icon
              name="refresh"
              size="xl"
              className="animate-spin text-on-surface-variant"
              decorative
            />
          </div>
        )}

        {/* Artists Grid */}
        {!loading && !error && artists.length > 0 && (
          <section className="px-8">
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
              {artists.map((artist) => (
                <Link
                  key={artist.id}
                  to={`/artists/${artist.id}`}
                  className="group"
                >
                  <div className="relative aspect-square rounded-2xl bg-surface-container overflow-hidden mb-3 transition-all duration-300 group-hover:scale-105 group-hover:shadow-2xl group-hover:shadow-primary/20">
                    {artist.photo_url ? (
                      <img
                        src={artist.photo_url}
                        alt={artist.name}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-dim/20 to-secondary/20">
                        <Icon
                          name="person"
                          size="xl"
                          className="text-primary transition-transform group-hover:scale-110"
                          decorative
                        />
                      </div>
                    )}
                    {/* Overlay on hover */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  </div>
                  <h3 className="font-bold text-white truncate group-hover:text-primary transition-colors">
                    {artist.name}
                  </h3>
                  <p className="text-sm text-on-surface-variant">
                    {artist.albums_count} {artist.albums_count === 1 ? 'álbum' : 'álbuns'}
                  </p>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-12">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 rounded-full bg-surface-container hover:bg-surface-bright disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Icon name="arrow_back" size="sm" decorative />
                </button>

                <div className="flex items-center gap-2">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (page <= 3) {
                      pageNum = i + 1;
                    } else if (page >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = page - 2 + i;
                    }

                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`w-10 h-10 rounded-full font-bold transition-all ${
                          page === pageNum
                            ? 'bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed'
                            : 'bg-surface-container hover:bg-surface-bright text-on-surface'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 rounded-full bg-surface-container hover:bg-surface-bright disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Icon name="arrow_forward" size="sm" decorative />
                </button>
              </div>
            )}
          </section>
        )}

        {/* Empty State */}
        {!loading && !error && artists.length === 0 && (
          <div className="text-center py-20 px-8">
            <div className="w-24 h-24 rounded-3xl bg-surface-container mx-auto mb-6 flex items-center justify-center">
              <Icon
                name="person"
                size="xl"
                className="text-on-surface-variant/40"
                decorative
              />
            </div>
            <h3 className="font-headline text-2xl font-bold text-white mb-2">
              Nenhum artista encontrado
            </h3>
            <p className="text-on-surface-variant">
              Não há artistas cadastrados no momento
            </p>
          </div>
        )}
      </main>
    </>
  );
}
