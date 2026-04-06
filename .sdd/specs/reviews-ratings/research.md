# Research & Design Decisions

## Summary
- **Feature**: `reviews-ratings`
- **Discovery Scope**: Extension (Integrates with music catalog, auth, and user-playlists systems)
- **Key Findings**:
  - Unique constraint on (user_id, song_id) enforces one review per user per song at database level
  - Average rating calculation cached in songs table (denormalized) with trigger for recalculation avoids N queries
  - Helpfulness voting requires separate review_votes table tracking user votes with vote_type (helpful/not_helpful)
  - Content moderation with profanity filtering uses better-profanity library with is_flagged boolean field
  - PostgreSQL CHECK constraint enforces rating range (1-5) at database level
  - Ownership verification reuses auth get_current_user pattern from user-playlists

## Research Log

### Database Unique Constraint for One Review Per User Per Song
- **Context**: Requirement 10 enforces one review limit per user per song to prevent spam
- **Sources Consulted**:
  - PostgreSQL unique constraints documentation
  - SQLAlchemy unique constraint patterns
  - Upsert (INSERT ON CONFLICT) strategies
- **Findings**:
  - **Unique constraint**: `UNIQUE(user_id, song_id)` at database level prevents duplicates
  - **Conflict handling**: SQLAlchemy doesn't support native upsert, requires explicit check or ON CONFLICT
  - **PostgreSQL ON CONFLICT**: `INSERT ... ON CONFLICT (user_id, song_id) DO UPDATE` upserts review
  - **Application-level check**: Query for existing review, then INSERT or UPDATE based on result
  - **Error handling**: IntegrityError raised if duplicate attempted without conflict handling
- **Implications**:
  - Add UNIQUE(user_id, song_id) constraint to reviews table
  - Service method: Check if review exists, then create or update
  - Return clear message: "You have already reviewed this song. Your review has been updated."
  - created_at preserved on update, updated_at modified

### Average Rating Calculation and Caching Strategy
- **Context**: Requirement 6 requires average rating calculation with caching to avoid recalculating on every request
- **Sources Consulted**:
  - Denormalization patterns (store calculated fields)
  - Database triggers for automatic recalculation
  - Redis caching strategies
  - Query optimization for aggregates
- **Findings**:
  - **Option 1: Calculate on query**: `SELECT AVG(rating) FROM reviews WHERE song_id = ?` (slow for 10k reviews)
  - **Option 2: Denormalize**: Store average_rating, review_count in songs table (fast reads, requires update logic)
  - **Option 3: Redis cache**: Cache calculated average (TTL 5 min), recalculate on miss (complexity)
  - **Database trigger approach**: PostgreSQL trigger on reviews INSERT/UPDATE/DELETE recalculates songs.average_rating
  - **Application-level approach**: Service recalculates after review mutation, updates songs table
  - **Performance**: Denormalized approach (Option 2) recommended for MVP, trigger for automation
- **Implications**:
  - Add average_rating (DECIMAL) and review_count (INTEGER) columns to songs table
  - ReviewService recalculates average after create/update/delete
  - Future optimization: PostgreSQL trigger automates recalculation
  - Round average to 1 decimal place: ROUND(AVG(rating), 1)

### Helpfulness Voting System with Vote Tracking
- **Context**: Requirement 7 requires helpfulness voting (helpful/not helpful) with vote tracking per user
- **Sources Consulted**:
  - Voting system patterns (upvote/downvote, like/dislike)
  - Composite key strategies for vote tracking
  - Vote change handling (user switches vote)
- **Findings**:
  - **Vote tracking table**: review_votes(user_id, review_id, vote_type) with composite PK
  - **Vote types**: helpful (+1), not_helpful (-1), or boolean is_helpful (true/false)
  - **Helpful count storage**: Store helpful_count in reviews table (denormalized for performance)
  - **Vote change logic**:
    1. User votes helpful → Insert vote, increment helpful_count
    2. User changes to not_helpful → Update vote, decrement helpful_count by 2 (-1 for removal, -1 for not_helpful)
    3. User removes vote → Delete vote, decrement helpful_count
  - **Prevent self-voting**: Check review.user_id != current_user.id before allowing vote
  - **Upsert pattern**: ON CONFLICT (user_id, review_id) DO UPDATE for vote changes
