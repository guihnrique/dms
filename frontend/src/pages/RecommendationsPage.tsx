/**
 * Recommendations Page - Personalized song recommendations
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, Button, Icon, Layout } from '../components';
import { useAuth } from '../context/AuthContext';
import { recommendationsAPI } from '../api/services';
import type { RecommendedSong } from '../api/types';

export function RecommendationsPage() {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState<RecommendedSong[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadRecommendations();
    } else {
      setLoading(false);
    }
  }, [user]);

  async function loadRecommendations() {
    try {
      const data = await recommendationsAPI.get(20);
      setRecommendations(data.recommendations);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleFeedback(songId: number, action: 'accepted' | 'dismissed' | 'clicked') {
    try {
      await recommendationsAPI.sendFeedback(songId, action);
      // Remove dismissed songs from the list
      if (action === 'dismissed') {
        setRecommendations(recommendations.filter(r => r.song_id !== songId));
      }
    } catch (error) {
      console.error('Failed to send feedback:', error);
    }
  }

  if (!user) {
    return (
      <Layout.Container>
        <div className="pt-32 text-center">
          <Icon
            name="magic_button"
            size="lg"
            className="mx-auto mb-4 text-on-surface-variant"
          />
          <h1 className="font-headline text-4xl mb-4 text-gradient">
            Personalized Recommendations
          </h1>
          <p className="text-on-surface-variant mb-8 max-w-2xl mx-auto">
            Get personalized music recommendations based on your playlists and reviews.
            Sign in to discover new music tailored just for you.
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
            <p className="text-on-surface-variant">Generating recommendations...</p>
          </div>
        </div>
      </Layout.Container>
    );
  }

  return (
    <Layout.Container>
      <div className="pt-32 pb-16">
        <div className="text-center mb-12">
          <h1 className="font-headline text-4xl mb-4 text-gradient">
            Recommended For You
          </h1>
          <p className="text-on-surface-variant max-w-2xl mx-auto">
            Based on your listening history, playlists, and reviews
          </p>
        </div>

        {recommendations.length === 0 ? (
          <div className="text-center py-12">
            <Icon
              name="music_note"
              size="lg"
              className="mx-auto mb-4 text-on-surface-variant"
            />
            <p className="text-on-surface-variant mb-4">
              No recommendations available yet
            </p>
            <p className="text-sm text-on-surface-variant mb-6">
              Create playlists and review songs to get personalized recommendations
            </p>
            <div className="flex gap-4 justify-center">
              <Link to="/search">
                <Button variant="primary">
                  Search Music
                </Button>
              </Link>
              <Link to="/playlists">
                <Button variant="secondary">
                  My Playlists
                </Button>
              </Link>
            </div>
          </div>
        ) : (
          <Layout.Grid cols={2} gap={6}>
            {recommendations.map((rec) => (
              <Card key={rec.song_id} glass>
                <Card.Content>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <Link
                        to={`/songs/${rec.song_id}`}
                        onClick={() => handleFeedback(rec.song_id, 'clicked')}
                      >
                        <h3 className="font-headline text-xl mb-1 hover:text-primary transition-colors">
                          {rec.title}
                        </h3>
                      </Link>
                      <p className="text-sm text-on-surface-variant">
                        {rec.artist_name} · {rec.album_title}
                      </p>
                      {rec.genre && (
                        <p className="text-xs text-on-surface-variant mt-1">
                          {rec.genre}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-1 ml-4">
                      <div className="w-12 h-12 rounded-full bg-gradient-primary flex items-center justify-center">
                        <span className="text-sm font-medium">{rec.score}</span>
                      </div>
                    </div>
                  </div>

                  <p className="text-sm text-on-surface-variant mb-4 italic">
                    {rec.reason}
                  </p>

                  {rec.average_rating && (
                    <div className="flex items-center gap-1 mb-4">
                      <Icon name="star" size="sm" />
                      <span className="text-sm">
                        {rec.average_rating.toFixed(1)} average rating
                      </span>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleFeedback(rec.song_id, 'accepted')}
                    >
                      <Icon name="add" size="sm" className="mr-1" />
                      Add to Playlist
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleFeedback(rec.song_id, 'dismissed')}
                    >
                      <Icon name="close" size="sm" className="mr-1" />
                      Dismiss
                    </Button>
                  </div>
                </Card.Content>
              </Card>
            ))}
          </Layout.Grid>
        )}
      </div>
    </Layout.Container>
  );
}
