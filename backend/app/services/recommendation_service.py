"""
RecommendationService with caching and scoring - Tasks 6.1-6.5
Requirements: 6, 7, 8, 9, 10
"""
import asyncio
import json
import logging
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.search import RecommendedSong, RecommendationResponse, UserProfile

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for personalized recommendations with caching"""

    # Recommendation scoring weights
    GENRE_WEIGHT = 40
    ARTIST_WEIGHT = 30
    RATING_WEIGHT = 20
    POPULARITY_WEIGHT = 10

    # Data sufficiency thresholds
    MIN_PLAYLISTS = 3
    MIN_REVIEWS = 3

    def __init__(self, db: AsyncSession, redis_client=None):
        self.db = db
        self.repo = RecommendationRepository(db)
        self.redis = redis_client

    async def get_recommendations(
        self,
        user_id: int,
        limit: int = 20
    ) -> RecommendationResponse:
        """
        Get personalized recommendations with caching

        Checks Redis cache first (24-hour TTL)
        On cache miss: generate recommendations and cache

        Args:
            user_id: User ID
            limit: Number of recommendations to return

        Returns:
            RecommendationResponse with recommended songs
        """
        # Check cache first
        if self.redis:
            cache_key = f"recommendations:{user_id}"
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    # Parse cached song IDs
                    song_ids = json.loads(cached)
                    songs_data = await self.repo.get_songs_by_ids(song_ids[:limit])

                    # Convert to RecommendedSong (with cached scores)
                    recommendations = [
                        RecommendedSong(
                            song_id=song["id"],
                            title=song["title"],
                            artist_name=song["artist_name"],
                            album_title=song["album_title"],
                            genre=song["genre"],
                            cover_art_url=song.get("cover_art_url"),
                            average_rating=song["average_rating"],
                            score=90,  # Default score for cached items
                            reason="Based on your listening history"
                        )
                        for song in songs_data
                    ]

                    return RecommendationResponse(
                        recommendations=recommendations,
                        total_count=len(recommendations)
                    )
            except Exception as e:
                logger.warning(f"Cache read error: {e}")

        # Cache miss: generate recommendations
        try:
            # Use timeout to ensure <1 second response
            recommendations = await asyncio.wait_for(
                self._generate_recommendations(user_id, limit),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            logger.warning(f"Recommendation generation timeout for user {user_id}, using fallback")
            recommendations = await self._get_popular_songs(limit)

        # Cache results (24-hour TTL)
        if self.redis and recommendations:
            cache_key = f"recommendations:{user_id}"
            song_ids = [rec.song_id for rec in recommendations]
            try:
                await self.redis.setex(
                    cache_key,
                    86400,  # 24 hours
                    json.dumps(song_ids)
                )
            except Exception as e:
                logger.warning(f"Cache write error: {e}")

        return RecommendationResponse(
            recommendations=recommendations,
            total_count=len(recommendations)
        )

    async def _generate_recommendations(
        self,
        user_id: int,
        limit: int
    ) -> List[RecommendedSong]:
        """
        Generate personalized recommendations

        Steps:
        1. Build user profile (favorite genres/artists)
        2. Check data sufficiency (<3 playlists and <3 reviews)
        3. Get candidate songs (exclude user's songs)
        4. Score each candidate
        5. Generate recommendation reasons
        6. Sort by score and return top N

        Returns:
            List of RecommendedSong with scores and reasons
        """
        # Build user profile
        profile = await self.repo.build_user_profile(user_id)

        # Check data sufficiency
        if profile.playlist_song_count < self.MIN_PLAYLISTS and profile.review_count < self.MIN_REVIEWS:
            logger.info(f"Insufficient data for user {user_id}, using popular songs")
            return await self._get_popular_songs(limit)

        # Get candidate songs (5x oversample for scoring)
        candidates = await self.repo.get_candidate_songs(user_id, limit=limit * 5)

        if not candidates:
            # No candidates found, use popular songs
            return await self._get_popular_songs(limit)

        # Score each candidate
        scored_candidates = []
        for candidate in candidates:
            score = self._score_candidate(candidate, profile)
            reason = self._generate_reason(candidate, profile, score)

            scored_candidates.append(
                RecommendedSong(
                    song_id=candidate["id"],
                    title=candidate["title"],
                    artist_name=candidate["artist_name"],
                    album_title=candidate["album_title"],
                    genre=candidate["genre"],
                    cover_art_url=candidate.get("cover_art_url"),
                    average_rating=candidate["average_rating"],
                    score=score,
                    reason=reason
                )
            )

        # Sort by score DESC and take top N
        scored_candidates.sort(key=lambda x: x.score, reverse=True)
        return scored_candidates[:limit]

    def _score_candidate(self, candidate: dict, profile: UserProfile) -> int:
        """
        Score candidate song based on user profile

        Scoring factors (weights):
        - Genre match: 40% (in favorite_genres)
        - Artist match: 30% (in favorite_artists)
        - High rating: 20% (average_rating >= 4.0)
        - Popularity: 10% (scaled by review_count / 1000)

        Returns:
            Score 0-100 (capped)
        """
        score = 0

        # Genre match (+40 points)
        if candidate.get("genre") in profile.favorite_genres:
            score += self.GENRE_WEIGHT

        # Artist match (+30 points)
        if candidate.get("artist_id") in profile.favorite_artists:
            score += self.ARTIST_WEIGHT

        # High rating (+20 points if >= 4.0)
        avg_rating = candidate.get("average_rating")
        if avg_rating and float(avg_rating) >= 4.0:
            score += self.RATING_WEIGHT

        # Popularity boost (+10 points scaled by review_count)
        review_count = candidate.get("review_count", 0)
        popularity_score = min(review_count / 1000.0, 1.0) * self.POPULARITY_WEIGHT
        score += int(popularity_score)

        # Cap at 100
        return min(score, 100)

    def _generate_reason(
        self,
        candidate: dict,
        profile: UserProfile,
        score: int
    ) -> str:
        """
        Generate human-readable recommendation reason

        Based on highest scoring factor:
        - Genre match: "Based on your love for {genre}"
        - Artist match: "Fans of {artist_name} also enjoy"
        - High rating: "Highly rated by Sonic Immersive users"
        - Default: "Popular among Sonic Immersive users"

        Returns:
            Human-readable reason string
        """
        # Check genre match (highest weight)
        if candidate.get("genre") in profile.favorite_genres:
            return f"Based on your love for {candidate['genre']}"

        # Check artist match
        if candidate.get("artist_id") in profile.favorite_artists:
            return f"Fans of {candidate['artist_name']} also enjoy"

        # Check high rating
        avg_rating = candidate.get("average_rating")
        if avg_rating and float(avg_rating) >= 4.0:
            return "Highly rated by Sonic Immersive users"

        # Default
        return "Popular among Sonic Immersive users"

    async def _get_popular_songs(self, limit: int) -> List[RecommendedSong]:
        """
        Fallback strategy: return popular songs

        Used when:
        - User has insufficient data (<3 playlists and <3 reviews)
        - Recommendation generation times out (>1 second)
        - No candidate songs found

        Returns:
            List of popular RecommendedSong with score 90
        """
        popular_songs = await self.repo.get_popular_songs(limit)

        return [
            RecommendedSong(
                song_id=song["id"],
                title=song["title"],
                artist_name=song["artist_name"],
                album_title=song["album_title"],
                genre=song["genre"],
                cover_art_url=song.get("cover_art_url"),
                average_rating=song["average_rating"],
                score=90,
                reason="Popular among Sonic Immersive users"
            )
            for song in popular_songs
        ]