- **Implications**:
  - Create review_votes table with (user_id, review_id) composite primary key
  - Add vote_type column: helpful (1) or not_helpful (-1), or boolean is_helpful
  - Store helpful_count in reviews table (default 0)
  - VotingService handles vote creation, update, and count adjustment
  - Prevent self-voting: Validate review.user_id != voter.user_id

### Content Moderation with Profanity Filtering
- **Context**: Requirement 8 requires automatic profanity detection and manual flagging for moderation
- **Sources Consulted**:
  - Python profanity filter libraries (better-profanity, profanity-check)
  - Content moderation patterns
  - Moderation queue implementation
- **Findings**:
  - **better-profanity library**: Lightweight, customizable word list, fast detection
  - **profanity-check library**: ML-based, more accurate but heavier (requires scikit-learn)
  - **Detection approach**: Check review body on create/update, set is_flagged=true if profanity detected
  - **Flagged review handling**: Do not display in public queries (WHERE is_flagged = false)
  - **Manual flagging**: Users can report reviews, increments flag_count field
  - **Admin moderation**: Admin endpoints to approve (set is_flagged=false) or delete flagged reviews
  - **Audit logging**: Log all moderation actions (flag, approve, delete) with moderator_user_id and timestamp
- **Implications**:
  - Add is_flagged (BOOLEAN, default false) and flag_count (INTEGER, default 0) to reviews table
  - Use better-profanity library for automatic detection (lightweight, sufficient for MVP)
  - ModerationService.check_profanity() scans review body, returns boolean
  - Public queries filter WHERE is_flagged = false
  - Admin endpoints: GET /admin/reviews/flagged, PATCH /admin/reviews/{id}/approve, DELETE /admin/reviews/{id}

### PostgreSQL CHECK Constraint for Rating Range
- **Context**: Requirement 1 validates rating is 1-5 integer, enforce at database level
- **Sources Consulted**:
  - PostgreSQL CHECK constraints documentation
  - SQLAlchemy CheckConstraint patterns
  - Application-level vs database-level validation
- **Findings**:
  - **CHECK constraint**: `CHECK (rating >= 1 AND rating <= 5)` at database level
  - **Data type**: Use SMALLINT (1 byte) instead of INTEGER (4 bytes) for rating (values 1-5)
  - **SQLAlchemy constraint**: `CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range')`
  - **Error handling**: IntegrityError raised if rating outside range, catch and return 400 Bad Request
  - **Pydantic validation**: Also validate in Pydantic schema for early rejection (before DB call)
- **Implications**:
  - Add CHECK constraint to reviews table: rating BETWEEN 1 AND 5
  - Use SMALLINT data type for rating column
  - Pydantic schema: `rating: int = Field(ge=1, le=5)`
  - Service catches IntegrityError and returns clear message: "Rating must be between 1 and 5"

### Review Text Validation and Sanitization
- **Context**: Requirement 11 specifies review text validation (0-2000 chars, no empty strings, trim whitespace)
- **Sources Consulted**:
  - Pydantic custom validators
  - Text sanitization patterns
  - HTML/XSS prevention strategies
- **Findings**:
  - **Pydantic validator**: Custom validator strips whitespace, validates length, rejects empty
  - **Character limit**: 2000 characters (standard review length, balances detail and brevity)
  - **Whitespace handling**: `body.strip()` removes leading/trailing whitespace before storage
  - **Empty body allowed**: Reviews can have rating only (body optional, nullable in database)
  - **Special character validation**: Reject if body contains only special chars/numbers (no meaningful content)
  - **HTML sanitization**: Not required for MVP (frontend escapes output), future: use bleach library
