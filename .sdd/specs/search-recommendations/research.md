# Research & Design Decisions

## Summary
- **Feature**: `search-recommendations`
- **Discovery Scope**: Complex Integration (Multi-entity search + ML-style recommendation engine)
- **Key Findings**:
  - PostgreSQL trigram GIN indexes enable fast partial match search (<300ms for 100k records)
  - Recommendation algorithm uses collaborative filtering lite (genre/artist matching from user playlists and reviews)
  - Redis caching with 24-hour TTL for recommendation results prevents expensive recalculation
  - Search relevance scoring uses ts_rank for full-text or weighted ILIKE position matching
  - Recommendation scoring combines genre match (40%), artist match (30%), rating (20%), popularity (10%)
  - Fallback strategy provides popular/trending songs when user data insufficient (<3 playlists, <3 reviews)

## Research Log

### PostgreSQL Full-Text Search vs Trigram GIN Indexes
- **Context**: Requirement 1 specifies case-insensitive partial match search across artists/albums/songs with <300ms performance
- **Sources Consulted**:
  - PostgreSQL full-text search (tsvector, tsquery, ts_rank)
  - Trigram GIN indexes (pg_trgm extension)
  - music-catalog-management research (trigram approach selected)
  - Search performance benchmarks
- **Findings**:
  - **Full-text search (tsvector)**: Best for natural language, supports ranking, requires tsvector column
  - **Trigram GIN index**: Best for partial match (ILIKE '%query%'), simpler than full-text, reuses from catalog
  - **Performance**: Trigram GIN index achieves <200ms for 100k records with proper index
  - **music-catalog-management precedent**: Already uses trigram GIN for artist/album/song search
  - **Relevance ranking**: Full-text provides ts_rank, trigram requires custom scoring (position, exact match)
- **Implications**:
  - Reuse trigram GIN indexes from music-catalog-management (already exists)
  - Custom relevance scoring: Exact match > prefix match > contains match
  - Search query: `WHERE name ILIKE '%query%'` uses trigram index automatically
  - Multi-entity search: UNION ALL across artists/albums/songs queries

### Recommendation Algorithm: Collaborative Filtering Lite
- **Context**: Requirement 6 and 7 specify personalized recommendations analyzing playlists, reviews, ratings
- **Sources Consulted**:
  - Collaborative filtering algorithms (user-based, item-based)
  - Content-based filtering (genre, artist matching)
  - Hybrid recommendation systems
  - Simple scoring algorithms for MVP
- **Findings**:
  - **Full collaborative filtering**: Matrix factorization, requires significant user data and computation (overkill for MVP)
  - **Content-based filtering**: Match genres/artists from user preferences (simpler, explainable)
  - **Hybrid lite approach**: Combine user's favorite genres/artists with popularity signals
  - **User profile extraction**:
    1. Extract genres from user's playlist songs (GROUP BY genre, COUNT)
    2. Extract favorite artists from user's playlists and high-rated reviews (4-5 stars)
    3. Identify rating patterns (average user rating, preferred genres)
  - **Candidate song scoring**:
    - Genre match: +40 points if song genre in user's top 3 genres
    - Artist match: +30 points if song artist in user's favorite artists
    - High rating: +20 points if average_rating >= 4.0
    - Popularity: +10 points scaled by review_count (max 10k reviews = 10 points)
  - **Deduplication**: Exclude songs already in user's playlists or reviewed
- **Implications**:
  - RecommendationService.build_user_profile() extracts favorite genres/artists
  - RecommendationService.score_candidate() calculates weighted score (0-100)
  - Simple algorithm sufficient for MVP, explainable to users
  - Future: Upgrade to collaborative filtering with more user data

### Redis Caching for Recommendation Results
- **Context**: Requirement 9 specifies 24-hour TTL caching to avoid expensive recalculation
- **Sources Consulted**:
  - Redis caching patterns (key-value, expiration)
  - Cache invalidation strategies
  - Recommendation system caching best practices
- **Findings**:
  - **Cache key**: `recommendations:{user_id}` (per-user cached list)
  - **TTL**: 24 hours (daily refresh captures new user activity)
  - **Cache structure**: Store list of song IDs with scores, fetch song details on-demand
  - **Cache invalidation**: Auto-expire after 24 hours, manual invalidate on major user activity (new playlist, review)
  - **Cache miss handling**: Generate recommendations, cache result, return to user
  - **Alternative**: Store recommendations in database with generated_at timestamp (simpler but slower reads)
