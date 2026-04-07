/**
 * Add to Playlist Modal - Reusable component for adding songs to playlists
 */

import { useState, useEffect } from 'react';
import { Icon } from './Icon';
import { playlistsAPI } from '../api/services';
import type { Playlist } from '../api/types';

interface AddToPlaylistModalProps {
  songId: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function AddToPlaylistModal({
  songId,
  isOpen,
  onClose,
  onSuccess,
}: AddToPlaylistModalProps) {
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState<number | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadPlaylists();
    }
  }, [isOpen]);

  async function loadPlaylists() {
    try {
      setLoading(true);
      setError('');
      const data = await playlistsAPI.listMy(1, 50);
      setPlaylists(data.items);
    } catch (err) {
      console.error('Failed to load playlists:', err);
      setError('Falha ao carregar playlists');
    } finally {
      setLoading(false);
    }
  }

  async function handleAddToPlaylist(playlistId: number) {
    try {
      setAdding(playlistId);
      setError('');
      console.log('Adding song', songId, 'to playlist', playlistId);
      const result = await playlistsAPI.addSong(playlistId, songId);
      console.log('Add to playlist result:', result);
      onSuccess?.();
      onClose();
    } catch (err: any) {
      console.error('Failed to add to playlist:', err);
      console.error('Error type:', typeof err);
      console.error('Error keys:', Object.keys(err));

      // Extract error message properly
      let errorMessage = 'Falha ao adicionar à playlist';

      if (err?.message) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err?.toString && err.toString() !== '[object Object]') {
        errorMessage = err.toString();
      }

      setError(errorMessage);
    } finally {
      setAdding(null);
    }
  }

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-surface-container rounded-3xl shadow-2xl max-w-md w-full max-h-[80vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-outline-variant/10">
          <h3 className="font-headline text-2xl font-bold text-white">
            Adicionar à Playlist
          </h3>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-full hover:bg-surface-bright flex items-center justify-center transition-colors"
          >
            <Icon name="close" size="sm" decorative />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[60vh]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Icon
                name="refresh"
                size="lg"
                className="animate-spin text-on-surface-variant"
                decorative
              />
            </div>
          ) : error ? (
            <div className="p-6 text-center">
              <Icon
                name="error"
                size="lg"
                className="text-error mx-auto mb-4"
                decorative
              />
              <p className="text-error">{error}</p>
            </div>
          ) : playlists.length === 0 ? (
            <div className="p-6 text-center">
              <Icon
                name="playlist_play"
                size="lg"
                className="text-on-surface-variant mx-auto mb-4"
                decorative
              />
              <p className="text-on-surface-variant mb-4">
                Você ainda não tem playlists
              </p>
              <button
                onClick={onClose}
                className="px-6 py-3 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed rounded-full font-bold hover:scale-105 transition-transform"
              >
                Criar Playlist
              </button>
            </div>
          ) : (
            <div className="p-2">
              {playlists.map((playlist) => (
                <button
                  key={playlist.id}
                  onClick={() => handleAddToPlaylist(playlist.id)}
                  disabled={adding === playlist.id}
                  className="w-full flex items-center justify-between p-4 rounded-xl hover:bg-white/5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-dim/30 to-secondary/30 flex items-center justify-center flex-shrink-0">
                      <Icon name="playlist_play" size="sm" decorative />
                    </div>
                    <div className="text-left">
                      <h4 className="font-bold text-white">{playlist.title}</h4>
                      <p className="text-xs text-on-surface-variant">
                        {playlist.songs_count}{' '}
                        {playlist.songs_count === 1 ? 'música' : 'músicas'}
                      </p>
                    </div>
                  </div>
                  {adding === playlist.id ? (
                    <Icon
                      name="refresh"
                      size="sm"
                      className="animate-spin text-on-surface-variant"
                      decorative
                    />
                  ) : (
                    <Icon
                      name="add"
                      size="sm"
                      className="text-primary"
                      decorative
                    />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
