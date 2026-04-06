# Implementation Tasks

## Overview
Implementation tasks for Search-Recommendations module following Test-Driven Development (TDD) methodology. This feature delivers multi-entity search (<300ms response time) across artists, albums, and songs with relevance ranking, genre/year filtering, and personalized recommendations based on user playlists and review history. All tasks follow Red-Green-Refactor cycle: write failing test first, implement minimal code to pass, then refactor while keeping tests green.

## Task Breakdown

- [x] 1. Database schema setup
- [x] 1.1 (P) Create database migration for search_logs table
  - Create migration file with search_logs table: id (SERIAL primary key), user_id (integer foreign key to users.id nullable), query_text (varchar 500), result_count (integer), created_at (timestamptz default NOW)
  - Add index on created_at for temporal queries
  - Add index on query_text for trend analysis
  - Set user_id as nullable to support guest searches
  - Add ON DELETE SET NULL for user_id foreign key
  - _Requirements: 12_

- [x] 1.2 (P) Create database migration for recommendation_feedback table
  - Create migration file with recommendation_feedback table: user_id (integer foreign key), song_id (integer foreign key), action (varchar 50), created_at (timestamptz default NOW)
  - Add composite primary key on (user_id, song_id)
  - Add indexes on user_id and song_id for feedback queries
  - Add NOT NULL constraints on user_id, song_id, action
  - Add CHECK constraint for action values: 'accepted', 'dismissed', 'clicked'
  - _Requirements: 11_

- [x] 1.3 (P) Add genre columns to songs and albums tables
  - Create migration to add genre (varchar 100) column to songs table if not exists
  - Create migration to add genre (varchar 100) column to albums table if not exists
  - Add index on songs.genre for filtering queries
  - Add index on albums.genre for filtering queries
  - Backfill existing records with default genre or NULL
  - _Requirements: 3_

- [x] 2. Validation and schema definitions
- [x] 2.1 (P) Define Pydantic request schemas for search
  - Write failing tests for SearchRequest schema validation (query min 2 chars, genre enum, year range 1900 to current_year + 1)
  - Create SearchRequest schema with query validation (min_length=2), genres list (optional), year_min/year_max integers (optional)
  - Define GenreEnum with values: Rock, Pop, Jazz, Classical, Electronic, Hip-Hop, Metal, Country, R&B, Indie
  - Create SortParameter enum: relevance, popularity, release_date, rating
  - Implement custom validators for year range (1900 to current_year + 1)
  - _Requirements: 1, 3, 4, 5_

- [x] 2.2 (P) Define Pydantic response schemas for search
  - Define SearchResponse schema with artists, albums, songs arrays, total_count integer
  - Define ArtistResult schema with id, name, relevance_score (0-100), albums_count
  - Define AlbumResult schema with id, title, artist_id, artist_name, release_year, genre, relevance_score
  - Define SongResult schema with id, title, artist_name, album_title, genre, average_rating, review_count, relevance_score
  - Include proper JSON serialization for datetime and decimal fields
  - _Requirements: 1, 2_

- [x] 2.3 (P) Define Pydantic schemas for recommendations
  - Define RecommendationResponse schema with recommendations array, total_count
  - Define RecommendedSong schema with song_id, title, artist_name, album_title, genre, average_rating, score (0-100), reason string
  - Define FeedbackRequest schema with song_id integer, action enum ('accepted', 'dismissed', 'clicked')
  - Define UserProfile internal schema with favorite_genres list, favorite_artists list, playlist_song_count, review_count
  - _Requirements: 6, 10, 11_

- [x] 3. Repository layer implementation
- [x] 3.1 Implement SearchRepository for multi-entity queries
  - Write failing tests for SearchRepository.search_artists with relevance scoring (exact 100, prefix 80, contains 60)
  - Implement search_artists method using ILIKE with trigram indexes, calculate relevance_score with CASE statement, add popularity boost from albums_count
  - Write failing tests for SearchRepository.search_albums with genre and year filtering
  - Implement search_albums method with ILIKE on title, genre IN filter, year range WHERE clauses, join with artists for artist_name
  - Write failing tests for SearchRepository.search_songs with genre filtering and soft-delete exclusion
  - Implement search_songs method with ILIKE on title, genre IN filter, WHERE deleted_at IS NULL, join with albums and artists, add popularity boost from review_count
  - Limit all queries to 50 results
  - Order all results by relevance_score DESC
  - _Requirements: 1, 2, 3, 4_

- [x] 3.2 Implement RecommendationRepository for user profile extraction
  - Write failing tests for RecommendationRepository.build_user_profile extracting favorite genres and artists
  - Implement build_user_profile method querying top 3 genres from user's playlists (join playlists → playlist_songs → songs, group by genre, order by count DESC)
  - Query favorite artists from reviews with rating >= 4 (join reviews → songs → albums → artists)
  - Count playlist_song_count and review_count for data sufficiency check
  - Return UserProfile with favorite_genres, favorite_artists, counts
  - _Requirements: 6_