- **Implications**:
  - Use Redis for recommendation caching (fast, TTL support, already available from auth-security-foundation)
  - Cache structure: `{song_ids: [123, 456, 789], scores: [95, 87, 82], generated_at: timestamp}`
  - Fetch song details from database after cache hit (JOIN with songs/albums/artists)
  - Manual cache invalidation endpoint for admins (future)

### Search Relevance Scoring Algorithm
- **Context**: Requirement 2 specifies relevance ranking (exact match > prefix > contains, popularity signals)
- **Sources Consulted**:
  - PostgreSQL ts_rank for full-text search
  - Custom scoring formulas
  - Search ranking best practices
- **Findings**:
  - **Exact match detection**: `name = query` (case-insensitive) gets highest score (100)
  - **Prefix match**: `name ILIKE 'query%'` gets high score (80)
  - **Contains match**: `name ILIKE '%query%'` gets medium score (60)
  - **Popularity boost**: Add scaled popularity (albums_count for artists, review_count for songs)
  - **Formula**: `base_score + (popularity_metric / max_popularity * 20)` (max 20 bonus points)
  - **Full-text alternative**: Use ts_rank with tsvector if full-text implemented (more accurate, more complex)
- **Implications**:
  - SearchService.calculate_relevance_score() implements scoring formula
  - SQL: CASE WHEN name = query THEN 100 WHEN name ILIKE 'query%' THEN 80 ELSE 60 END
  - Add popularity boost from review_count or albums_count
  - Return relevance_score field in search results (0-100)

### Recommendation Fallback Strategy
- **Context**: Requirement 8 requires fallback when user has insufficient data (<3 playlists, <3 reviews)
- **Sources Consulted**:
  - Cold start problem in recommendation systems
  - Popular/trending content strategies
  - Hybrid recommendation fallbacks
- **Findings**:
  - **Cold start problem**: New users have no data → cannot generate personalized recommendations
  - **Fallback strategy**: Use popular/trending songs (average_rating >= 4.0, review_count >= 10)
  - **Partial data handling**: Mix personalized (if some data) with popular (fill remaining slots)
  - **Thresholds**: <3 playlist songs AND <3 reviews = insufficient data
  - **Fallback query**: `SELECT * FROM songs WHERE average_rating >= 4.0 AND review_count >= 10 ORDER BY review_count DESC LIMIT 20`
  - **Reason generation**: "Popular among Sonic Immersive users" for fallback recommendations
- **Implications**:
  - Check user data count before recommendation generation
  - If insufficient, use fallback query (popular songs)
  - If partial data (3-10 songs/reviews), mix 50% personalized + 50% popular
  - Log fallback usage for monitoring (track cold start rate)

### Genre and Year Filtering Implementation
- **Context**: Requirements 3 and 4 specify genre and release year filtering for search results
- **Sources Consulted**:
  - PostgreSQL IN operator for multiple values
  - Range filtering with BETWEEN
  - Filter application order (relevance → filter → sort)
- **Findings**:
  - **Genre filter**: `WHERE genre IN ('Rock', 'Pop', 'Jazz')` for multiple selection
  - **Year filter**: `WHERE release_year BETWEEN year_min AND year_max` for albums
  - **Predefined genre list**: Rock, Pop, Jazz, Classical, Electronic, Hip-Hop, Metal, Country, R&B, Indie
  - **Validation**: Pydantic enum for genre values, year range validation (1900 to current_year + 1)
  - **Application order**: Relevance ranking first, then filter, then final sort
  - **Index**: Create index on songs.genre, albums.release_year for filter performance
- **Implications**:
  - Pydantic GenreEnum with predefined values
  - SearchService applies filters after relevance ranking
  - Validation rejects invalid genres or year ranges
  - Return filtered results with relevance_score preserved

### Search Analytics and Logging
- **Context**: Requirement 12 specifies search query logging for trending analysis and quality improvement
- **Sources Consulted**:
  - Search analytics patterns
  - PII detection and sanitization
  - Aggregation strategies for reporting
