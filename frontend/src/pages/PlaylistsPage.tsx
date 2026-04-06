/**
 * Playlists Page - User's playlists
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, Button, Icon, Layout, Input } from '../components';
import { useAuth } from '../context/AuthContext';
import { playlistsAPI } from '../api/services';
import type { Playlist } from '../api/types';

export function PlaylistsPage() {
  const { user } = useAuth();
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPlaylistTitle, setNewPlaylistTitle] = useState('');
  const [isPublic, setIsPublic] = useState(false);

  useEffect(() => {
    if (user) {
      loadPlaylists();
    } else {
      setLoading(false);
    }
  }, [user]);

  async function loadPlaylists() {
    try {
      const data = await playlistsAPI.listMy();
      setPlaylists(data.items);
    } catch (error) {
      console.error('Failed to load playlists:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreatePlaylist(e: React.FormEvent) {
    e.preventDefault();
    if (!newPlaylistTitle.trim()) return;

    setCreating(true);
    try {
      await playlistsAPI.create({
        title: newPlaylistTitle,
        is_public: isPublic,
      });
      setNewPlaylistTitle('');
      setIsPublic(false);
      setShowCreateForm(false);
      await loadPlaylists();
    } catch (error) {
      console.error('Failed to create playlist:', error);
    } finally {
      setCreating(false);
    }
  }

  function formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  if (!user) {
    return (
      <Layout.Container>
        <div className="pt-32 text-center">
          <Icon
            name="playlist_play"
            size="lg"
            className="mx-auto mb-4 text-on-surface-variant"
          />
          <h1 className="font-headline text-4xl mb-4">Your Playlists</h1>
          <p className="text-on-surface-variant mb-8">
            Sign in to create and manage your playlists
          </p>
          <Link to="/login">
            <Button variant="primary" size="lg">
              Sign In
            </Button>
          </Link>
        </div>
      </Layout.Container>
    );
  }

  if (loading) {
    return (
      <Layout.Container>
        <div className="flex items-center justify-center min-h-[50vh] pt-32">
          <div className="text-center">
            <Icon name="refresh" size="lg" className="animate-spin mx-auto mb-4" />
            <p className="text-on-surface-variant">Loading playlists...</p>
          </div>
        </div>
      </Layout.Container>
    );
  }

  return (
    <Layout.Container>
      <div className="pt-32 pb-16">
        <div className="flex justify-between items-center mb-8">
          <h1 className="font-headline text-4xl">My Playlists</h1>
          <Button
            variant="primary"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            <Icon name="add" size="sm" className="mr-2" />
            Create Playlist
          </Button>
        </div>

        {/* Create Playlist Form */}
        {showCreateForm && (
          <Card glass className="mb-8">
            <Card.Header>
              <h3 className="font-headline text-xl">New Playlist</h3>
            </Card.Header>
            <Card.Content>
              <form onSubmit={handleCreatePlaylist} className="space-y-4">
                <Input
                  label="Playlist Title"
                  placeholder="My Awesome Playlist"
                  value={newPlaylistTitle}
                  onChange={(e) => setNewPlaylistTitle(e.target.value)}
                  required
                />

                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isPublic}
                    onChange={(e) => setIsPublic(e.target.checked)}
                    className="w-5 h-5 rounded accent-primary"
                  />
                  <span className="text-sm">Make playlist public</span>
                </label>

                <div className="flex gap-3">
                  <Button
                    type="submit"
                    variant="primary"
                    loading={creating}
                  >
                    Create
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setShowCreateForm(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </Card.Content>
          </Card>
        )}

        {/* Playlists List */}
        {playlists.length === 0 ? (
          <div className="text-center py-12">
            <Icon
              name="playlist_play"
              size="lg"
              className="mx-auto mb-4 text-on-surface-variant"
            />
            <p className="text-on-surface-variant mb-4">
              You don't have any playlists yet
            </p>
            <Button
              variant="secondary"
              onClick={() => setShowCreateForm(true)}
            >
              Create Your First Playlist
            </Button>
          </div>
        ) : (
          <Layout.Grid cols={3} gap={6}>
            {playlists.map((playlist) => (
              <Link key={playlist.id} to={`/playlists/${playlist.id}`}>
                <Card glass interactive>
                  <Card.Content>
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="font-headline text-xl">{playlist.title}</h3>
                      {!playlist.is_public && (
                        <Icon
                          name="lock"
                          size="sm"
                          className="text-on-surface-variant"
                        />
                      )}
                    </div>
                    <div className="space-y-1 text-sm text-on-surface-variant">
                      <p>
                        {playlist.songs_count}{' '}
                        {playlist.songs_count === 1 ? 'song' : 'songs'}
                      </p>
                      {playlist.total_duration_seconds > 0 && (
                        <p>{formatDuration(playlist.total_duration_seconds)}</p>
                      )}
                      <p className="text-xs">
                        {new Date(playlist.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                  </Card.Content>
                </Card>
              </Link>
            ))}
          </Layout.Grid>
        )}
      </div>
    </Layout.Container>
  );
}