- **Implications**:
  - Pydantic validator: Strip whitespace, validate length (0-2000), reject empty after strip
  - Database column: body TEXT NULL (optional review text)
  - Service validates body not empty string after strip (if provided)
  - Frontend: Display character counter (2000 - body.length) during composition

### Ownership Verification Dependency Pattern
- **Context**: Requirement 9 requires ownership verification for review update/delete (reuse auth pattern)
- **Sources Consulted**:
  - user-playlists verify_playlist_ownership pattern
  - FastAPI dependency injection
- **Findings**:
  - **Dependency pattern**: Create verify_review_ownership() dependency similar to playlists
  - **Composition**: Depends on get_current_user, fetches review, verifies user_id matches
  - **Return value**: Returns verified review to route handler (avoids duplicate query)
  - **Error handling**: Raises 404 if review not found, 403 if ownership verification fails
  - **Path parameter access**: Extracts review_id from path parameter
- **Implications**:
  - Create verify_review_ownership dependency in reviews module
  - Update/delete endpoints use dependency: `review: Review = Depends(verify_review_ownership)`
  - Consistent error messages with other modules (403 Forbidden, 404 Not Found)

### Review Retrieval Performance with Pagination
- **Context**: Requirement 4 specifies pagination (default 10, max 50) for song reviews
- **Sources Consulted**:
  - music-catalog-management pagination strategy
  - user-playlists pagination patterns
- **Findings**:
  - **Offset-based pagination**: LIMIT/OFFSET sufficient for review lists (not 10k+ records per page)
  - **Default page size**: 10 reviews (smaller than playlists/songs for UX, more digestible)
  - **Max page size**: 50 reviews (prevent excessive data transfer)
  - **Ordering**: created_at DESC (newest first) OR helpful_count DESC (most helpful first)
  - **Include username**: Join with users table to display reviewer username
  - **Exclude flagged**: Filter WHERE is_flagged = false in public queries
- **Implications**:
  - Pagination params: page (default 1), page_size (default 10, max 50)
  - Order by: created_at DESC default, support sort_by=helpful_count for most helpful
  - Response includes: items, total_count, page, page_size, total_pages
  - Query joins users table for username (eager loading)

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| **Repository Pattern (Selected)** | Separate data access layer with ReviewRepository, VotingRepository | Consistent with other modules, testable, clear boundaries | Extra abstraction layer | Aligns with existing architecture |
| Service-Only | Combine business logic and data access in ReviewService | Less boilerplate, faster development | Tight coupling, hard to test | Not recommended for complex logic |
| Event-Driven | Publish review events, subscribers update average rating | Decoupled, scalable | Complex for MVP, adds message broker | Future consideration if scaling needed |

**Selected**: Repository Pattern
- Consistent with music-catalog-management, user-playlists
- Clean separation: Service (business logic) → Repository (data access)
- Testable: Mock repository in unit tests, real DB in integration tests
- Enables future event-driven architecture (publish ReviewCreated events)

## Design Decisions

### Decision: Denormalized Average Rating in Songs Table
- **Context**: Requirement 6 requires average rating calculation with caching to avoid recalculating on every request
- **Alternatives Considered**:
  1. **Denormalize (store in songs table)** - Fast reads, requires update logic
  2. **Calculate on query** - Simple but slow for 10k reviews
  3. **Redis cache** - Fast but adds dependency, cache invalidation complexity
- **Selected Approach**: Denormalize average_rating and review_count in songs table
  ```sql
  ALTER TABLE songs ADD COLUMN average_rating DECIMAL(3,1);
  ALTER TABLE songs ADD COLUMN review_count INTEGER DEFAULT 0;
  ```
  ```python
  async def recalculate_average_rating(song_id: int):
      result = await db.execute(
          select(func.avg(Review.rating), func.count(Review.id))
          .where(Review.song_id == song_id)
          .where(Review.is_flagged == False)
      )
      avg_rating, count = result.one()
      await db.execute(
          update(Song)
          .where(Song.id == song_id)
          .values(average_rating=round(avg_rating, 1), review_count=count)
      )
  ```