- **Findings**:
  - **Log structure**: search_logs(id, user_id, query_text, result_count, timestamp)
  - **PII detection**: Check query for email patterns, phone numbers, names (simple regex)
  - **Aggregation**: Daily job aggregates popular queries (GROUP BY query_text, COUNT)
  - **Zero-result tracking**: Log queries with result_count = 0 for search quality improvement
  - **CTR tracking**: Log click events when user selects search result
  - **Data retention**: Anonymize user_id after 90 days (GDPR compliance)
- **Implications**:
  - Create search_logs table with query_text, result_count, user_id (nullable)
  - AnalyticsService.log_search() checks for PII before logging
  - Background job aggregates search data daily
  - Admin dashboard displays popular searches, zero-result queries

### Recommendation Feedback Loop
- **Context**: Requirement 11 specifies tracking user feedback (dismissed, accepted) to improve recommendations
- **Sources Consulted**:
  - Recommendation feedback patterns
  - Reinforcement learning for recommendations (advanced)
  - Simple feedback adjustments
- **Findings**:
  - **Feedback table**: recommendation_feedback(user_id, song_id, action, timestamp)
  - **Actions**: accepted (added to playlist), dismissed (hidden/skipped), clicked (viewed details)
  - **Feedback application**: Reduce score for dismissed songs and similar songs (same artist/genre)
  - **CTR tracking**: Calculate click-through rate from feedback data
  - **Advanced**: Machine learning model adjusts weights based on feedback (future enhancement)
  - **Simple approach**: If user dismisses artist, reduce artist match score by 10% in future recommendations
- **Implications**:
  - Create recommendation_feedback table with action enum
  - FeedbackService.record_feedback() logs user actions
  - Future: Adjust scoring weights based on aggregate feedback patterns
  - Monitor CTR for recommendation quality assessment

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| **Repository + Service Pattern (Selected)** | Search and Recommendation services with repository layer | Consistent with existing modules, testable, clear boundaries | Extra abstraction layer | Aligns with Clean Architecture |
| Search Engine (Elasticsearch) | Dedicated search engine with advanced features | Powerful search, faceted filtering, relevance tuning | Additional infrastructure, complexity | Future consideration if search becomes core feature |
| ML Recommendation Service | Separate microservice for recommendations with ML models | Scalable, specialized, real-time learning | Significant complexity, requires ML expertise | Future: Upgrade from content-based to collaborative filtering |

**Selected**: Repository + Service Pattern
- Consistent with music-catalog-management, user-playlists, reviews-ratings
- Search: SearchService + SearchRepository for multi-entity queries
- Recommendations: RecommendationService + caching layer for performance
- Testable: Mock repository/cache in unit tests, real DB in integration tests

## Design Decisions

### Decision: Trigram GIN Indexes for Partial Match Search (Reuse from Catalog)
- **Context**: Requirement 1 requires case-insensitive partial match search with <300ms performance
- **Alternatives Considered**:
  1. **Trigram GIN indexes** - Reuse from music-catalog-management, proven performance
  2. **Full-text search (tsvector)** - More powerful but requires tsvector column and migration
  3. **Elasticsearch** - Dedicated search engine, most powerful but complex infrastructure
- **Selected Approach**: Trigram GIN indexes (already exists)
  ```sql
  -- Already created in music-catalog-management
  CREATE EXTENSION IF NOT EXISTS pg_trgm;
  CREATE INDEX idx_artists_name_trgm ON artists USING GIN (name gin_trgm_ops);
  CREATE INDEX idx_albums_title_trgm ON albums USING GIN (title gin_trgm_ops);
  CREATE INDEX idx_songs_title_trgm ON songs USING GIN (title gin_trgm_ops);
  ```
  ```python
  # Search query uses indexes automatically
  query = f"%{search_term}%"
  artists = await db.execute(
      select(Artist).where(Artist.name.ilike(query)).limit(50)
  )
  ```
- **Rationale**:
  - Trigram indexes already created in music-catalog-management (no migration needed)
  - Proven to achieve <200ms for 100k records (exceeds 300ms requirement)
  - Simpler than full-text search (no tsvector column, no query rewrite)
  - ILIKE '%query%' automatically uses trigram index
