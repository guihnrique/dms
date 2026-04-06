/**
 * Explore Page - Following Stitch Mockup Design
 * Hero section + genre filters + recommended albums grid
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TopBar } from '../components/TopBar';
import { Icon } from '../components/Icon';
import { albumsAPI, artistsAPI } from '../api/services';
import type { Album } from '../api/types';

const GENRES = [
  'Para Você',
  'Eletrônica',
  'Lo-Fi Jazz',
  'Rock Alternativo',
  'Techno',
  'Deep House',
  'Chillwave',
];

export function ExplorePage() {
  const [albums, setAlbums] = useState<Album[]>([]);
  const [selectedGenre, setSelectedGenre] = useState('Para Você');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadContent();
  }, []);

  async function loadContent() {
    try {
      const data = await albumsAPI.list(1, 10);
      setAlbums(data.items);
    } catch (error) {
      console.error('Failed to load content:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <TopBar />

      <main className="pb-32">
        {/* Hero Section */}
        <section className="px-8 pt-6">
          <div className="relative h-[480px] rounded-[2rem] overflow-hidden group">
            {/* Background Image with Gradient Overlays */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary-dim/40 to-secondary/20 transition-transform duration-700 group-hover:scale-105" />
            <div className="absolute inset-0 bg-gradient-to-t from-background via-background/40 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-r from-background/80 via-transparent to-transparent" />

            {/* Hero Content */}
            <div className="relative h-full flex flex-col justify-end p-12 max-w-3xl">
              <span className="inline-block px-4 py-1 rounded-full bg-tertiary-container text-white text-xs font-bold tracking-widest uppercase mb-4 w-fit">
                Novo Lançamento
              </span>
              <h2 className="font-headline text-6xl md:text-7xl font-extrabold text-white mb-4 leading-none tracking-tighter">
                CYBER PULSE <br />
                <span className="text-secondary">VOL. IV</span>
              </h2>
              <p className="font-body text-xl text-on-surface-variant mb-8 max-w-xl">
                Mergulhe na nova dimensão do Synthwave. Uma experiência sonora
                imersiva em 360° que redefine os limites do áudio digital.
              </p>
              <div className="flex items-center gap-4">
                <button className="px-8 py-4 bg-gradient-to-r from-primary-dim to-secondary text-on-primary-fixed font-black rounded-full flex items-center gap-3 hover:shadow-[0_0_30px_rgba(165,51,255,0.4)] transition-all">
                  <Icon name="play_arrow" size="md" decorative />
                  OUVIR AGORA
                </button>
                <button className="px-8 py-4 border border-white/20 backdrop-blur-md bg-white/5 text-white font-bold rounded-full hover:bg-white/10 transition-all">
                  SALVAR NA BIBLIOTECA
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Genre Filters */}
        <section className="px-8 py-10 flex gap-4 overflow-x-auto no-scrollbar">
          {GENRES.map((genre) => (
            <button
              key={genre}
              onClick={() => setSelectedGenre(genre)}
              className={`px-6 py-2 rounded-full font-bold whitespace-nowrap transition-all ${
                selectedGenre === genre
                  ? 'bg-primary-dim text-on-primary-fixed'
                  : 'bg-surface-container hover:bg-surface-bright text-on-surface-variant hover:text-white'
              }`}
            >
              {genre}
            </button>
          ))}
        </section>

        {/* Recommended Albums */}
        <section className="px-8 mb-12">
          <div className="flex justify-between items-end mb-8">
            <div>
              <h3 className="font-headline text-3xl font-bold text-white tracking-tight">
                Álbuns Recomendados
              </h3>
              <p className="text-on-surface-variant">
                Baseado no seu gosto recente
              </p>
            </div>
            <Link
              to="/albums"
              className="text-secondary font-bold hover:underline flex items-center gap-1"
            >
              Ver tudo{' '}
              <Icon name="arrow_forward" size="sm" decorative />
            </Link>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Icon
                name="refresh"
                size="lg"
                className="animate-spin text-on-surface-variant"
                decorative
              />
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {albums.map((album) => (
                <Link
                  key={album.id}
                  to={`/albums/${album.id}`}
                  className="group bg-surface-container rounded-xl p-4 transition-all duration-300 hover:bg-surface-bright hover:scale-[1.02] cursor-pointer"
                >
                  <div className="relative aspect-square rounded-lg overflow-hidden mb-4 bg-surface-bright">
                    {album.cover_art_url ? (
                      <img
                        src={album.cover_art_url}
                        alt={album.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
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
                  <p className="text-sm text-on-surface-variant truncate">
                    {album.artist_name}
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