- **Rationale**:
  - Fast reads (no aggregate query on every song detail request)
  - Simple implementation for MVP (service updates songs table after review mutation)
  - Acceptable data staleness (updated synchronously after review create/update/delete)
  - Meets 100ms calculation requirement (single UPDATE query)
- **Trade-offs**:
  - **Benefit**: Fast reads, meets performance requirement, simple for MVP
  - **Compromise**: Denormalization creates update logic complexity, potential inconsistency on failure
- **Follow-up**: Add PostgreSQL trigger for automatic recalculation (future optimization)

### Decision: Unique Constraint on (user_id, song_id) with Upsert Logic
- **Context**: Requirement 10 enforces one review per user per song
- **Alternatives Considered**:
  1. **Database unique constraint** - Enforced at DB level, prevents duplicates
  2. **Application-level check** - Query existing review, then create or update
  3. **PostgreSQL ON CONFLICT** - Upsert pattern (INSERT ON CONFLICT DO UPDATE)
- **Selected Approach**: Database unique constraint + application-level check
  ```sql
  ALTER TABLE reviews ADD CONSTRAINT unique_user_song UNIQUE(user_id, song_id);
  ```
  ```python
  async def create_or_update_review(user_id, song_id, rating, body):
      existing = await review_repo.get_by_user_and_song(user_id, song_id)
      if existing:
          # Update existing review
          existing.rating = rating
          existing.body = body
          existing.updated_at = datetime.now()
          return existing  # Message: "Your review has been updated"
      else:
          # Create new review
          return await review_repo.create(user_id, song_id, rating, body)
  ```
- **Rationale**:
  - Unique constraint prevents race condition (two simultaneous creates)
  - Application check provides clear UX message (updated vs created)
  - created_at preserved on update (audit trail of original review date)
  - Simple logic, no need for PostgreSQL-specific ON CONFLICT
- **Trade-offs**:
  - **Benefit**: Clear UX, race condition protected, audit trail preserved
  - **Compromise**: Extra query to check existence (acceptable 50-100ms)
- **Follow-up**: Monitor race condition frequency (should be rare, constraint handles it)

### Decision: Review Helpfulness Voting with Separate Votes Table
- **Context**: Requirement 7 requires helpfulness voting with vote tracking per user
- **Alternatives Considered**:
  1. **Separate votes table** - Track each user's vote, supports vote changes
  2. **Helpful/unhelpful counts only** - No vote tracking, users can vote multiple times
  3. **Like-only system** - Simplified (only helpful, no not_helpful option)
- **Selected Approach**: Separate review_votes table with vote_type
  ```sql
  CREATE TABLE review_votes (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    review_id INTEGER NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    vote_type SMALLINT NOT NULL,  -- 1 (helpful) or -1 (not_helpful)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, review_id)
  );
  ```
  ```python
  async def vote_review(user_id, review_id, vote_type: Literal[1, -1]):
      existing_vote = await vote_repo.get_vote(user_id, review_id)
      
      if existing_vote:
          # Change vote
          if existing_vote.vote_type == vote_type:
              raise ValueError("You have already voted this way")
          old_vote = existing_vote.vote_type
          existing_vote.vote_type = vote_type
          # Adjust count: remove old vote, add new vote
          adjustment = vote_type - old_vote  # e.g., 1 - (-1) = 2
          await review_repo.adjust_helpful_count(review_id, adjustment)
      else:
          # New vote
          await vote_repo.create(user_id, review_id, vote_type)
          await review_repo.adjust_helpful_count(review_id, vote_type)
  ```
- **Rationale**:
  - Vote tracking enables vote changes (user switches from helpful to not_helpful)
  - Composite primary key (user_id, review_id) enforces one vote per user per review
  - vote_type (-1, 1) enables both helpful and not_helpful (future: neutral = 0)
  - helpful_count in reviews table provides fast reads (no aggregate query)
- **Trade-offs**:
  - **Benefit**: Flexible, supports vote changes, prevents duplicate votes
  - **Compromise**: Extra table, more complex vote change logic
- **Follow-up**: Prevent self-voting (review.user_id != voter.user_id check)