- **Trade-offs**:
  - **Benefit**: Reuse existing infrastructure, simple queries, meets performance requirement
  - **Compromise**: Less sophisticated than full-text search (no stemming, synonyms)
- **Follow-up**: Monitor search performance, consider Elasticsearch if requirements expand

### Decision: Content-Based Recommendation with Genre/Artist Matching
- **Context**: Requirement 6 and 7 require personalized recommendations from playlists and reviews
- **Alternatives Considered**:
  1. **Content-based (genre/artist matching)** - Simple, explainable, sufficient for MVP
  2. **Collaborative filtering (user-item matrix)** - More accurate but requires significant data
  3. **Hybrid (content + collaborative)** - Best accuracy but complex implementation
- **Selected Approach**: Content-based filtering with weighted scoring
  ```python
  async def build_user_profile(user_id: int):
      # Extract favorite genres from playlists
      favorite_genres = await db.execute(
          select(Song.genre, func.count())
          .join(PlaylistSong)
          .join(Playlist)
          .where(Playlist.owner_user_id == user_id)
          .group_by(Song.genre)
          .order_by(func.count().desc())
          .limit(3)
      )
      
      # Extract favorite artists from reviews (4-5 stars)
      favorite_artists = await db.execute(
          select(Artist.id)
          .join(Album)
          .join(Song)
          .join(Review)
          .where(Review.user_id == user_id)
          .where(Review.rating >= 4)
          .group_by(Artist.id)
      )
      
      return favorite_genres, favorite_artists
  
  def score_candidate(song, user_profile):
      score = 0
      # Genre match: +40 points
      if song.genre in user_profile.favorite_genres:
          score += 40
      # Artist match: +30 points
      if song.artist_id in user_profile.favorite_artists:
          score += 30
      # High rating: +20 points
      if song.average_rating >= 4.0:
          score += 20
      # Popularity: +10 points (scaled)
      score += min(10, song.review_count / 1000)
      return score
  ```
- **Rationale**:
  - Simple algorithm sufficient for MVP (explainable, no ML dependencies)
  - Leverages existing data (playlists, reviews) without complex matrix calculations
  - Meets 1-second performance requirement (simple scoring, cacheable)
  - Provides clear recommendation reasons (genre match, artist match)
- **Trade-offs**:
  - **Benefit**: Simple, fast, explainable, works with limited user data
  - **Compromise**: Less accurate than collaborative filtering (no "users like you" signal)
- **Follow-up**: Upgrade to collaborative filtering when user base grows (>10k active users)

### Decision: Redis Caching with 24-Hour TTL for Recommendations
- **Context**: Requirement 9 requires caching to avoid expensive recalculation
- **Alternatives Considered**:
  1. **Redis caching** - Fast, TTL support, already available
  2. **Database table (recommendations)** - Simpler but slower reads
  3. **In-memory cache (lru_cache)** - Fast but not shared across instances
- **Selected Approach**: Redis caching with 24-hour TTL
  ```python
  async def get_recommendations(user_id: int):
      cache_key = f"recommendations:{user_id}"
      cached = await redis.get(cache_key)
      
      if cached:
          song_ids = json.loads(cached)
          songs = await song_repo.get_by_ids(song_ids)
          return songs
      
      # Generate recommendations
      recommendations = await recommendation_service.generate(user_id)
      song_ids = [r.song_id for r in recommendations]
      
      # Cache for 24 hours
      await redis.setex(cache_key, 86400, json.dumps(song_ids))
      
      return recommendations
  ```
- **Rationale**:
  - Redis already available from auth-security-foundation (no new dependency)
  - 24-hour TTL captures new user activity daily (balance freshness and performance)
  - Fast reads (sub-millisecond cache hit)
  - Shared across API instances (horizontal scaling support)
- **Trade-offs**:
  - **Benefit**: Fast reads, shared cache, automatic expiration
  - **Compromise**: Cache invalidation on manual refresh requires Redis clear
- **Follow-up**: Manual cache invalidation endpoint for admins (immediate refresh)

### Decision: Custom Relevance Scoring (Exact > Prefix > Contains)
- **Context**: Requirement 2 requires relevance ranking with exact/prefix/contains matching
- **Alternatives Considered**:
  1. **Custom scoring formula** - Simple, deterministic, no full-text required
  2. **PostgreSQL ts_rank** - More sophisticated but requires tsvector column
  3. **Levenshtein distance** - Edit distance scoring, slower