- [x] 3.3 Implement RecommendationRepository for candidate retrieval
  - Write failing tests for RecommendationRepository.get_candidate_songs excluding user's songs
  - Implement get_candidate_songs method extracting user's song IDs (UNION of playlist songs and reviewed songs)
  - Query candidate songs WHERE song.id NOT IN (user_song_ids) AND deleted_at IS NULL
  - Join with albums and artists for complete song details
  - Limit candidates to 100 for scoring
  - Write failing tests for get_popular_songs with rating and review_count filters
  - Implement get_popular_songs method querying songs WHERE average_rating >= 4.0 AND review_count >= 10, order by review_count DESC
  - _Requirements: 6, 8_

- [x] 3.4 (P) Implement AnalyticsRepository for search logging
  - Write failing tests for AnalyticsRepository.log_search with user_id and result_count
  - Implement log_search method inserting into search_logs table with query_text, result_count, user_id (nullable), timestamp
  - Handle database errors gracefully (non-blocking logging)
  - _Requirements: 12_

- [x] 3.5 (P) Implement FeedbackRepository for recommendation tracking
  - Write failing tests for FeedbackRepository.log_feedback with user_id, song_id, action
  - Implement log_feedback method inserting or updating recommendation_feedback table
  - Handle duplicate key violations using INSERT ... ON CONFLICT UPDATE
  - _Requirements: 11_

- [x] 4. Search service implementation
- [x] 4.1 Implement SearchService for multi-entity orchestration
  - Write failing tests for SearchService.search validating query minimum 2 characters
  - Implement search method validating query length, raising ValueError if < 2 characters
  - Write failing tests for executing multi-entity search across artists, albums, songs
  - Implement parallel queries calling SearchRepository for artists, albums, songs with limit 50 each
  - Write failing tests for genre filtering (OR logic with multiple selection)
  - Apply genre filter to albums and songs queries (albums with genres parameter, songs with genres parameter)
  - Write failing tests for year range filtering on albums (inclusive min/max)
  - Apply year_min and year_max filters to search_albums
  - Validate year range is between 1900 and current_year + 1, raise ValueError if invalid
  - _Requirements: 1, 3, 4_

- [x] 4.2 Implement SearchService result ranking and sorting
  - Write failing tests for relevance ranking (exact > prefix > contains + popularity boost)
  - Verify relevance_score calculated correctly in SearchRepository queries (test with exact match "Rock" = 100, prefix "Rock Band" = 80, contains "Hard Rock" = 60)
  - Write failing tests for custom sorting (popularity, release_date, rating)
  - Implement _apply_sort method sorting results by sort_by parameter (popularity: review_count DESC, release_date: release_year DESC, rating: average_rating DESC)
  - Support sort_order parameter (asc or desc), default desc
  - Return SearchResults with grouped artists, albums, songs, total_count
  - _Requirements: 2, 5_

- [x] 4.3 Integrate SearchService with AnalyticsService
  - Write failing tests for search logging with query, result_count, user_id
  - Call AnalyticsService.log_search asynchronously (non-blocking) after search execution
  - Log zero-result searches for quality improvement
  - _Requirements: 12_

- [x] 5. Analytics and PII detection
- [x] 5.1 (P) Implement AnalyticsService with PII sanitization
  - Write failing tests for AnalyticsService.log_search with PII detection (email, phone, SSN patterns)
  - Implement contains_pii method using regex patterns: email (@ symbol), phone (XXX-XXX-XXXX), SSN (XXX-XX-XXXX)
  - Skip logging queries containing PII (return early without inserting)
  - Call AnalyticsRepository.log_search for non-PII queries
  - Log zero-result searches with result_count = 0
  - _Requirements: 12_

- [x] 6. Recommendation service implementation
- [x] 6.1 Implement RecommendationService with caching
  - Write failing tests for RecommendationService.get_recommendations checking cache first
  - Implement get_recommendations method checking Redis cache with key "recommendations:{user_id}"
  - On cache hit: Parse cached song IDs, call RecommendationRepository.get_songs_by_ids, return results
  - On cache miss: Call _generate_recommendations method
  - Write failing tests for cache storage with 24-hour TTL
  - Store recommendation results in Redis with SETEX 86400 seconds (24 hours)
  - Return list of RecommendedSong with song details, scores, reasons
  - _Requirements: 9_

