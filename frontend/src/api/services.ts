/**
 * API Services - Typed methods for all backend endpoints
 */

import { apiClient } from './client';
import type {
  AuthResponse,
  LogoutResponse,
  LoginRequest,
  RegisterRequest,
  User,
  ArtistListResponse,
  Artist,
  AlbumListResponse,
  Album,
  SongListResponse,
  Song,
  PlaylistListResponse,
  Playlist,
  PlaylistCreateRequest,
  ReviewListResponse,
  ReviewCreateRequest,
  SearchResponse,
  RecommendationResponse,
} from './types';

// Auth API
export const authAPI = {
  async register(data: RegisterRequest): Promise<User> {
    return apiClient.post('/api/v1/auth/register', data);
  },

  async login(data: LoginRequest): Promise<AuthResponse> {
    return apiClient.post('/api/v1/auth/login', data);
  },

  async logout(): Promise<LogoutResponse> {
    return apiClient.post('/api/v1/auth/logout');
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get('/api/v1/auth/me', { requiresAuth: true });
  },
};

// Artists API
export const artistsAPI = {
  async list(page = 1, pageSize = 20): Promise<ArtistListResponse> {
    return apiClient.get(`/api/v1/artists?page=${page}&page_size=${pageSize}`);
  },

  async get(id: number): Promise<Artist> {
    return apiClient.get(`/api/v1/artists/${id}`);
  },
};

// Albums API
export const albumsAPI = {
  async list(
    page = 1,
    pageSize = 20,
    artistId?: number
  ): Promise<AlbumListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (artistId) params.append('artist_id', artistId.toString());
    return apiClient.get(`/api/v1/albums?${params}`);
  },

  async get(id: number): Promise<Album> {
    return apiClient.get(`/api/v1/albums/${id}`);
  },
};

// Songs API
export const songsAPI = {
  async list(
    page = 1,
    pageSize = 20,
    albumId?: number
  ): Promise<SongListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (albumId) params.append('album_id', albumId.toString());
    return apiClient.get(`/api/v1/songs?${params}`);
  },

  async get(id: number): Promise<Song> {
    return apiClient.get(`/api/v1/songs/${id}`);
  },
};

// Playlists API
export const playlistsAPI = {
  async listMy(page = 1, pageSize = 20): Promise<PlaylistListResponse> {
    return apiClient.get(`/playlists/me?page=${page}&page_size=${pageSize}`, {
      requiresAuth: true,
    });
  },

  async listPublic(page = 1, pageSize = 20): Promise<PlaylistListResponse> {
    return apiClient.get(`/playlists/public?page=${page}&page_size=${pageSize}`);
  },

  async get(id: number): Promise<Playlist> {
    return apiClient.get(`/playlists/${id}`);
  },

  async create(data: PlaylistCreateRequest): Promise<Playlist> {
    return apiClient.post('/playlists', data, { requiresAuth: true });
  },

  async update(
    id: number,
    data: Partial<PlaylistCreateRequest>
  ): Promise<Playlist> {
    return apiClient.put(`/playlists/${id}`, data, { requiresAuth: true });
  },

  async delete(id: number): Promise<void> {
    return apiClient.delete(`/playlists/${id}`, { requiresAuth: true });
  },

  async addSong(playlistId: number, songId: number): Promise<Playlist> {
    return apiClient.post(`/playlists/${playlistId}/songs`, { song_id: songId }, {
      requiresAuth: true,
    });
  },

  async removeSong(
    playlistId: number,
    playlistSongId: number
  ): Promise<{ message: string }> {
    return apiClient.delete(
      `/playlists/${playlistId}/songs/${playlistSongId}`,
      { requiresAuth: true }
    );
  },
};