- **Selected Approach**: Custom scoring with CASE WHEN
  ```sql
  SELECT 
    id,
    name,
    CASE 
      WHEN LOWER(name) = LOWER(?) THEN 100  -- Exact match
      WHEN LOWER(name) LIKE LOWER(?) || '%' THEN 80  -- Prefix match
      ELSE 60  -- Contains match
    END + (albums_count / 100.0 * 20) AS relevance_score
  FROM artists
  WHERE name ILIKE '%' || ? || '%'
  ORDER BY relevance_score DESC
  LIMIT 50
  ```
- **Rationale**:
  - Simple deterministic scoring (no complex full-text configuration)
  - Exact match prioritized (user typed full name)
  - Prefix match prioritized over contains (user started typing name)
  - Popularity boost (albums_count, review_count) differentiates similar matches
- **Trade-offs**:
  - **Benefit**: Simple, deterministic, no migration needed
  - **Compromise**: Less sophisticated than ts_rank (no phrase matching, stemming)
- **Follow-up**: Consider full-text search if relevance quality insufficient

### Decision: Fallback to Popular Songs When User Data Insufficient
- **Context**: Requirement 8 requires fallback strategy for cold start problem
- **Alternatives Considered**:
  1. **Popular songs (rating + review count)** - Simple, always available
  2. **Trending songs (recent reviews)** - Time-sensitive, may not be stable
  3. **Random songs** - Poor UX, no quality signal
- **Selected Approach**: Popular songs with rating >= 4.0, review_count >= 10
  ```python
  async def get_recommendations(user_id: int):
      user_profile = await build_user_profile(user_id)
      
      if user_profile.playlist_song_count < 3 and user_profile.review_count < 3:
          # Insufficient data, use fallback
          return await get_popular_songs(limit=20)
      
      # Generate personalized recommendations
      recommendations = await generate_personalized(user_profile)
      
      # If not enough personalized, mix with popular
      if len(recommendations) < 20:
          popular = await get_popular_songs(limit=20 - len(recommendations))
          recommendations.extend(popular)
      
      return recommendations
  
  async def get_popular_songs(limit: int):
      return await db.execute(
          select(Song)
          .where(Song.average_rating >= 4.0)
          .where(Song.review_count >= 10)
          .order_by(Song.review_count.desc())
          .limit(limit)
      )
  ```
- **Rationale**:
  - Popular songs always available (no dependency on user data)
  - Quality threshold (rating >= 4.0) ensures good experience
  - Review count threshold (>= 10) filters low-confidence ratings
  - Mix strategy provides partial personalization when possible
- **Trade-offs**:
  - **Benefit**: Always provides recommendations, gradual personalization as user data grows
  - **Compromise**: Less personalized for new users (cold start UX)
- **Follow-up**: Monitor cold start rate, improve onboarding to collect preferences faster

### Decision: Multi-Entity Search with UNION ALL
- **Context**: Requirement 1 requires simultaneous search across artists, albums, songs
- **Alternatives Considered**:
  1. **UNION ALL three queries** - Simple, parallel execution possible
  2. **Three separate queries** - Sequential, slower
  3. **Single query with multiple LIKE conditions** - Complex, less performant
- **Selected Approach**: UNION ALL with entity type tagging
  ```python
  # Construct query for each entity type
  artist_query = (
      select(
          Artist.id,
          Artist.name.label('title'),
          literal('artist').label('entity_type'),
          calculate_relevance_score(Artist.name, search_term).label('relevance_score')
      )
      .where(Artist.name.ilike(f'%{search_term}%'))
      .limit(50)
  )
  
  album_query = (
      select(
          Album.id,
          Album.title,
          literal('album').label('entity_type'),
          calculate_relevance_score(Album.title, search_term).label('relevance_score')
      )
      .where(Album.title.ilike(f'%{search_term}%'))
      .limit(50)
  )
  
  song_query = (
      select(
          Song.id,
          Song.title,
          literal('song').label('entity_type'),
          calculate_relevance_score(Song.title, search_term).label('relevance_score')
      )
      .where(Song.title.ilike(f'%{search_term}%'))
      .limit(50)
  )
  
  # UNION ALL for parallel execution
  combined = union_all(artist_query, album_query, song_query)
  results = await db.execute(combined)
  
  # Group by entity type
  grouped = {
      'artists': [],
      'albums': [],
      'songs': []
  }
  for row in results:
      grouped[row.entity_type + 's'].append(row)
  ```