- [x] 6.2 Implement recommendation generation with user profiling
  - Write failing tests for RecommendationService._generate_recommendations building user profile
  - Call RecommendationRepository.build_user_profile to extract favorite genres and artists
  - Write failing tests for data sufficiency check (<3 playlists and <3 reviews)
  - Check if playlist_song_count < 3 AND review_count < 3, use fallback if insufficient
  - On sufficient data: Call RecommendationRepository.get_candidate_songs with limit 100 (5x oversample for scoring)
  - Score each candidate using _score_candidate method
  - Generate recommendation reason using _generate_reason method
  - Sort scored candidates by score DESC, take top limit (default 20)
  - _Requirements: 6_

- [x] 6.3 Implement recommendation scoring algorithm
  - Write failing tests for _score_candidate with weighted factors (genre 40%, artist 30%, rating 20%, popularity 10%)
  - Implement _score_candidate method scoring songs based on: genre match (+40 points if in favorite_genres), artist match (+30 points if in favorite_artists), high rating (+20 points if average_rating >= 4.0), popularity (+10 points scaled by review_count / 1000)
  - Cap total score at 100
  - Normalize scores to 0-100 range
  - Write failing tests verifying scoring accuracy with known inputs
  - _Requirements: 7_

- [x] 6.4 Implement recommendation explanation generation
  - Write failing tests for _generate_reason with multiple scenarios (genre match, artist match, high rating, popular)
  - Implement _generate_reason method returning reason based on highest scoring factor: genre match → "Based on your love for {genre}", artist match → "Fans of {artist_name} also enjoy", high rating → "Highly rated by Sonic Immersive users", default → "Popular among Sonic Immersive users"
  - Return human-readable reason string
  - _Requirements: 10_

- [x] 6.5 Implement fallback strategy for insufficient data
  - Write failing tests for _get_popular_songs returning top-rated songs
  - Implement _get_popular_songs calling RecommendationRepository.get_popular_songs with limit
  - Return RecommendedSong list with score 90 and reason "Popular among Sonic Immersive users"
  - Write failing tests for timeout handling (1-second timeout)
  - Wrap _generate_recommendations in asyncio.timeout(1.0) context manager
  - On TimeoutError: Log timeout event, call _get_popular_songs fallback
  - _Requirements: 8, 9_

- [x] 7. Feedback tracking service
- [x] 7.1 (P) Implement FeedbackService for user actions
  - Write failing tests for FeedbackService.log_feedback with user_id, song_id, action
  - Implement log_feedback method validating action is 'accepted', 'dismissed', or 'clicked'
  - Call FeedbackRepository.log_feedback to store feedback
  - Write failing tests for feedback preventing duplicate votes (same user, song, action)
  - Return success message or 400 Bad Request if validation fails
  - _Requirements: 11_

- [x] 8. API routes and endpoints
- [x] 8.1 Implement GET /search endpoint for multi-entity search
  - Write failing integration tests for GET /search with query parameter (valid query returns 200 OK with grouped results)
  - Create GET /search route accepting query parameters: q (required), genres (optional list), year_min (optional), year_max (optional), sort_by (optional), sort_order (optional)
  - Validate query using SearchRequest schema (Pydantic validation)
  - Call SearchService.search method
  - Return 200 OK with SearchResponse (artists, albums, songs arrays, total_count)
  - Write failing tests for query too short (<2 chars returns 400 Bad Request)
  - Return 400 Bad Request with message "Search query must be at least 2 characters"
  - Write failing tests for invalid genre (returns 400 Bad Request with "Invalid genre")
  - Validate genre values against GenreEnum
  - _Requirements: 1, 3, 4, 5_

- [x] 8.2 Implement GET /search endpoint with filtering
  - Write failing integration tests for genre filtering (multiple genres with OR logic)
  - Pass genres parameter to SearchService.search as list
  - Return only songs and albums matching genres
  - Write failing integration tests for year range filtering on albums
  - Pass year_min and year_max parameters to SearchService.search
  - Return only albums within year range (inclusive)
  - Validate year range 1900 to current_year + 1, return 400 Bad Request if invalid
  - _Requirements: 3, 4_

- [x] 8.3 Implement GET /search endpoint with sorting
  - Write failing integration tests for sorting by popularity, release_date, rating
  - Pass sort_by and sort_order parameters to SearchService.search
  - Return results sorted by specified parameter (override default relevance sort)
  - Default to relevance sort if invalid sort_by provided
  - Support sort_order: asc or desc (default desc)
  - _Requirements: 5_

- [x] 8.4 Implement GET /recommendations endpoint for personalized suggestions
  - Write failing integration tests for GET /recommendations with authenticated user (returns 200 OK with recommendations)
  - Create GET /recommendations route with get_current_user dependency (JWT authentication required)
  - Accept optional limit parameter (default 20)
  - Call RecommendationService.get_recommendations with user_id and limit
  - Return 200 OK with RecommendationResponse (recommendations array, total_count)
  - Write failing tests for unauthenticated request (returns 401 Unauthorized)
  - Require authentication via get_current_user dependency
  - _Requirements: 6_