### Decision: Profanity Filtering with better-profanity Library
- **Context**: Requirement 8 requires automatic profanity detection for content moderation
- **Alternatives Considered**:
  1. **better-profanity** - Lightweight, fast, customizable word list
  2. **profanity-check** - ML-based, more accurate but requires scikit-learn (heavier)
  3. **Manual moderation only** - No automatic detection, relies on user reports
- **Selected Approach**: better-profanity library for automatic detection
  ```python
  from better_profanity import profanity
  
  profanity.load_censor_words()  # Load default word list
  
  async def create_review(user_id, song_id, rating, body):
      is_flagged = profanity.contains_profanity(body) if body else False
      review = await review_repo.create(
          user_id, song_id, rating, body, is_flagged=is_flagged
      )
      if is_flagged:
          logger.warning(f"Review {review.id} flagged for profanity")
      return review
  ```
- **Rationale**:
  - Lightweight (no ML dependencies), fast detection (<1ms for typical review)
  - Customizable word list (can add platform-specific words)
  - Sufficient for MVP (catches obvious profanity, manual reports handle edge cases)
  - Meets 1-second flagging requirement (detection synchronous during create/update)
- **Trade-offs**:
  - **Benefit**: Fast, simple integration, no heavy dependencies
  - **Compromise**: Less accurate than ML-based (false positives/negatives possible)
- **Follow-up**: Monitor false positive rate, add custom whitelist if needed

### Decision: Ownership Verification via FastAPI Dependency
- **Context**: Requirement 9 requires ownership verification for review update/delete
- **Alternatives Considered**:
  1. **FastAPI dependency** - Reusable, composable with get_current_user
  2. **Service method check** - Manual check in each service method
  3. **Decorator pattern** - Custom decorator for route handlers
- **Selected Approach**: FastAPI dependency (consistent with user-playlists pattern)
  ```python
  async def verify_review_ownership(
      review_id: int,
      current_user: User = Depends(get_current_user),
      db: AsyncSession = Depends(get_db),
  ) -> Review:
      review_repo = ReviewRepository(db)
      review = await review_repo.get_by_id(review_id)
      
      if not review:
          raise HTTPException(status_code=404, detail="Review not found")
      
      if review.user_id != current_user.id:
          raise HTTPException(
              status_code=403,
              detail="You do not own this review"
          )
      
      return review
  ```
- **Rationale**:
  - Consistent with verify_playlist_ownership from user-playlists module
  - FastAPI dependency injection provides clean, reusable pattern
  - Returns verified review to route handler (avoids duplicate query)
  - Easy to test (mock dependency in route tests)
- **Trade-offs**:
  - **Benefit**: Declarative, reusable, testable, consistent with existing patterns
  - **Compromise**: Extra database query to fetch review (acceptable 50-100ms)
- **Follow-up**: Consider caching review ownership for high-traffic scenarios

### Decision: Public Queries Filter Flagged Reviews (is_flagged = false)
- **Context**: Requirement 4 specifies flagged reviews should not display to public users
- **Alternatives Considered**:
  1. **Filter in query (WHERE is_flagged = false)** - Database-level filtering
  2. **Filter in application** - Fetch all, filter in Python (inefficient)
  3. **Soft delete flagged reviews** - Use deleted_at pattern (confuses deletion with moderation)
- **Selected Approach**: Filter in database query
  ```python
  async def get_reviews_for_song(song_id: int, page: int, page_size: int):
      query = (
          select(Review)
          .where(Review.song_id == song_id)
          .where(Review.is_flagged == False)  # Exclude flagged reviews
          .order_by(Review.created_at.desc())
          .limit(page_size)
          .offset((page - 1) * page_size)
      )
      result = await db.execute(query)
      return result.scalars().all()
  ```
- **Rationale**:
  - Database filtering most efficient (no wasted data transfer)
  - is_flagged boolean simple to understand (true = hidden, false = visible)
  - Admin queries can include flagged reviews (omit WHERE is_flagged = false)
  - Clear separation: public queries exclude flagged, admin queries include all
