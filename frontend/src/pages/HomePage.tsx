/**
 * Home Page - Landing page with featured content
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, Button, Icon, Layout } from '../components';
import { artistsAPI, albumsAPI, songsAPI } from '../api/services';
import type { Artist, Album, Song } from '../api/types';

export function HomePage() {
  const [featuredArtists, setFeaturedArtists] = useState<Artist[]>([]);
  const [featuredAlbums, setFeaturedAlbums] = useState<Album[]>([]);
  const [topSongs, setTopSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFeaturedContent();
  }, []);

  async function loadFeaturedContent() {
    try {
      const [artists, albums, songs] = await Promise.all([
        artistsAPI.list(1, 6),
        albumsAPI.list(1, 6),
        songsAPI.list(1, 10),
      ]);
      setFeaturedArtists(artists.items);
      setFeaturedAlbums(albums.items);
      setTopSongs(songs.items);
    } catch (error) {
      console.error('Failed to load content:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <Layout.Container>
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="text-center">
            <Icon name="refresh" size="lg" className="animate-spin mx-auto mb-4" />
            <p className="text-on-surface-variant">Loading...</p>
          </div>
        </div>
      </Layout.Container>
    );
  }

  return (
    <Layout.Container>
      {/* Hero Section */}
      <div className="pt-32 pb-16 text-center">
        <h1 className="font-headline text-6xl font-medium mb-6 text-gradient">
          The Sonic Immersive
        </h1>
        <p className="text-xl text-on-surface-variant mb-8 max-w-2xl mx-auto">
          Discover, share, and immerse yourself in the world's music
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link to="/search">
            <Button variant="primary" size="lg">
              <Icon name="search" size="sm" className="mr-2" />
              Search Music
            </Button>
          </Link>
          <Link to="/recommendations">
            <Button variant="secondary" size="lg">
              <Icon name="magic_button" size="sm" className="mr-2" />
              Get Recommendations
            </Button>
          </Link>
        </div>
      </div>

      {/* Featured Artists */}
      {featuredArtists.length > 0 && (
        <div className="mb-16">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-headline text-3xl">Featured Artists</h2>
            <Link to="/artists">
              <Button variant="ghost" size="sm">
                View All
                <Icon name="arrow_forward" size="sm" className="ml-2" />
              </Button>
            </Link>
          </div>
          <Layout.Grid cols={3} gap={6}>
            {featuredArtists.map((artist) => (
              <Link key={artist.id} to={`/artists/${artist.id}`}>
                <Card glass interactive>
                  <Card.Content>
                    <h3 className="font-headline text-xl mb-2">{artist.name}</h3>
                    <p className="text-on-surface-variant text-sm">
                      {artist.albums_count} {artist.albums_count === 1 ? 'album' : 'albums'}
                    </p>
                  </Card.Content>
                </Card>
              </Link>
            ))}
          </Layout.Grid>
        </div>
      )}

      {/* Featured Albums */}
      {featuredAlbums.length > 0 && (
        <div className="mb-16">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-headline text-3xl">Recent Albums</h2>
            <Link to="/albums">
              <Button variant="ghost" size="sm">
                View All
                <Icon name="arrow_forward" size="sm" className="ml-2" />
              </Button>
            </Link>
          </div>
          <Layout.Grid cols={3} gap={6}>
            {featuredAlbums.map((album) => (
              <Link key={album.id} to={`/albums/${album.id}`}>
                <Card glass interactive>
                  <Card.Content>
                    <h3 className="font-headline text-xl mb-1">{album.title}</h3>
                    <p className="text-on-surface-variant text-sm mb-2">
                      {album.artist_name}
                    </p>
                    {album.release_year && (
                      <p className="text-on-surface-variant text-xs">
                        {album.release_year}
                        {album.genre && ` · ${album.genre}`}
                      </p>
                    )}
                  </Card.Content>
                </Card>
              </Link>
            ))}
          </Layout.Grid>
        </div>
      )}

      {/* Top Songs */}
      {topSongs.length > 0 && (
        <div className="mb-16">
          <h2 className="font-headline text-3xl mb-6">Top Songs</h2>
          <Card glass>
            <Card.Content>
              <div className="space-y-3">
                {topSongs.map((song, index) => (
                  <Link
                    key={song.id}
                    to={`/songs/${song.id}`}
                    className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 transition-colors"
                  >
                    <span className="text-on-surface-variant w-8 text-right">
                      {index + 1}
                    </span>
                    <div className="flex-1">
                      <p className="font-medium">{song.title}</p>
                      <p className="text-sm text-on-surface-variant">
                        {song.artist_name} · {song.album_title}
                      </p>
                    </div>
                    {song.average_rating && (
                      <div className="flex items-center gap-1">
                        <Icon name="star" size="sm" />
                        <span className="text-sm">
                          {song.average_rating.toFixed(1)}
                        </span>
                      </div>
                    )}
                    <span className="text-sm text-on-surface-variant">
                      {Math.floor(song.duration_seconds / 60)}:
                      {(song.duration_seconds % 60).toString().padStart(2, '0')}
                    </span>
                  </Link>
                ))}
              </div>
            </Card.Content>
          </Card>
        </div>
      )}
    </Layout.Container>
  );
}
