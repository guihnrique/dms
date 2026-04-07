/**
 * Create Review Page - Write a review for a song
 * Following Stitch Design System
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { useAuth } from '../context/AuthContext';
import { songsAPI, reviewsAPI } from '../api/services';
import type { Song } from '../api/types';

export function CreateReviewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [song, setSong] = useState<Song | null>(null);
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [reviewText, setReviewText] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (id) {
      loadSong();
    }
  }, [id, user, navigate]);

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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (rating === 0) {
      setError('Por favor, selecione uma avaliação');
      return;
    }

    try {
      setSubmitting(true);
      setError('');

      await reviewsAPI.create({
        song_id: Number(id),
        rating,
        body: reviewText.trim() || undefined,
      });

      // Redirect back to song page
      navigate(`/songs/${id}`, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit review');
    } finally {
      setSubmitting(false);
    }
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

  if (!song) {
    return (
      <>
        <TopBar />
        <div className="flex flex-col items-center justify-center min-h-screen px-8">
          <div className="w-24 h-24 rounded-3xl bg-surface-container mb-6 flex items-center justify-center">
            <Icon name="error" size="xl" className="text-error" decorative />
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
        <div className="max-w-3xl mx-auto px-8 py-12">
          {/* Back Button */}
          <Link
            to={`/songs/${id}`}
            className="inline-flex items-center gap-2 text-on-surface-variant hover:text-white transition-colors mb-8"
          >
            <Icon name="arrow_back" size="sm" decorative />
            Voltar para música
          </Link>

          {/* Page Header */}
          <div className="mb-8">
            <h1 className="font-headline text-5xl font-bold text-white tracking-tighter mb-4">
              Escrever Avaliação
            </h1>
            <div className="flex items-center gap-4">
              {song.cover_art_url && (
                <img
                  src={song.cover_art_url}
                  alt={song.title}
                  className="w-16 h-16 rounded-xl object-cover"
                />
              )}
              <div>
                <p className="font-bold text-white text-lg">{song.title}</p>
                <p className="text-on-surface-variant">
                  {song.artist_name}
                  {song.album_title && ` · ${song.album_title}`}
                </p>
              </div>
            </div>
          </div>

          {/* Review Form */}
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Rating Selection */}
            <div className="bg-surface-container rounded-2xl p-8">
              <label className="block font-bold text-white text-lg mb-4">
                Sua Avaliação *
              </label>
              <div className="flex items-center gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoverRating(star)}
                    onMouseLeave={() => setHoverRating(0)}
                    className="transition-transform hover:scale-110"
                  >
                    <Icon
                      name={
                        star <= (hoverRating || rating) ? 'star' : 'star_border'
                      }
                      size="xl"
                      className={
                        star <= (hoverRating || rating)
                          ? 'text-tertiary'
                          : 'text-on-surface-variant'
                      }
                      decorative
                    />
                  </button>
                ))}
                {rating > 0 && (
                  <span className="ml-4 font-bold text-white text-xl">
                    {rating}.0
                  </span>
                )}
              </div>
              <p className="text-sm text-on-surface-variant mt-2">
                Clique nas estrelas para avaliar
              </p>
            </div>

            {/* Review Text */}
            <div className="bg-surface-container rounded-2xl p-8">
              <label
                htmlFor="review-text"
                className="block font-bold text-white text-lg mb-4"
              >
                Comentário (Opcional)
              </label>
              <textarea
                id="review-text"
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
                placeholder="Compartilhe sua opinião sobre esta música..."
                rows={6}
                className="w-full px-4 py-3 bg-surface-bright rounded-xl text-white placeholder-on-surface-variant focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                maxLength={500}
              />
              <div className="flex items-center justify-between mt-2">
                <p className="text-sm text-on-surface-variant">
                  Máximo 500 caracteres
                </p>
                <p className="text-sm text-on-surface-variant">
                  {reviewText.length}/500
                </p>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-error-container/20 border border-error/30 rounded-2xl p-4">
                <p className="text-error text-center">{error}</p>
              </div>
            )}

            {/* Submit Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <button
                type="submit"
                disabled={submitting || rating === 0}
                className="flex-1 flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed rounded-full font-bold hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                {submitting ? (
                  <>
                    <Icon
                      name="refresh"
                      size="sm"
                      className="animate-spin"
                      decorative
                    />
                    Enviando...
                  </>
                ) : (
                  <>
                    <Icon name="send" size="sm" decorative />
                    Publicar Avaliação
                  </>
                )}
              </button>

              <Link
                to={`/songs/${id}`}
                className="sm:flex-initial flex items-center justify-center px-8 py-4 bg-surface-container hover:bg-surface-bright rounded-full font-bold transition-colors"
              >
                Cancelar
              </Link>
            </div>
          </form>

          {/* Guidelines */}
          <div className="mt-12 p-6 bg-surface-container/50 rounded-2xl border border-white/5">
            <div className="flex items-start gap-3">
              <Icon
                name="info"
                size="sm"
                className="text-secondary flex-shrink-0 mt-1"
                decorative
              />
              <div className="text-sm text-on-surface-variant">
                <p className="font-bold text-white mb-2">
                  Diretrizes para avaliações:
                </p>
                <ul className="space-y-1">
                  <li>• Seja respeitoso e construtivo</li>
                  <li>• Foque na música, não no artista pessoalmente</li>
                  <li>• Evite spoilers ou conteúdo inapropriado</li>
                  <li>• Avaliações podem ser moderadas</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