- [x] 8.5 Implement GET /recommendations caching and performance
  - Write failing integration tests for cache hit (second request within 24h returns cached results)
  - Verify response time <1 second for cache hit
  - Write failing tests for cache miss (first request generates recommendations)
  - Verify response time <1 second for cache miss (with timeout fallback)
  - Write failing tests for insufficient user data (returns popular songs)
  - Verify new users receive popular/trending songs as fallback
  - _Requirements: 8, 9_

- [x] 8.6 (P) Implement POST /recommendations/feedback endpoint
  - Write failing integration tests for POST /recommendations/feedback with authenticated user (accepted action returns 200 OK)
  - Create POST /recommendations/feedback route with get_current_user dependency
  - Validate request using FeedbackRequest schema (song_id, action enum)
  - Call FeedbackService.log_feedback with user_id, song_id, action
  - Return 200 OK with success message
  - Write failing tests for unauthenticated request (returns 401 Unauthorized)
  - Write failing tests for invalid action (returns 400 Bad Request)
  - _Requirements: 11_

- [x] 9. Integration and end-to-end testing
- [x] 9.1* Test complete search flow with filtering
  - Write integration test for search lifecycle: submit query "rock" → verify multi-entity results → apply genre filter "Rock" → verify filtered results → apply year range filter → verify albums filtered by year
  - Test query too short (< 2 chars) returns 400 Bad Request
  - Test invalid genre returns 400 Bad Request with "Invalid genre"
  - Test invalid year range returns 400 Bad Request
  - Test zero-result search returns 200 OK with empty arrays
  - Verify search response time <300ms for 100k records
  - _Requirements: 1, 3, 4_

- [x] 9.2* Test search relevance ranking and sorting
  - Write integration test for relevance scoring: search "Rock" → verify exact match scores 100, prefix match scores 80, contains match scores 60
  - Test popularity boost applied correctly (higher albums_count or review_count increases score)
  - Test custom sorting: sort_by=popularity → verify results ordered by review_count DESC, sort_by=release_date → verify albums ordered by release_year DESC, sort_by=rating → verify songs ordered by average_rating DESC
  - Test sort_order parameter (asc vs desc)
  - _Requirements: 2, 5_

- [x] 9.3* Test recommendation generation workflow
  - Write integration test for personalized recommendations: user with 5 playlists and 10 reviews → generate recommendations → verify songs match user's favorite genres and artists → verify scores calculated correctly → verify reasons generated
  - Test insufficient data fallback: user with 2 playlists and 1 review → verify popular songs returned with reason "Popular among Sonic Immersive users"
  - Test recommendation caching: first request generates recommendations and caches, second request within 24h returns cached results, verify cache hit performance <100ms
  - Test recommendation timeout: slow profile building (mock delay >1s) → verify fallback to popular songs
  - _Requirements: 6, 7, 8, 9, 10_

- [x] 9.4* Test analytics and PII protection
  - Write integration test for search logging: submit search "rock" → verify logged in search_logs with query_text, result_count, user_id (if authenticated), timestamp
  - Test PII detection: search "user@example.com" → verify NOT logged (PII detected), search "123-456-7890" → verify NOT logged (phone detected)
  - Test zero-result search logging: search "xyz123abc" → verify logged with result_count = 0
  - Test guest search logging: unauthenticated search → verify logged with user_id NULL
  - _Requirements: 12_

- [x] 9.5* Test feedback tracking and performance
  - Write integration test for recommendation feedback: user views recommendations → clicks song (action='clicked') → adds to playlist (action='accepted') → verify both actions logged in recommendation_feedback table
  - Test feedback duplicate handling: user logs same action twice → verify updated timestamp, not duplicated
  - Test feedback prevents voting on same song multiple times with different actions
  - Verify search performance: 100 concurrent searches complete within 300ms (p95)
  - Verify recommendation performance: 100 users generate recommendations within 1 second (p95)
  - _Requirements: 11_

## Notes
- All tasks follow TDD methodology: Write failing test (Red) → Implement minimal code (Green) → Refactor while keeping tests green
- Tasks marked with `(P)` can be executed in parallel as they have no data dependencies
- Tasks marked with `*` are optional test coverage tasks that can be deferred post-MVP
- Use AsyncSession for all database operations per design.md
- Reuse trigram GIN indexes from music-catalog-management (automatic with ILIKE queries)
- Redis cache from auth-security-foundation used for recommendations (24-hour TTL)
- Search must complete within 300ms for 100k records (use EXPLAIN ANALYZE to verify indexes)
- Recommendations must complete within 1 second with timeout fallback
- PII detection prevents logging personally identifiable information (email, phone, SSN patterns)
- Recommendation scoring: genre 40%, artist 30%, rating 20%, popularity 10%
- Fallback to popular songs when user has <3 playlists and <3 reviews
