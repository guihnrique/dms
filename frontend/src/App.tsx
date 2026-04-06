/**
 * Main App Component - Following Stitch Design System
 * Sidebar navigation + main content area
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components';
import { AuthProvider } from './context/AuthContext';
import {
  HomePage,
  ExplorePage,
  SearchPage,
  LoginPage,
  LibraryPage,
  PlaylistsPage,
  RecommendationsPage,
  ArtistsListPage,
  ArtistProfilePage,
  AlbumsListPage,
  AlbumDetailPage,
  SongDetailPage,
  CreateReviewPage,
} from './pages';

function AppContent() {
  return (
    <div className="min-h-screen bg-background text-on-surface overflow-x-hidden">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Canvas */}
      <main className="md:ml-64">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/explore" element={<ExplorePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/playlists" element={<PlaylistsPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="/artists" element={<ArtistsListPage />} />
          <Route path="/artists/:id" element={<ArtistProfilePage />} />
          <Route path="/albums" element={<AlbumsListPage />} />
          <Route path="/albums/:id" element={<AlbumDetailPage />} />
          <Route path="/songs/:id" element={<SongDetailPage />} />
          <Route path="/songs/:id/review" element={<CreateReviewPage />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
