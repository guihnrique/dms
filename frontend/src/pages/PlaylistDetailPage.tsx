/**
 * Playlist Detail Page - Individual playlist with songs
 */

import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { ConfirmModal } from '../components/ConfirmModal';
import { useAuth } from '../context/AuthContext';
import { playlistsAPI } from '../api/services';
import type { Playlist } from '../api/types';

export function PlaylistDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [playlist, setPlaylist] = useState<Playlist | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editIsPublic, setEditIsPublic] = useState(false);
  const [editing, setEditing] = useState(false);
  const [songToRemove, setSongToRemove] = useState<{ id: number; title: string } | null>(null);
  const [removingSong, setRemovingSong] = useState(false);

  useEffect(() => {
    if (id) {
      loadPlaylist();
    }
  }, [id]);

  async function loadPlaylist() {
    try {
      setLoading(true);
      const data = await playlistsAPI.get(Number(id));
      setPlaylist(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load playlist');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete() {
    if (!id) return;

    try {
      setDeleting(true);
      await playlistsAPI.delete(Number(id));
      navigate('/playlists');
    } catch (err) {
      console.error('Failed to delete playlist:', err);
      alert('Falha ao excluir playlist');
      setDeleting(false);
      setShowDeleteModal(false);
    }
  }

  async function handleEdit(e: React.FormEvent) {
    e.preventDefault();
    if (!id || !editTitle.trim()) return;

    try {
      setEditing(true);
      const updated = await playlistsAPI.update(Number(id), {
        title: editTitle,
        is_public: editIsPublic,
      });
      setPlaylist(updated);
      setShowEditModal(false);
    } catch (err) {
      console.error('Failed to update playlist:', err);
      alert('Falha ao atualizar playlist');
    } finally {
      setEditing(false);
    }
  }

  async function handleRemoveSong() {
    if (!id || !songToRemove) return;

    try {
      setRemovingSong(true);
      await playlistsAPI.removeSong(Number(id), songToRemove.id);
      await loadPlaylist();
      setSongToRemove(null);
    } catch (err) {
      console.error('Failed to remove song:', err);
      alert('Falha ao remover música');
    } finally {
      setRemovingSong(false);
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

  if (error || !playlist) {
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
            Playlist não encontrada
          </h2>
          <p className="text-on-surface-variant mb-6">{error}</p>
          <Link to="/playlists">
            <button className="px-6 py-3 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed rounded-full font-bold hover:scale-105 transition-transform">
              Ver Minhas Playlists
            </button>
          </Link>
        </div>
      </>
    );
  }

  const isOwner = user && playlist.owner_user_id === user.id;

  return (
    <>
      <TopBar />

      <main className="pb-32">
        {/* Hero Section */}
        <section className="relative px-8 pt-12 pb-20">
          <div className="absolute inset-0 bg-gradient-to-b from-primary-dim/20 via-background to-background" />

          <div className="relative max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row gap-8 items-start">
              {/* Playlist Cover */}
              <div className="w-full md:w-80 flex-shrink-0">
                <div className="aspect-square rounded-3xl bg-gradient-to-br from-primary-dim/30 to-secondary/30 overflow-hidden shadow-2xl flex items-center justify-center">
                  <Icon
                    name="playlist_play"
                    size="xl"
                    className="text-primary"
                    decorative
                  />
                </div>
              </div>

              {/* Playlist Info */}
              <div className="flex-1 min-w-0">
                <div className="mb-4">
                  <span className="inline-block px-4 py-1 rounded-full bg-tertiary-container/20 text-tertiary text-xs font-bold tracking-wider uppercase mb-4">
                    Playlist {playlist.is_public ? '• Pública' : '• Privada'}
                  </span>
                </div>

                <h1 className="font-headline text-6xl md:text-7xl font-extrabold text-white tracking-tighter mb-6 leading-none">
                  {playlist.title}
                </h1>

                {/* Stats */}
                <div className="flex flex-wrap items-center gap-6 mb-8">
                  <div className="flex items-center gap-2">
                    <Icon name="music_note" size="sm" className="text-on-surface-variant" decorative />
                    <span className="text-on-surface-variant">
                      {playlist.songs_count} {playlist.songs_count === 1 ? 'música' : 'músicas'}
                    </span>
                  </div>

                  {playlist.total_duration_seconds > 0 && (
                    <div className="flex items-center gap-2">
                      <Icon name="schedule" size="sm" className="text-on-surface-variant" decorative />
                      <span className="text-on-surface-variant">
                        {Math.floor(playlist.total_duration_seconds / 60)} min
                      </span>
                    </div>
                  )}

                  <div className="px-3 py-1 rounded-full bg-surface-container">
                    <span className="text-on-surface text-sm">
                      Atualizada em {new Date(playlist.updated_at).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-4">
                  <button className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed rounded-full font-bold hover:scale-105 transition-transform shadow-lg shadow-primary/20">
                    <Icon name="play_arrow" size="md" decorative />
                    Reproduzir
                  </button>

                  {isOwner && (
                    <>
                      <button
                        onClick={() => {
                          setEditTitle(playlist.title);
                          setEditIsPublic(playlist.is_public);
                          setShowEditModal(true);
                        }}
                        className="flex items-center gap-2 px-6 py-4 bg-surface-container hover:bg-surface-bright rounded-full font-bold transition-colors"
                      >
                        <Icon name="edit" size="sm" decorative />
                        Editar
                      </button>

                      <button
                        onClick={() => setShowDeleteModal(true)}
                        className="flex items-center gap-2 px-6 py-4 bg-error-container hover:bg-error-container/80 text-error rounded-full font-bold transition-colors"
                      >
                        <Icon name="delete" size="sm" decorative />
                        Excluir
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Songs List */}
        <section className="px-8 max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-headline text-3xl font-bold text-white">
              Músicas
            </h2>
          </div>

          {!playlist.songs || playlist.songs.length === 0 ? (
            <div className="text-center py-20 bg-surface-container rounded-2xl">
              <div className="w-16 h-16 rounded-2xl bg-surface-container-highest/40 mx-auto mb-4 flex items-center justify-center">
                <Icon
                  name="music_note"
                  size="lg"
                  className="text-on-surface-variant/40"
                  decorative
                />
              </div>
              <h3 className="font-headline text-xl font-bold text-white mb-2">
                Nenhuma música ainda
              </h3>
              <p className="text-on-surface-variant mb-6">
                Adicione músicas para começar a construir sua playlist
              </p>
              <Link to="/explore">
                <button className="px-6 py-3 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed rounded-full font-bold hover:scale-105 transition-transform">
                  Explorar Música
                </button>
              </Link>
            </div>
          ) : (
            <div className="space-y-1">
              {playlist.songs.map((song, index) => (
                <div
                  key={song.playlist_song_id}
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

                  {/* Album Cover Thumbnail */}
                  <Link to={`/songs/${song.song_id}`} className="flex-shrink-0">
                    {song.cover_art_url ? (
                      <img
                        src={song.cover_art_url}
                        alt={song.song_title}
                        className="w-12 h-12 rounded-lg object-cover"
                      />
                    ) : (
                      <div className="w-12 h-12 rounded-lg bg-surface-container flex items-center justify-center">
                        <Icon name="music_note" size="sm" className="text-on-surface-variant" decorative />
                      </div>
                    )}
                  </Link>

                  <Link to={`/songs/${song.song_id}`} className="flex-1">
                    <h4 className="text-white font-bold hover:underline">{song.song_title}</h4>
                    <p className="text-xs text-on-surface-variant">
                      {song.artist_name}
                    </p>
                  </Link>

                  {song.album_title && (
                    <Link
                      to={`/albums/${song.album_id}`}
                      className="hidden md:block text-sm text-on-surface-variant hover:underline"
                    >
                      {song.album_title}
                    </Link>
                  )}

                  <div className="hidden md:flex items-center gap-8 text-on-surface-variant text-sm">
                    {isOwner && (
                      <button
                        onClick={() => setSongToRemove({ id: song.playlist_song_id, title: song.song_title })}
                        className="opacity-0 group-hover:opacity-100 hover:text-error transition-all"
                      >
                        <Icon name="close" size="sm" decorative />
                      </button>
                    )}
                    <span className="font-mono">{formatDuration(song.duration_seconds)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDelete}
        title="Excluir Playlist"
        message={`Tem certeza que deseja excluir a playlist "${playlist?.title}"? Esta ação não pode ser desfeita.`}
        confirmText="Excluir"
        cancelText="Cancelar"
        confirmButtonClass="bg-error text-on-error"
        loading={deleting}
      />

      {/* Edit Modal */}
      {showEditModal && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setShowEditModal(false)}
        >
          <div
            className="bg-surface-container rounded-3xl shadow-2xl max-w-md w-full overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-outline-variant/10">
              <h3 className="font-headline text-2xl font-bold text-white">
                Editar Playlist
              </h3>
              <button
                onClick={() => setShowEditModal(false)}
                className="w-10 h-10 rounded-full hover:bg-surface-bright flex items-center justify-center transition-colors"
              >
                <Icon name="close" size="sm" decorative />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleEdit} className="p-6">
              <div className="space-y-4">
                <div>
                  <label htmlFor="title" className="block text-sm font-bold text-white mb-2">
                    Título
                  </label>
                  <input
                    id="title"
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    required
                    className="w-full px-4 py-3 rounded-xl bg-surface-bright text-white border border-outline-variant/20 focus:border-primary focus:outline-none transition-colors"
                    placeholder="Nome da playlist"
                  />
                </div>

                <div>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={editIsPublic}
                      onChange={(e) => setEditIsPublic(e.target.checked)}
                      className="w-5 h-5 rounded accent-primary"
                    />
                    <span className="text-sm text-on-surface">Playlist pública</span>
                  </label>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  disabled={editing}
                  className="flex-1 px-6 py-3 rounded-full bg-surface-bright hover:bg-surface-container-highest text-white font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={editing || !editTitle.trim()}
                  className="flex-1 px-6 py-3 rounded-full bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed font-bold hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {editing ? (
                    <div className="flex items-center justify-center gap-2">
                      <Icon
                        name="refresh"
                        size="sm"
                        className="animate-spin"
                        decorative
                      />
                      Salvando...
                    </div>
                  ) : (
                    'Salvar'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Remove Song Confirmation Modal */}
      {songToRemove && (
        <ConfirmModal
          isOpen={!!songToRemove}
          onClose={() => setSongToRemove(null)}
          onConfirm={handleRemoveSong}
          title="Remover Música"
          message={`Tem certeza que deseja remover "${songToRemove.title}" desta playlist?`}
          confirmText="Remover"
          cancelText="Cancelar"
          confirmButtonClass="bg-error text-on-error"
          loading={removingSong}
        />
      )}
    </>
  );
}
