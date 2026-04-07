/**
 * Library Page (Minha Biblioteca) - Following Stitch Mockup
 * Bento grid layout with featured liked songs + saved albums
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { useAuth } from '../context/AuthContext';
import { playlistsAPI, albumsAPI, favoritesAPI } from '../api/services';
import type { Playlist, Album } from '../api/types';

export function LibraryPage() {
  const { user } = useAuth();
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [albums, setAlbums] = useState<Album[]>([]);
  const [favoriteSongsCount, setFavoriteSongsCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadLibrary();
    } else {
      setLoading(false);
    }
  }, [user]);

  async function loadLibrary() {
    try {
      const [playlistsData, favoriteAlbumsData, favoriteSongsData] = await Promise.all([
        playlistsAPI.listMy(1, 10),
        favoritesAPI.listFavoriteAlbums(),
        favoritesAPI.listFavoriteSongs(),
      ]);
      setPlaylists(playlistsData.items);
      setAlbums(favoriteAlbumsData.items);
      setFavoriteSongsCount(favoriteSongsData.total);
    } catch (error) {
      console.error('Failed to load library:', error);
    } finally {
      setLoading(false);
    }
  }

  if (!user) {
    return (
      <>
        <TopBar />
        <div className="flex items-center justify-center min-h-screen px-8">
          <div className="text-center max-w-md">
            <Icon
              name="library_music"
              size="lg"
              className="mx-auto mb-6 text-on-surface-variant"
              decorative
            />
            <h1 className="font-headline text-4xl mb-4">Minha Biblioteca</h1>
            <p className="text-on-surface-variant mb-8">
              Faça login para acessar sua biblioteca pessoal
            </p>
            <Link to="/login">
              <button className="px-8 py-4 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed font-bold rounded-full hover:scale-105 transition-transform">
                Entrar / Cadastrar
              </button>
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
        {/* Page Hero */}
        <section className="px-8 py-10">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
            <div>
              <span className="text-secondary font-headline tracking-[0.2em] text-xs uppercase mb-2 block">
                Sua Coleção
              </span>
              <h2 className="text-5xl font-headline font-bold text-white tracking-tighter">
                Minha Biblioteca
              </h2>
            </div>
            <Link to="/playlists">
              <button className="flex items-center gap-2 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed px-8 py-4 rounded-full font-bold shadow-lg shadow-primary-dim/20 hover:scale-105 transition-transform duration-200 active:scale-95">
                <Icon name="add_circle" size="sm" decorative />
                Criar Nova Playlist
              </button>
            </Link>
          </div>
        </section>

        {/* Library Content Bento Grid */}
        <section className="px-8 grid grid-cols-1 md:grid-cols-4 lg:grid-cols-6 gap-6">
          {/* Featured: Liked Songs */}
          <Link
            to="/library/favorites"
            className="md:col-span-2 lg:col-span-2 aspect-square md:aspect-auto group relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#450074] to-[#a533ff] p-6 flex flex-col justify-end shadow-2xl transition-all hover:scale-[1.02] cursor-pointer"
          >
            <div className="absolute top-6 right-6">
              <div className="w-16 h-16 rounded-2xl bg-white/10 backdrop-blur-md flex items-center justify-center border border-white/20">
                <Icon
                  name="favorite"
                  size="lg"
                  className="text-white"
                  decorative
                />
              </div>
            </div>
            <div className="z-10">
              <h3 className="text-3xl font-headline font-bold text-white mb-1">
                Músicas Curtidas
              </h3>
              <p className="text-on-surface/70 font-medium">
                {favoriteSongsCount} {favoriteSongsCount === 1 ? 'faixa' : 'faixas'}
              </p>
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          </Link>

          {/* Bento: Saved Albums */}
          <div className="md:col-span-2 lg:col-span-4 grid grid-cols-2 md:grid-cols-3 gap-6">
            {loading ? (
              <div className="col-span-full flex items-center justify-center py-12">
                <Icon
                  name="refresh"
                  size="lg"
                  className="animate-spin text-on-surface-variant"
                  decorative
                />
              </div>
            ) : albums.length === 0 ? (
              <div className="col-span-full flex flex-col items-center justify-center py-16 px-6 text-center">
                <div className="w-24 h-24 rounded-3xl bg-surface-container-highest/40 backdrop-blur-sm flex items-center justify-center mb-6 border border-white/5">
                  <Icon
                    name="album"
                    size="xl"
                    className="text-on-surface-variant/40"
                    decorative
                  />
                </div>
                <h3 className="font-headline text-2xl font-bold text-white mb-2">
                  Sua biblioteca está vazia
                </h3>
                <p className="text-on-surface-variant mb-6 max-w-md">
                  Comece a explorar e salve seus álbuns favoritos para vê-los aqui
                </p>
                <Link to="/explore">
                  <button className="flex items-center gap-2 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed px-6 py-3 rounded-full font-bold hover:scale-105 transition-transform">
                    <Icon name="explore" size="sm" decorative />
                    Explorar Música
                  </button>
                </Link>
              </div>
            ) : (
              albums.slice(0, 6).map((album) => (
                <Link
                  key={album.id}
                  to={`/albums/${album.id}`}
                  className="group cursor-pointer"
                >
                  <div className="relative aspect-square overflow-hidden rounded-2xl bg-surface-container shadow-xl transition-transform duration-300 group-hover:scale-[1.03]">
                    {album.cover_art_url ? (
                      <img
                        src={album.cover_art_url}
                        alt={album.title}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
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
                  <div className="mt-3">
                    <h4 className="font-bold text-white truncate">
                      {album.title}
                    </h4>
                    <p className="text-sm text-on-surface-variant truncate">
                      {album.artist_name}
                    </p>
                  </div>
                </Link>
              ))
            )}
          </div>
        </section>

        {/* Playlists Section */}
        <section className="px-8 mt-12">
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-headline text-2xl font-bold text-white">
              Suas Playlists
            </h3>
            {playlists.length > 0 && (
              <Link
                to="/playlists"
                className="text-secondary font-bold hover:underline flex items-center gap-1"
              >
                Ver todas
                <Icon name="arrow_forward" size="sm" decorative />
              </Link>
            )}
          </div>

          {playlists.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 px-6 text-center bg-surface-container rounded-3xl">
              <div className="w-20 h-20 rounded-2xl bg-surface-container-highest/40 backdrop-blur-sm flex items-center justify-center mb-4 border border-white/5">
                <Icon
                  name="queue_music"
                  size="lg"
                  className="text-on-surface-variant/40"
                  decorative
                />
              </div>
              <h4 className="font-headline text-xl font-bold text-white mb-2">
                Nenhuma playlist criada
              </h4>
              <p className="text-on-surface-variant mb-6 max-w-sm">
                Crie sua primeira playlist e organize suas músicas favoritas
              </p>
              <Link to="/playlists">
                <button className="flex items-center gap-2 bg-surface-bright hover:bg-surface-container-highest text-white px-6 py-3 rounded-full font-bold hover:scale-105 transition-transform border border-white/10">
                  <Icon name="add" size="sm" decorative />
                  Criar Playlist
                </button>
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {playlists.slice(0, 5).map((playlist) => (
                <Link
                  key={playlist.id}
                  to={`/playlists/${playlist.id}`}
                  className="group bg-surface-container rounded-xl p-4 transition-all duration-300 hover:bg-surface-bright hover:scale-[1.02]"
                >
                  <div className="aspect-square rounded-lg bg-gradient-to-br from-primary-dim/20 to-secondary/20 flex items-center justify-center mb-3">
                    <Icon
                      name="queue_music"
                      size="lg"
                      className="text-primary"
                      decorative
                    />
                  </div>
                  <h4 className="font-bold text-white truncate">
                    {playlist.title}
                  </h4>
                  <p className="text-sm text-on-surface-variant">
                    {playlist.songs_count} músicas
                  </p>
                </Link>
              ))}
            </div>
          )}
        </section>
      </main>
    </>
  );
}
