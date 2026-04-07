/**
 * Artist Profile Page - Following Stitch Mockup
 * Hero section with artist info + popular songs + discography
 */

import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate, useSearchParams } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { useAuth } from '../context/AuthContext';
import { artistsAPI, albumsAPI, songsAPI, favoritesAPI } from '../api/services';
import type { Artist, Album, Song } from '../api/types';

export function ArtistProfilePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [artist, setArtist] = useState<Artist | null>(null);
  const [albums, setAlbums] = useState<Album[]>([]);
  const [topSongs, setTopSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const [songFavorites, setSongFavorites] = useState<Record<number, boolean>>({});

  useEffect(() => {
    if (id) {
      loadArtistData();
    }
  }, [id]);

  async function loadArtistData() {
    try {
      const [artistData, albumsData, songsData] = await Promise.all([
        artistsAPI.get(Number(id)),
        albumsAPI.list(1, 8, Number(id)),
        songsAPI.list(1, 5, undefined, Number(id)),
      ]);
      setArtist(artistData);
      setAlbums(albumsData.items);
      setTopSongs(songsData.items);

      // Load favorite status for songs
      await loadSongFavorites(songsData.items.map(s => s.id));
    } catch (error) {
      console.error('Failed to load artist:', error);
    } finally {
      setLoading(false);
    }
  }

  async function loadSongFavorites(songIds: number[]) {
    if (!user) {
      const favorites: Record<number, boolean> = {};
      songIds.forEach(songId => favorites[songId] = false);
      setSongFavorites(favorites);
      return;
    }

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

    if (!user) {
      navigate('/login');
      return;
    }

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

  if (!artist) {
    return (
      <>
        <TopBar />
        <div className="flex items-center justify-center min-h-screen px-8">
          <div className="text-center">
            <h1 className="font-headline text-4xl mb-4">Artista não encontrado</h1>
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
        {/* Hero Section */}
        <section className="relative h-[614px] flex flex-col justify-end p-8 md:p-12 overflow-hidden">
          {/* Background with gradients */}
          <div className="absolute inset-0 z-0">
            <div className="w-full h-full bg-gradient-to-br from-primary-dim/40 to-secondary/20 scale-105" />
            <div className="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-transparent" />
          </div>

          {/* Artist Content */}
          <div className="relative z-10 flex flex-col md:flex-row items-end gap-8">
            {/* Artist Image */}
            <div className="w-48 h-48 md:w-64 md:h-64 rounded-2xl overflow-hidden shadow-2xl border-4 border-surface-container-high/50 transform -rotate-2">
              {artist.photo_url ? (
                <img
                  src={artist.photo_url}
                  alt={artist.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-surface-bright">
                  <Icon
                    name="person"
                    size="lg"
                    className="text-on-surface-variant"
                    decorative
                  />
                </div>
              )}
            </div>

            {/* Artist Info */}
            <div className="flex-1 space-y-4">
              <div className="flex items-center gap-2 text-secondary font-headline font-bold uppercase tracking-widest text-sm">
                <Icon
                  name="verified"
                  size="sm"
                  className="text-secondary"
                  decorative
                />
                Artista Verificado
              </div>
              <h1 className="text-6xl md:text-8xl font-headline font-extrabold tracking-tighter leading-none text-white">
                {artist.name.toUpperCase()}
              </h1>
              {artist.bio && (
                <p className="max-w-xl text-on-surface-variant font-medium text-lg leading-relaxed">
                  {artist.bio}
                </p>
              )}
              <div className="flex flex-wrap gap-4 pt-4">
                <button className="px-8 py-4 rounded-full bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed font-black uppercase tracking-tighter flex items-center gap-2 hover:scale-105 transition-transform">
                  <Icon name="play_arrow" size="md" decorative />
                  Play All
                </button>
                <button className="px-8 py-4 rounded-full border border-outline/20 backdrop-blur-md bg-white/5 text-white font-bold hover:bg-white/10 transition-colors">
                  Seguir
                </button>
                <button className="p-4 rounded-full border border-outline/20 backdrop-blur-md bg-white/5 text-white hover:text-secondary transition-colors">
                  <Icon name="more_horiz" size="md" decorative />
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Content Grid */}
        <div className="p-8 md:p-12 grid grid-cols-1 xl:grid-cols-3 gap-12">
          {/* Popular Songs */}
          <div className="xl:col-span-2 space-y-8">
            <div className="flex justify-between items-end">
              <h2 className="text-3xl font-headline font-bold tracking-tight">
                Músicas Mais Populares
              </h2>
              <Link
                to={`/search?q=${encodeURIComponent(artist?.name || '')}`}
                className="text-secondary text-sm font-bold hover:underline"
              >
                Ver todas
              </Link>
            </div>

            <div className="space-y-1">
              {topSongs.map((song, index) => (
                <Link
                  key={song.id}
                  to={`/songs/${song.id}`}
                  className="group flex items-center gap-6 p-4 rounded-xl hover:bg-surface-container transition-all cursor-pointer"
                >
                  <span className="w-4 text-on-surface-variant font-headline font-bold group-hover:hidden">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  <span className="w-4 text-secondary hidden group-hover:block">
                    <Icon name="play_arrow" size="sm" decorative />
                  </span>

                  <div className="w-12 h-12 rounded-lg bg-surface-container-highest overflow-hidden flex-shrink-0">
                    {song.cover_art_url ? (
                      <img
                        src={song.cover_art_url}
                        alt={song.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-surface-bright">
                        <Icon
                          name="music_note"
                          size="sm"
                          className="text-on-surface-variant/30"
                          decorative
                        />
                      </div>
                    )}
                  </div>

                  <div className="flex-1">
                    <h4 className="font-bold text-white group-hover:text-secondary transition-colors">
                      {song.title}
                    </h4>
                    <p className="text-xs text-on-surface-variant">
                      {song.album_title}
                    </p>
                  </div>

                  {song.average_rating && (
                    <div className="flex items-center gap-1 text-tertiary">
                      <Icon name="star" size="sm" decorative />
                      <span className="text-sm font-bold">
                        {song.average_rating.toFixed(1)}
                      </span>
                    </div>
                  )}

                  <button
                    onClick={(e) => toggleSongFavorite(song.id, e)}
                    className={`transition-all ${
                      songFavorites[song.id] ? 'text-tertiary' : 'text-on-surface-variant hover:text-white'
                    }`}
                  >
                    <Icon name={songFavorites[song.id] ? 'favorite' : 'favorite_border'} size="sm" decorative />
                  </button>
                </Link>
              ))}
            </div>

            {/* Discography Section */}
            <div className="pt-8 space-y-8">
              <div className="flex justify-between items-end">
                <h2 className="text-3xl font-headline font-bold tracking-tight">
                  Discografia
                </h2>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
                {albums.map((album) => (
                  <Link
                    key={album.id}
                    to={`/albums/${album.id}`}
                    className="group"
                  >
                    <div className="relative aspect-square rounded-xl overflow-hidden bg-surface-container mb-3 shadow-lg transition-transform duration-300 hover:scale-[1.03]">
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
                            className="text-on-surface-variant/30"
                            decorative
                          />
                        </div>
                      )}
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center text-on-primary-fixed shadow-lg scale-90 group-hover:scale-100 transition-transform">
                          <Icon name="play_arrow" size="md" decorative />
                        </div>
                      </div>
                    </div>
                    <h4 className="font-bold text-white truncate">
                      {album.title}
                    </h4>
                    <p className="text-sm text-on-surface-variant">
                      {album.release_year || 'Ano desconhecido'}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar: About */}
          <div className="space-y-8">
            <div className="glass-card rounded-2xl p-6 space-y-4">
              <h3 className="font-headline text-xl font-bold">Sobre</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-3">
                  <Icon
                    name="album"
                    size="sm"
                    className="text-secondary"
                    decorative
                  />
                  <span className="text-on-surface-variant">
                    {artist.albums_count} álbuns
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <Icon
                    name="calendar_today"
                    size="sm"
                    className="text-secondary"
                    decorative
                  />
                  <span className="text-on-surface-variant">
                    Desde {new Date(artist.created_at).getFullYear()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
