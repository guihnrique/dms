/**
 * Album Detail Page - Following Stitch Mockup
 * Album hero + tracklist + reviews section
 */

import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { AddToPlaylistModal } from '../components/AddToPlaylistModal';
import { albumsAPI, songsAPI, reviewsAPI, favoritesAPI } from '../api/services';
import type { Album, Song, Review } from '../api/types';

export function AlbumDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [album, setAlbum] = useState<Album | null>(null);
  const [songs, setSongs] = useState<Song[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoritingLoading, setFavoritingLoading] = useState(false);
  const [songFavorites, setSongFavorites] = useState<Record<number, boolean>>({});
  const [votedReviews, setVotedReviews] = useState<Set<string>>(new Set());
  const [votingReview, setVotingReview] = useState<string | null>(null);
  const [showPlaylistModal, setShowPlaylistModal] = useState(false);
  const [selectedSongForPlaylist, setSelectedSongForPlaylist] = useState<number | null>(null);

  useEffect(() => {
    if (id) {
      loadAlbumData();
      checkFavoriteStatus();
    }
  }, [id]);

  useEffect(() => {
    if (reviews.length > 0) {
      loadUserVotes();
    }
  }, [reviews]);

  async function loadAlbumData() {
    try {
      const [albumData, songsData] = await Promise.all([
        albumsAPI.get(Number(id)),
        songsAPI.list(1, 20, Number(id)),
      ]);
      setAlbum(albumData);
      setSongs(songsData.items);

      // Load favorite status for all songs
      await loadSongFavorites(songsData.items.map(s => s.id));

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

  async function loadSongFavorites(songIds: number[]) {
    try {
      const favorites: Record<number, boolean> = {};
      await Promise.all(
        songIds.map(async (songId) => {
          try {
            const { favorited } = await favoritesAPI.checkSongFavoriteStatus(songId);
            favorites[songId] = favorited;
          } catch {
            favorites[songId] = false;
          }
        })
      );
      setSongFavorites(favorites);
    } catch (err) {
      console.error('Failed to load song favorites:', err);
    }
  }

  async function toggleSongFavorite(songId: number, e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();

    try {
      const currentStatus = songFavorites[songId] || false;

      if (currentStatus) {
        await favoritesAPI.unfavoriteSong(songId);
        setSongFavorites(prev => ({ ...prev, [songId]: false }));
      } else {
        await favoritesAPI.favoriteSong(songId);
        setSongFavorites(prev => ({ ...prev, [songId]: true }));
      }
    } catch (err) {
      console.error('Failed to toggle song favorite:', err);
    }
  }

  async function checkFavoriteStatus() {
    if (!id) return;
    try {
      const { favorited } = await favoritesAPI.checkAlbumFavoriteStatus(Number(id));
      setIsFavorited(favorited);
    } catch (err) {
      console.error('Failed to check favorite status:', err);
    }
  }

  async function toggleFavorite() {
    if (!id) return;

    try {
      setFavoritingLoading(true);
      if (isFavorited) {
        await favoritesAPI.unfavoriteAlbum(Number(id));
        setIsFavorited(false);
      } else {
        await favoritesAPI.favoriteAlbum(Number(id));
        setIsFavorited(true);
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err);
    } finally {
      setFavoritingLoading(false);
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

  async function loadUserVotes() {
    if (reviews.length === 0) return;
    try {
      const reviewIds = reviews.map(r => r.id);
      const votes = await reviewsAPI.checkVotes(reviewIds);
      const votedIds = Object.keys(votes).filter(id => votes[id] === 'helpful');
      setVotedReviews(new Set(votedIds));
    } catch (err) {
      console.error('Failed to load user votes:', err);
    }
  }

  async function voteReview(reviewId: string) {
    if (votedReviews.has(reviewId)) return;

    try {
      setVotingReview(reviewId);
      await reviewsAPI.vote(reviewId, 'helpful');

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
                {songs.length > 0 && (
                  <button
                    onClick={() => {
                      setSelectedSongForPlaylist(songs[0].id);
                      setShowPlaylistModal(true);
                    }}
                    className="px-8 py-3 rounded-full border border-outline/20 backdrop-blur-md bg-white/5 text-white font-bold text-sm uppercase tracking-wider flex items-center gap-2 hover:bg-white/10 transition-all"
                  >
                    <Icon name="playlist_add" size="sm" decorative />
                    Adicionar à Playlist
                  </button>
                )}
                <button
                  onClick={toggleFavorite}
                  disabled={favoritingLoading}
                  className={`w-12 h-12 flex items-center justify-center rounded-full border border-outline/20 backdrop-blur-md transition-all ${
                    isFavorited
                      ? 'bg-tertiary-container text-tertiary'
                      : 'bg-white/5 text-tertiary hover:text-white'
                  } ${favoritingLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <Icon name={isFavorited ? 'favorite' : 'favorite_border'} size="sm" decorative />
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
              <Link
                key={song.id}
                to={`/songs/${song.id}`}
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
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setSelectedSongForPlaylist(song.id);
                      setShowPlaylistModal(true);
                    }}
                    className="opacity-0 group-hover:opacity-100 hover:text-primary transition-all"
                  >
                    <Icon name="playlist_add" size="sm" decorative />
                  </button>
                  <button
                    onClick={(e) => toggleSongFavorite(song.id, e)}
                    className={`opacity-0 group-hover:opacity-100 transition-all ${
                      songFavorites[song.id] ? 'text-tertiary opacity-100' : 'hover:text-white'
                    }`}
                  >
                    <Icon name={songFavorites[song.id] ? 'favorite' : 'favorite_border'} size="sm" decorative />
                  </button>
                  <span className="font-mono">
                    {formatDuration(song.duration_seconds)}
                  </span>
                  <button onClick={(e) => e.preventDefault()}>
                    <Icon name="more_horiz" size="sm" decorative />
                  </button>
                </div>
              </Link>
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
                        <button
                          onClick={() => voteReview(review.id)}
                          disabled={votedReviews.has(review.id) || votingReview === review.id}
                          className={`flex items-center gap-1 transition-colors ${
                            votedReviews.has(review.id)
                              ? 'text-tertiary cursor-default'
                              : 'text-on-surface-variant hover:text-white'
                          } ${votingReview === review.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
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

      {/* Add to Playlist Modal */}
      {selectedSongForPlaylist && (
        <AddToPlaylistModal
          songId={selectedSongForPlaylist}
          isOpen={showPlaylistModal}
          onClose={() => {
            setShowPlaylistModal(false);
            setSelectedSongForPlaylist(null);
          }}
          onSuccess={() => {
            console.log('Added to playlist successfully');
          }}
        />
      )}
    </>
  );
}
