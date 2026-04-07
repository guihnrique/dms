/**
 * Song Detail Page - Individual song details with reviews
 * Following Stitch Design System
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { AddToPlaylistModal } from '../components/AddToPlaylistModal';
import { useAuth } from '../context/AuthContext';
import { songsAPI, reviewsAPI, favoritesAPI } from '../api/services';
import type { Song, Review } from '../api/types';

export function SongDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [song, setSong] = useState<Song | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoritingLoading, setFavoritingLoading] = useState(false);
  const [votedReviews, setVotedReviews] = useState<Set<string>>(new Set());
  const [votingReview, setVotingReview] = useState<string | null>(null);
  const [showPlaylistModal, setShowPlaylistModal] = useState(false);

  useEffect(() => {
    if (id) {
      loadSong();
      loadReviews();
      if (user) {
        checkFavoriteStatus();
      }
    }
  }, [id, user]);

  useEffect(() => {
    if (user && reviews.length > 0) {
      loadUserVotes();
    }
  }, [user, reviews]);

  async function loadSong() {
    try {
      setLoading(true);
      const data = await songsAPI.get(Number(id));
      setSong(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load song');
    } finally {
      setLoading(false);
    }
  }

  async function loadReviews() {
    try {
      setReviewsLoading(true);
      const data = await reviewsAPI.listForSong(Number(id), 1, 10);
      setReviews(data.items);
    } catch (err) {
      console.error('Failed to load reviews:', err);
    } finally {
      setReviewsLoading(false);
    }
  }

  async function checkFavoriteStatus() {
    if (!user || !id) return;
    try {
      const { favorited } = await favoritesAPI.checkSongFavoriteStatus(Number(id));
      setIsFavorited(favorited);
    } catch (err) {
      console.error('Failed to check favorite status:', err);
    }
  }

  async function loadUserVotes() {
    if (!user || reviews.length === 0) return;
    try {
      const reviewIds = reviews.map(r => r.id);
      const votes = await reviewsAPI.checkVotes(reviewIds);
      const votedIds = Object.keys(votes).filter(id => votes[id] === 'helpful');
      setVotedReviews(new Set(votedIds));
    } catch (err) {
      console.error('Failed to load user votes:', err);
    }
  }

  async function toggleFavorite() {
    if (!user || !id) return;

    try {
      setFavoritingLoading(true);
      if (isFavorited) {
        await favoritesAPI.unfavoriteSong(Number(id));
        setIsFavorited(false);
      } else {
        await favoritesAPI.favoriteSong(Number(id));
        setIsFavorited(true);
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    } finally {
      setFavoritingLoading(false);
    }
  }

  async function voteReview(reviewId: string) {
    if (!user || votedReviews.has(reviewId)) return;

    try {
      setVotingReview(reviewId);
      await reviewsAPI.vote(reviewId, 'helpful');

      // Update local state
      setVotedReviews(prev => new Set(prev).add(reviewId));
      setReviews(prevReviews =>
        prevReviews.map(review =>
          review.id === reviewId
            ? { ...review, helpful_count: review.helpful_count + 1 }
            : review
        )
      );
    } catch (err) {
      console.error('Failed to vote on review:', err);
    } finally {
      setVotingReview(null);
    }
  }

  function formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  if (loading) {
    return (
      <>
        <TopBar />
        <div className="flex items-center justify-center min-h-screen">
          <Icon
            name="refresh"
            size="xl"
            className="animate-spin text-on-surface-variant"
            decorative
          />
        </div>
      </>
    );
  }

  if (error || !song) {
    return (
      <>
        <TopBar />
        <div className="flex flex-col items-center justify-center min-h-screen px-8">
          <div className="w-24 h-24 rounded-3xl bg-surface-container mb-6 flex items-center justify-center">
            <Icon
              name="error"
              size="xl"
              className="text-error"
              decorative
            />
          </div>
          <h2 className="font-headline text-3xl font-bold text-white mb-2">
            Música não encontrada
          </h2>
          <p className="text-on-surface-variant mb-6">{error}</p>
          <Link to="/explore">
            <button className="px-6 py-3 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed rounded-full font-bold hover:scale-105 transition-transform">
              Explorar Músicas
            </button>
          </Link>
        </div>
      </>
    );
  }

  return (
    <>
      <TopBar />

      <main className="pb-32">
        {/* Hero Section */}
        <section className="relative px-8 pt-12 pb-20">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-b from-primary-dim/20 via-background to-background" />

          <div className="relative max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row gap-8 items-start">
              {/* Album Art */}
              <div className="w-full md:w-80 flex-shrink-0">
                <div className="group relative aspect-square rounded-3xl bg-surface-container overflow-hidden shadow-2xl">
                  {song.album?.cover_art_url ? (
                    <img
                      src={song.album.cover_art_url}
                      alt={song.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-dim/30 to-secondary/30">
                      <Icon
                        name="music_note"
                        size="xl"
                        className="text-primary"
                        decorative
                      />
                    </div>
                  )}

                  {/* Play button overlay */}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <button className="w-20 h-20 rounded-full bg-primary flex items-center justify-center hover:scale-110 transition-transform shadow-2xl">
                      <Icon
                        name="play_arrow"
                        size="lg"
                        className="text-on-primary ml-1"
                        decorative
                      />
                    </button>
                  </div>
                </div>
              </div>

              {/* Song Info */}
              <div className="flex-1 min-w-0">
                <div className="mb-4">
                  <span className="inline-block px-4 py-1 rounded-full bg-tertiary-container/20 text-tertiary text-xs font-bold tracking-wider uppercase mb-4">
                    Música
                  </span>
                </div>

                <h1 className="font-headline text-6xl md:text-7xl font-extrabold text-white tracking-tighter mb-6 leading-none">
                  {song.title}
                </h1>

                {/* Artist & Album Links */}
                <div className="flex flex-wrap items-center gap-2 text-lg mb-6">
                  {song.album?.artist && (
                    <>
                      <Link
                        to={`/artists/${song.album.artist_id}`}
                        className="font-bold text-white hover:text-primary transition-colors"
                      >
                        {song.album.artist.name}
                      </Link>
                      <span className="text-on-surface-variant">·</span>
                    </>
                  )}
                  {song.album && (
                    <Link
                      to={`/albums/${song.album_id}`}
                      className="text-on-surface-variant hover:text-white transition-colors"
                    >
                      {song.album.title}
                    </Link>
                  )}
                </div>

                {/* Stats */}
                <div className="flex flex-wrap items-center gap-6 mb-8">
                  <div className="flex items-center gap-2">
                    <Icon name="schedule" size="sm" className="text-on-surface-variant" decorative />
                    <span className="text-on-surface-variant">
                      {formatDuration(song.duration_seconds)}
                    </span>
                  </div>

                  {song.average_rating && (
                    <div className="flex items-center gap-2">
                      <Icon name="star" size="sm" className="text-tertiary" decorative />
                      <span className="font-bold text-white">
                        {typeof song.average_rating === 'string'
                          ? parseFloat(song.average_rating).toFixed(1)
                          : song.average_rating.toFixed(1)}
                      </span>
                      <span className="text-on-surface-variant text-sm">
                        ({song.review_count} {song.review_count === 1 ? 'avaliação' : 'avaliações'})
                      </span>
                    </div>
                  )}

                  {song.genre && (
                    <div className="px-3 py-1 rounded-full bg-surface-container">
                      <span className="text-on-surface text-sm">{song.genre}</span>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-4">
                  <button className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed rounded-full font-bold hover:scale-105 transition-transform shadow-lg shadow-primary/20">
                    <Icon name="play_arrow" size="md" decorative />
                    Reproduzir
                  </button>

                  {user && (
                    <>
                      <button
                        onClick={toggleFavorite}
                        disabled={favoritingLoading}
                        className={`flex items-center gap-2 px-6 py-4 rounded-full font-bold transition-all ${
                          isFavorited
                            ? 'bg-tertiary-container text-tertiary hover:bg-tertiary-container/80'
                            : 'bg-surface-container hover:bg-surface-bright text-white'
                        } ${favoritingLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        <Icon name={isFavorited ? 'favorite' : 'favorite_border'} size="sm" decorative />
                        {isFavorited ? 'Curtido' : 'Curtir'}
                      </button>

                      <button
                        onClick={() => setShowPlaylistModal(true)}
                        className="flex items-center gap-2 px-6 py-4 bg-surface-container hover:bg-surface-bright rounded-full font-bold transition-colors"
                      >
                        <Icon name="add" size="sm" decorative />
                        Adicionar à Playlist
                      </button>
                    </>
                  )}

                  <button className="w-12 h-12 rounded-full bg-surface-container hover:bg-surface-bright flex items-center justify-center transition-colors">
                    <Icon name="more_vert" size="sm" decorative />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Add to Playlist Modal */}
        {user && song && (
          <AddToPlaylistModal
            songId={song.id}
            isOpen={showPlaylistModal}
            onClose={() => setShowPlaylistModal(false)}
            onSuccess={() => {
              // Optional: show success message
              console.log('Added to playlist successfully');
            }}
          />
        )}

        {/* Reviews Section */}
        <section className="px-8 max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-headline text-3xl font-bold text-white">
              Avaliações
            </h2>
            {user && (
              <Link to={`/songs/${id}/review`}>
                <button className="flex items-center gap-2 px-6 py-3 bg-surface-container hover:bg-surface-bright rounded-full font-bold transition-colors">
                  <Icon name="rate_review" size="sm" decorative />
                  Escrever Avaliação
                </button>
              </Link>
            )}
          </div>

          {reviewsLoading ? (
            <div className="flex items-center justify-center py-12">
              <Icon
                name="refresh"
                size="lg"
                className="animate-spin text-on-surface-variant"
                decorative
              />
            </div>
          ) : reviews.length > 0 ? (
            <div className="space-y-4">
              {reviews.map((review) => (
                <div
                  key={review.id}
                  className="bg-surface-container rounded-2xl p-6 hover:bg-surface-bright transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-bold text-white">{review.username}</p>
                      <div className="flex items-center gap-1 mt-1">
                        {Array.from({ length: 5 }, (_, i) => (
                          <Icon
                            key={i}
                            name={i < review.rating ? 'star' : 'star_border'}
                            size="sm"
                            className={i < review.rating ? 'text-tertiary' : 'text-on-surface-variant'}
                            decorative
                          />
                        ))}
                      </div>
                    </div>
                    <span className="text-sm text-on-surface-variant">
                      {new Date(review.created_at).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                  {review.body && (
                    <p className="text-on-surface">{review.body}</p>
                  )}
                  <div className="flex items-center gap-4 mt-4">
                    {user && (
                      <button
                        onClick={() => voteReview(review.id)}
                        disabled={votedReviews.has(review.id) || votingReview === review.id}
                        className={`flex items-center gap-1 text-sm transition-colors ${
                          votedReviews.has(review.id)
                            ? 'text-tertiary cursor-default'
                            : 'text-on-surface-variant hover:text-white'
                        } ${votingReview === review.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        <Icon name="thumb_up" size="sm" decorative />
                        Útil ({review.helpful_count})
                      </button>
                    )}
                    {!user && (
                      <div className="flex items-center gap-1 text-sm text-on-surface-variant">
                        <Icon name="thumb_up" size="sm" decorative />
                        Útil ({review.helpful_count})
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-surface-container rounded-2xl">
              <div className="w-16 h-16 rounded-2xl bg-surface-container-highest/40 mx-auto mb-4 flex items-center justify-center">
                <Icon
                  name="rate_review"
                  size="lg"
                  className="text-on-surface-variant/40"
                  decorative
                />
              </div>
              <h3 className="font-headline text-xl font-bold text-white mb-2">
                Nenhuma avaliação ainda
              </h3>
              <p className="text-on-surface-variant mb-6">
                Seja o primeiro a avaliar esta música
              </p>
              {user && (
                <Link to={`/songs/${id}/review`}>
                  <button className="px-6 py-3 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed rounded-full font-bold hover:scale-105 transition-transform">
                    Escrever Avaliação
                  </button>
                </Link>
              )}
            </div>
          )}
        </section>
      </main>
    </>
  );
}