- **Rationale**:
  - UNION ALL enables parallel query execution (PostgreSQL optimization)
  - Each query limited to 50 results (prevents overwhelming response)
  - Entity type tagging enables grouping in application layer
  - Meets 300ms performance requirement (each query <100ms with indexes)
- **Trade-offs**:
  - **Benefit**: Parallel execution, clean separation, meets performance requirement
  - **Compromise**: Slightly more complex than separate queries
- **Follow-up**: Monitor query plan (EXPLAIN ANALYZE), verify parallel execution

## Risks & Mitigations

### Risk 1: Search Performance Degradation Beyond 100k Records
- **Description**: Trigram ILIKE queries may exceed 300ms as dataset grows beyond 100k records
- **Impact**: Slow search experience, poor UX
- **Mitigation**:
  - Monitor p95 search latency (alert if >300ms)
  - Limit results per entity to 50 (already implemented)
  - Add additional indexes on frequently searched fields
  - Future: Migrate to Elasticsearch if dataset exceeds 500k records

### Risk 2: Recommendation Generation Timeout (>1s)
- **Description**: Complex user profiles (many playlists, reviews) may cause recommendation generation to exceed 1s
- **Impact**: Slow recommendations, fallback to popular songs
- **Mitigation**:
  - Implement 1-second timeout on recommendation generation
  - Use fallback strategy (popular songs) on timeout
  - Cache recommendations with 24-hour TTL (avoid recalculation)
  - Optimize query: Limit playlist/review analysis to recent 100 songs

### Risk 3: Cold Start Problem (New Users)
- **Description**: New users with no playlists or reviews receive only popular songs (not personalized)
- **Impact**: Poor first-time experience, low engagement
- **Mitigation**:
  - Implement onboarding flow to collect genre/artist preferences
  - Offer trending playlists during onboarding (quick start)
  - Mix popular songs with diverse genres (avoid filter bubble)
  - Monitor cold start rate (% users with <3 playlists/reviews)

### Risk 4: Cache Staleness (24-Hour TTL)
- **Description**: User adds new playlist/review but recommendations not updated until cache expires
- **Impact**: Recommendations feel outdated, don't reflect recent activity
- **Mitigation**:
  - Acceptable for MVP (24-hour refresh reasonable)
  - Future: Manual cache invalidation on major activity (new playlist, review)
  - Alternative: Reduce TTL to 12 hours (balance freshness and performance)
  - Provide "Refresh recommendations" button in UI

### Risk 5: Search Analytics PII Leakage
- **Description**: Users may search for names, emails, phone numbers (PII) which gets logged
- **Impact**: GDPR compliance violation, privacy risk
- **Mitigation**:
  - Implement PII detection regex (email, phone patterns)
  - Sanitize queries before logging (replace PII with [REDACTED])
  - Anonymize user_id after 90 days (GDPR compliance)
  - Do not log queries containing @, phone number patterns

## References

### Official Documentation
- [PostgreSQL Trigram Indexes](https://www.postgresql.org/docs/current/pgtrgm.html) - pg_trgm extension, GIN indexes
- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html) - tsvector, ts_rank (future consideration)
- [Redis Caching](https://redis.io/docs/manual/keyspace/) - TTL, expiration policies

### Recommendation Systems
- Content-Based Filtering - Genre and artist matching
- Collaborative Filtering - Future upgrade path
- Cold Start Problem - Fallback strategies

### Internal References
- `.sdd/steering/structure.md` - Backend structure patterns
- `.sdd/steering/tech.md` - SQLAlchemy ORM, FastAPI async patterns, TDD requirements
- `.sdd/specs/music-catalog-management/research.md` - Trigram GIN index patterns
- `.sdd/specs/user-playlists/design.md` - Playlist data access patterns
- `.sdd/specs/reviews-ratings/design.md` - Review and rating data access