// Reviews API
export const reviewsAPI = {
  async listForSong(
    songId: number,
    page = 1,
    pageSize = 10
  ): Promise<ReviewListResponse> {
    return apiClient.get(
      `/reviews/songs/${songId}/reviews?page=${page}&page_size=${pageSize}`
    );
  },

  async listMy(page = 1, pageSize = 10): Promise<ReviewListResponse> {
    return apiClient.get(`/reviews/me?page=${page}&page_size=${pageSize}`, {
      requiresAuth: true,
    });
  },

  async create(data: ReviewCreateRequest): Promise<{ message: string }> {
    return apiClient.post('/reviews', data, { requiresAuth: true });
  },

  async vote(
    reviewId: string,
    voteType: 'helpful' | 'not_helpful'
  ): Promise<{ message: string }> {
    return apiClient.post(
      `/reviews/${reviewId}/vote`,
      { vote_type: voteType },
      { requiresAuth: true }
    );
  },

  async checkVotes(reviewIds: string[]): Promise<Record<string, string>> {
    return apiClient.post(
      '/reviews/votes/check',
      reviewIds,
      { requiresAuth: true }
    );
  },
};

// Search API
export const searchAPI = {
  async search(
    query: string,
    options?: {
      genres?: string[];
      yearMin?: number;
      yearMax?: number;
      sortBy?: string;
      sortOrder?: string;
    }
  ): Promise<SearchResponse> {
    const params = new URLSearchParams({ q: query });
    if (options?.genres) {
      options.genres.forEach((g) => params.append('genres', g));
    }
    if (options?.yearMin) params.append('year_min', options.yearMin.toString());
    if (options?.yearMax) params.append('year_max', options.yearMax.toString());
    if (options?.sortBy) params.append('sort_by', options.sortBy);
    if (options?.sortOrder) params.append('sort_order', options.sortOrder);

    return apiClient.get(`/search?${params}`);
  },
};

// Recommendations API
export const recommendationsAPI = {
  async get(limit = 20): Promise<RecommendationResponse> {
    return apiClient.get(`/search/recommendations?limit=${limit}`, {
      requiresAuth: true,
    });
  },

  async sendFeedback(
    songId: number,
    action: 'accepted' | 'dismissed' | 'clicked'
  ): Promise<{ message: string }> {
    return apiClient.post(
      '/search/recommendations/feedback',
      { song_id: songId, action },
      { requiresAuth: true }
    );
  },
};

// Favorites API
export const favoritesAPI = {
  async favoriteSong(songId: number): Promise<{ message: string; favorited: boolean }> {
    return apiClient.post(`/api/v1/favorites/songs/${songId}`, {}, { requiresAuth: true });
  },

  async unfavoriteSong(songId: number): Promise<{ message: string; favorited: boolean }> {
    return apiClient.delete(`/api/v1/favorites/songs/${songId}`, { requiresAuth: true });
  },

  async checkSongFavoriteStatus(songId: number): Promise<{ favorited: boolean }> {
    return apiClient.get(`/api/v1/favorites/songs/${songId}/status`, { requiresAuth: true });
  },

  async favoriteAlbum(albumId: number): Promise<{ message: string; favorited: boolean }> {
    return apiClient.post(`/api/v1/favorites/albums/${albumId}`, {}, { requiresAuth: true });
  },

  async unfavoriteAlbum(albumId: number): Promise<{ message: string; favorited: boolean }> {
    return apiClient.delete(`/api/v1/favorites/albums/${albumId}`, { requiresAuth: true });
  },

  async checkAlbumFavoriteStatus(albumId: number): Promise<{ favorited: boolean }> {
    return apiClient.get(`/api/v1/favorites/albums/${albumId}/status`, { requiresAuth: true });
  },

  async listFavoriteSongs(): Promise<{ items: any[]; total: number }> {
    return apiClient.get('/api/v1/favorites/songs', { requiresAuth: true });
  },

  async listFavoriteAlbums(): Promise<{ items: any[]; total: number }> {
    return apiClient.get('/api/v1/favorites/albums', { requiresAuth: true });
  },
};