- **Trade-offs**:
  - **Benefit**: Efficient, clear logic, admin control
  - **Compromise**: Flagged reviews not deleted (remain in database for audit)
- **Follow-up**: Admin endpoints to review and approve/delete flagged content

## Risks & Mitigations

### Risk 1: Average Rating Inconsistency on Transaction Failure
- **Description**: If review create/update succeeds but average rating recalculation fails, songs table has stale rating
- **Impact**: Displayed average rating incorrect until next review mutation
- **Mitigation**:
  - Use database transaction for review mutation + average rating update (atomic)
  - Rollback both on failure (ensures consistency)
  - Alternative: PostgreSQL trigger recalculates automatically (future optimization)
  - Background job recalculates all average ratings nightly (reconciliation)

### Risk 2: Helpfulness Vote Count Drift from Race Conditions
- **Description**: Concurrent votes on same review may cause helpful_count incorrect due to race condition
- **Impact**: helpful_count slightly off (e.g., 42 instead of 43)
- **Mitigation**:
  - Use database transaction with row-level locking (SELECT FOR UPDATE) for vote operations
  - Alternative: Use PostgreSQL atomic increment (UPDATE reviews SET helpful_count = helpful_count + 1)
  - Monitor helpful_count accuracy (rarely critical, cosmetic drift acceptable)
  - Recalculation job corrects drift periodically (COUNT(*) from review_votes)

### Risk 3: Profanity Filter False Positives
- **Description**: better-profanity may flag legitimate reviews containing words with multiple meanings
- **Impact**: Valid reviews hidden from public, user frustration
- **Mitigation**:
  - Maintain custom whitelist for false positives (e.g., "Scunthorpe problem")
  - Manual review process: Admins can approve flagged reviews
  - User notification: "Your review is pending moderation" instead of silent hiding
  - Monitor false positive rate (review sample of flagged content weekly)

### Risk 4: Review Spam via Rapid Create/Update
- **Description**: User rapidly creates/updates reviews to abuse system (even with one-review-per-song limit)
- **Impact**: Database load, potential DoS
- **Mitigation**:
  - Rate limiting: Max 10 review mutations per minute per user (via slowapi from auth module)
  - Monitor mutation frequency per user (alert if >50 reviews/hour)
  - CAPTCHA for review creation (future: if abuse detected)
  - Account suspension for repeated abuse (manual moderation action)

### Risk 5: Review Text Storage Bloat
- **Description**: Reviews with 2000 characters each, 10k reviews per popular song = 20MB per song
- **Impact**: Database storage growth, query performance degradation
- **Mitigation**:
  - Pagination limits data transfer (default 10 reviews per page)
  - Index on (song_id, created_at DESC) optimizes recent review queries
  - Archive old reviews (>1 year) to separate table (future optimization)
  - Monitor database size growth (alert if >10GB for reviews table)

## References

### Official Documentation
- [SQLAlchemy Constraints](https://docs.sqlalchemy.org/en/20/core/constraints.html) - Unique constraints, CHECK constraints
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) - Dependency injection patterns
- [PostgreSQL Triggers](https://www.postgresql.org/docs/current/sql-createtrigger.html) - Automatic recalculation

### Python Libraries
- [better-profanity](https://pypi.org/project/better-profanity/) - Profanity filter library
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/) - Custom validation

### Design Patterns
- Repository Pattern - Data access abstraction
- Denormalization Pattern - Store calculated fields for performance

### Internal References
- `.sdd/steering/structure.md` - Backend structure patterns, database schema location
- `.sdd/steering/tech.md` - SQLAlchemy ORM, FastAPI async patterns, TDD requirements
- `.sdd/specs/auth-security-foundation/design.md` - JWT authentication, get_current_user dependency
- `.sdd/specs/music-catalog-management/design.md` - Song entity, soft delete pattern
- `.sdd/specs/user-playlists/design.md` - Ownership verification pattern
- `src/digital-music-store.sql` - Database schema (reviews table)
