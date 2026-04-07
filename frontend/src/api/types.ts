/**
 * TypeScript types for API responses
 */

// Auth
export interface User {
  id: number;
  email: string;
  username?: string;
  role: 'USER' | 'ADMIN';
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
}

export interface LogoutResponse {
  message: string;
}

// Artists
export interface Artist {
  id: number;
  name: string;
  bio?: string;
  photo_url?: string;
  albums_count: number;
  created_at: string;
  updated_at: string;
}

export interface ArtistListResponse {
  items: Artist[];
  total: number;
  page: number;
  page_size: number;
}

// Albums
export interface Album {
  id: number;
  title: string;
  artist_id: number;
  artist_name: string;
  release_year?: number;
  genre?: string;
  cover_art_url?: string;
  created_at: string;
  updated_at: string;
}

export interface AlbumListResponse {
  items: Album[];
  total: number;
  page: number;
  page_size: number;
}

// Songs
export interface Song {
  id: number;
  title: string;
  album_id: number;
  album_title: string;
  artist_id?: number;
  artist_name: string;
  duration_seconds: number;
  genre?: string;
  year?: number;
  cover_art_url?: string;
  average_rating?: number;
  review_count: number;
  created_at: string;
  updated_at: string;
}

export interface SongListResponse {
  items: Song[];
  total: number;
  page: number;
  page_size: number;
}

// Playlists
export interface Playlist {
  id: number;
  title: string;
  owner_user_id: number;
  is_public: boolean;
  songs_count: number;
  total_duration_seconds: number;
  created_at: string;
  updated_at: string;
  songs?: PlaylistSong[];
}

export interface PlaylistSong {
  playlist_song_id: number;
  position: number;
  song_id: number;
  song_title: string;
  artist_name: string;
  album_id: number;
  album_title: string;
  duration_seconds: number;
  cover_art_url?: string;
}

export interface PlaylistListResponse {
  items: Playlist[];
  total: number;
  page: number;
  page_size: number;
}

export interface PlaylistCreateRequest {
  title: string;
  is_public?: boolean;
}

// Reviews
export interface Review {
  id: string;
  user_id: number;
  username: string;
  song_id: number;
  rating: number;
  body?: string;
  is_flagged: boolean;
  helpful_count: number;
  created_at: string;
  updated_at: string;
}

export interface ReviewListResponse {
  items: Review[];
  total: number;
  page: number;
  page_size: number;
}

export interface ReviewCreateRequest {
  song_id: number;
  rating: number;
  body?: string;
}

// Search
export interface SearchResponse {
  artists: ArtistResult[];
  albums: AlbumResult[];
  songs: SongResult[];
  total_count: number;
}

export interface ArtistResult {
  id: number;
  name: string;
  photo_url?: string | null;
  relevance_score: number;
  albums_count: number;
}

export interface AlbumResult {
  id: number;
  title: string;
  artist_id: number;
  artist_name: string;
  release_year?: number;
  genre?: string;
  cover_art_url?: string;
  relevance_score: number;
}

export interface SongResult {
  id: number;
  title: string;
  artist_name: string;
  album_title: string;
  genre?: string;
  cover_art_url?: string;
  average_rating?: number | string | null;
  review_count: number;
  relevance_score: number;
}

// Recommendations
export interface RecommendationResponse {
  recommendations: RecommendedSong[];
  total_count: number;
}

export interface RecommendedSong {
  song_id: number;
  title: string;
  artist_name: string;
  album_title: string;
  genre?: string;
  cover_art_url?: string;
  average_rating?: number;
  score: number;
  reason: string;
}

// Favorites
export interface FavoriteSong {
  song_id: number;
  title: string;
  artist_name: string;
  album_title: string;
  album_id: number;
  duration_seconds: number;
  genre?: string;
  cover_art_url?: string;
  average_rating?: number;
  review_count?: number;
}
