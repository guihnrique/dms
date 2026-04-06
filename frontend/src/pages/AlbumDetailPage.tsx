/**
 * Album Detail Page - Following Stitch Mockup
 * Album hero + tracklist + reviews section
 */

import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { albumsAPI, songsAPI, reviewsAPI } from '../api/services';
import type { Album, Song, Review } from '../api/types';

export function AlbumDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [album, setAlbum] = useState<Album | null>(null);
  const [songs, setSongs] = useState<Song[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadAlbumData();
    }
  }, [id]);

  async function loadAlbumData() {
    try {
      const [albumData, songsData] = await Promise.all([
        albumsAPI.get(Number(id)),
        songsAPI.list(1, 20, Number(id)),
      ]);
      setAlbum(albumData);
      setSongs(songsData.items);

      // Load reviews for first song if available
      if (songsData.items.length > 0) {
        const reviewsData = await reviewsAPI.listForSong(songsData.items[0].id, 1, 5);
        setReviews(reviewsData.items);
      }
    } catch (error) {
      console.error('Failed to load album:', error);
    } finally {
      setLoading(false);
    }
  }

  function formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  function calculateTotalDuration(): string {
    const totalSeconds = songs.reduce((acc, song) => acc + song.duration_seconds, 0);
    const minutes = Math.floor(totalSeconds / 60);
    return `${songs.length} Tracks • ${minutes} min`;
  }

  if (loading) {
    return (
      <>
        <TopBar />
        <div className="flex items-center justify-center min-h-screen">
          <Icon
            name="refresh"
            size="lg"
            className="animate-spin text-on-surface-variant"
            decorative
          />
        </div>
      </>
    );
  }

  if (!album) {
    return (
      <>
        <TopBar />
        <div className="flex items-center justify-center min-h-screen px-8">
          <div className="text-center">
            <h1 className="font-headline text-4xl mb-4">Álbum não encontrado</h1>
            <Link to="/explore" className="text-secondary hover:underline">
              Voltar para Explorar
            </Link>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <TopBar />

      <main className="pb-32">
        {/* Album Hero Section */}
        <section className="px-8 pt-12 pb-12">
          <div className="flex flex-col lg:flex-row gap-12 items-end">
            {/* Album Cover */}
            <div className="relative group flex-shrink-0">
              <div className="absolute -inset-4 bg-primary-dim/20 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
              <div className="w-80 h-80 md:w-96 md:h-96 relative z-10 rounded-2xl overflow-hidden shadow-2xl group-hover:scale-[1.02] transition-transform duration-500">
                {album.cover_art_url ? (
                  <img
                    src={album.cover_art_url}
                    alt={album.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-surface-bright">
                    <Icon
                      name="album"
                      size="lg"
                      className="text-on-surface-variant"
                      decorative
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Album Info */}
            <div className="flex-1 z-10 pb-4">
              <span className="px-3 py-1 bg-primary-dim/20 text-primary text-xs font-bold rounded-full tracking-widest uppercase mb-4 inline-block">
                {album.genre || 'Electronic'}
              </span>
              <h2 className="text-5xl md:text-7xl font-bold font-headline tracking-tighter text-white mb-4">
                {album.title}
              </h2>
              <div className="flex items-center gap-4 mb-8 flex-wrap">
                <Link
                  to={`/artists/${album.artist_id}`}
                  className="text-xl font-medium text-white hover:underline"
                >
                  {album.artist_name}
                </Link>
                {album.release_year && (
                  <>
                    <span className="w-1 h-1 bg-outline-variant rounded-full" />
                    <span className="text-on-surface-variant font-medium">
                      {album.release_year}
                    </span>
                  </>
                )}
                <span className="w-1 h-1 bg-outline-variant rounded-full" />
                <span className="text-on-surface-variant font-medium">
                  {calculateTotalDuration()}
                </span>
              </div>

              <div className="flex flex-wrap gap-4">
                <button className="px-8 py-3 rounded-full bg-gradient-to-r from-primary-dim to-secondary text-black font-black text-sm uppercase tracking-wider flex items-center gap-2 hover:shadow-[0_0_30px_rgba(165,51,255,0.4)] transition-all active:scale-95">
                  <Icon name="play_arrow" size="sm" decorative />
                  Reproduzir Álbum
                </button>
                <button className="px-8 py-3 rounded-full border border-outline/20 backdrop-blur-md bg-white/5 text-white font-bold text-sm uppercase tracking-wider flex items-center gap-2 hover:bg-white/10 transition-all">
                  <Icon name="playlist_add" size="sm" decorative />
                  Adicionar à Playlist
                </button>
                <button className="w-12 h-12 flex items-center justify-center rounded-full border border-outline/20 backdrop-blur-md bg-white/5 text-tertiary hover:text-white transition-colors">
                  <Icon name="favorite" size="sm" decorative />
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Tracks Section */}
        <section className="px-8 py-12">
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-2xl font-bold font-headline text-white">
              Tracklist
            </h3>
          </div>

          <div className="space-y-1">
            {songs.map((song, index) => (
              <div
                key={song.id}
                className="group flex items-center gap-4 p-4 rounded-xl hover:bg-white/5 transition-all cursor-pointer border-b border-outline-variant/10"
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

                <div className="flex-1">
                  <h4 className="text-white font-bold">{song.title}</h4>
                  <p className="text-xs text-on-surface-variant">
                    {song.artist_name}
                  </p>
                </div>

                <div className="hidden md:flex items-center gap-8 text-on-surface-variant text-sm">
                  <button className="opacity-0 group-hover:opacity-100 hover:text-white transition-all">
                    <Icon name="favorite" size="sm" decorative />
                  </button>
                  <span className="font-mono">
                    {formatDuration(song.duration_seconds)}
                  </span>
                  <button>
                    <Icon name="more_horiz" size="sm" decorative />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Reviews Section */}
        {reviews.length > 0 && (
          <section className="px-8 py-12">
            <h3 className="text-2xl font-bold font-headline text-white mb-8">
              Avaliações e Reviews
            </h3>

            <div className="space-y-6">
              {reviews.map((review) => (
                <div
                  key={review.id}
                  className="p-6 rounded-2xl bg-surface-container-low/50 border border-outline-variant/10"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-dim to-secondary flex items-center justify-center flex-shrink-0">
                      <span className="text-white font-bold text-sm">
                        {review.username[0].toUpperCase()}
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-bold text-white">{review.username}</h4>
                        <div className="flex gap-0.5">
                          {Array.from({ length: 5 }).map((_, i) => (
                            <Icon
                              key={i}
                              name="star"
                              size="sm"
                              className={
                                i < review.rating
                                  ? 'text-secondary'
                                  : 'text-on-surface-variant/30'
                              }
                              decorative
                            />
                          ))}
                        </div>
                      </div>
                      {review.body && (
                        <p className="text-on-surface-variant">{review.body}</p>
                      )}
                      <div className="flex items-center gap-4 mt-3 text-sm">
                        <button className="flex items-center gap-1 text-on-surface-variant hover:text-white transition-colors">
                          <Icon name="thumb_up" size="sm" decorative />
                          <span>{review.helpful_count}</span>
                        </button>
                        <span className="text-on-surface-variant text-xs">
                          {new Date(review.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </>
  );
}
