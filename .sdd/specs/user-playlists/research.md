# Research & Design Decisions

## Summary
- **Feature**: `user-playlists`
- **Discovery Scope**: Extension (Integrates with existing catalog and auth systems)
- **Key Findings**:
  - SQLAlchemy association table pattern for many-to-many playlist-song relationships with position ordering
  - Ownership verification via JWT dependency injection reuses auth-security-foundation infrastructure
  - Position reordering requires transaction with row-level locking to prevent race conditions
  - Playlist-songs join table needs surrogate primary key (id) to support duplicate song instances
  - Pagination essential for playlists with 1000 songs (default 50/page, max 100/page)
  - Hard delete for playlists with CASCADE delete for playlist_songs join table entries

## Research Log

### SQLAlchemy Many-to-Many Association Table Pattern
- **Context**: Requirements specify many-to-many relationship between playlists and songs with position ordering and duplicate support
- **Sources Consulted**:
  - SQLAlchemy documentation (association tables, order_by)
  - Many-to-many patterns with additional data (position, timestamps)
  - Composite vs surrogate primary keys
- **Findings**:
  - **Association object pattern**: playlist_songs table with surrogate primary key (id) allows duplicate entries
  - **Position ordering**: Add position INTEGER field to association table, ordered by position ASC
  - **Surrogate key requirement**: Composite key (playlist_id, song_id) prevents duplicates; surrogate id column required
  - **SQLAlchemy relationship**: `relationship("Song", secondary="playlist_songs", order_by="playlist_songs.c.position")`
  - **Delete behavior**: Cascade delete on playlist removal deletes all playlist_songs entries
  - **Index strategy**: Index on (playlist_id, position) for efficient position lookups and reordering
- **Implications**:
  - playlist_songs table schema: `id SERIAL PRIMARY KEY, playlist_id INT, song_id INT, position INT, created_at TIMESTAMPTZ`
  - Foreign keys: playlist_id → playlists.id ON DELETE CASCADE, song_id → songs.id ON DELETE RESTRICT
  - Repository method for adding song: Find max(position) + 1, insert with next position
  - Remove song: Delete by id (specific instance), then reorder remaining positions

### Position Reordering Transaction Safety
- **Context**: Requirement 7 specifies song reordering within playlist with gap-free sequential positions
- **Sources Consulted**:
  - PostgreSQL transaction isolation levels
  - Row-level locking strategies (SELECT FOR UPDATE)
  - Race condition prevention in position updates
- **Findings**:
  - **Race condition risk**: Two concurrent reorder requests can create position conflicts or gaps
  - **Row-level locking**: Use `SELECT ... FOR UPDATE` to lock playlist_songs rows during reorder transaction
  - **Reorder algorithm**:
    1. Lock all playlist_songs for playlist (SELECT FOR UPDATE)
    2. Move target song to new position
    3. Shift other songs up/down to fill gap and make room
    4. Commit transaction (releases locks)
  - **Alternative approach**: Use fractional positions (1.0, 1.5, 2.0) to avoid full reorder, but adds complexity
  - **PostgreSQL transaction isolation**: READ COMMITTED sufficient (default), SERIALIZABLE overkill
- **Implications**:
  - Use database transaction with row-level locking for reorder operations
  - SQLAlchemy: `async with session.begin()` for transaction, `query.with_for_update()` for locking
  - Reorder endpoint may take 200-300ms for large playlists (acceptable per performance requirement)
  - Monitor deadlock potential (unlikely with single-playlist locking)

### Ownership Verification via JWT Dependency Injection
- **Context**: Requirement 10 requires ownership verification for all playlist mutations
- **Sources Consulted**:
  - FastAPI dependency injection patterns
  - auth-security-foundation design (get_current_user dependency)
  - Authorization vs authentication separation
- **Findings**:
  - **Reuse auth dependencies**: get_current_user from auth-security-foundation extracts user from JWT
  - **Custom dependency pattern**: Create `verify_playlist_ownership(playlist_id, current_user)` dependency
  - **Dependency composition**: Combine get_current_user + verify_playlist_ownership for protected routes
  - **Error handling**: Raise HTTPException(403) if owner_user_id != current_user.id
  - **Path parameter access**: Dependencies can access path parameters via Depends pattern
- **Implications**:
  - Define verify_playlist_ownership dependency in playlists module
  - All mutation endpoints (update, delete, add_song, remove_song, reorder) use dependency
  - Read endpoints (get playlist by ID) check ownership only for private playlists
  - No need for separate OwnershipService class (FastAPI dependencies sufficient)

### Duplicate Song Handling with Surrogate Keys
- **Context**: Requirement 12 allows same song multiple times in playlist
- **Sources Consulted**:
  - Database normalization principles
  - Surrogate vs natural keys
  - Join table design patterns
- **Findings**:
  - **Surrogate key pattern**: playlist_songs.id as PRIMARY KEY enables duplicate (playlist_id, song_id) pairs
  - **Natural key limitation**: Composite key (playlist_id, song_id) enforces uniqueness, prevents duplicates
  - **Removal by instance**: DELETE by playlist_songs.id removes specific instance, not all instances of song
  - **Query duplicates**: `SELECT song_id, COUNT(*) FROM playlist_songs WHERE playlist_id = ? GROUP BY song_id HAVING COUNT(*) > 1`
  - **Position uniqueness**: position should be unique per playlist but not enforced by constraint (reordering complexity)
- **Implications**:
  - Use SERIAL id column as primary key in playlist_songs table
  - Remove composite unique constraint on (playlist_id, song_id)
  - API responses include playlist_song_id for removal operations
  - Frontend displays unique identifier per playlist entry (not just song_id)

### Pagination Strategy for Large Playlists
- **Context**: Requirement 9 supports playlists up to 1000 songs, requires pagination
- **Sources Consulted**:
  - FastAPI pagination patterns
  - music-catalog-management research (offset-based pagination)
  - Large dataset performance considerations
- **Findings**:
  - **Offset-based pagination**: `LIMIT page_size OFFSET (page-1)*page_size` simple for MVP
  - **Default page size**: 50 songs (balances UX and performance)
  - **Maximum page size**: 100 songs (prevent excessive data transfer)
  - **Song count included**: Playlist response includes total_songs_count for pagination calculation
  - **Cursor-based future**: For playlists >1000 songs, cursor-based pagination more performant (deferred)
  - **Position ordering**: Always order by position ASC, pagination applies after ordering
- **Implications**:
  - Playlist detail endpoint: `GET /playlists/{id}?page=1&page_size=50`
  - Response includes: songs (paginated), total_songs_count, page, page_size, total_pages
  - Default behavior: Return first 50 songs if no pagination params provided
  - Monitor performance at 1000 song threshold (may need optimization)

### Foreign Key Cascade and Referential Integrity
- **Context**: Requirements specify playlist deletion removes all songs, song deletion affects playlists
- **Sources Consulted**:
  - music-catalog-management research (cascade rules)
  - PostgreSQL foreign key options
  - Data integrity trade-offs
- **Findings**:
  - **Playlist deletion**: ON DELETE CASCADE for playlist_songs (delete playlist removes all entries)
  - **Song deletion**: ON DELETE RESTRICT for playlist_songs.song_id (prevent song deletion if in playlists)
    - **Alternative**: ON DELETE CASCADE removes song from all playlists (destructive)
    - **Conflict with soft delete**: Songs use soft delete (deleted_at), so CASCADE not triggered
  - **Soft delete interaction**: Soft-deleted songs remain in playlist_songs table but excluded from queries
  - **User deletion**: ON DELETE CASCADE for playlists.owner_user_id (delete user removes all playlists)
- **Implications**:
  - playlist_songs.playlist_id: `REFERENCES playlists(id) ON DELETE CASCADE`
  - playlist_songs.song_id: `REFERENCES songs(id) ON DELETE RESTRICT`
  - Queries filter out soft-deleted songs: `JOIN songs WHERE songs.deleted_at IS NULL`
  - Admin cleanup job (future): Remove playlist_songs entries for soft-deleted songs

### Calculated Fields Performance
- **Context**: Requirement 2 includes total_duration_seconds and songs_count in playlist responses
- **Sources Consulted**:
  - PostgreSQL aggregate functions
  - SQLAlchemy hybrid properties
  - Computed columns vs on-demand calculation
- **Findings**:
  - **On-demand calculation**: Calculate sum/count in SELECT query (no stored column)
  - **SQLAlchemy hybrid_property**: Define `@hybrid_property` on Playlist model for total_duration, songs_count
  - **Query optimization**: Use `func.sum()` and `func.count()` with LEFT JOIN to playlist_songs + songs
  - **Caching consideration**: For large playlists (1000 songs), caching total_duration reduces recalculation
  - **Incremental update**: Alternative stores counts/totals in playlist table, updated on add/remove (complex, prone to drift)
- **Implications**:
  - Calculate total_duration_seconds and songs_count in repository query (JOIN + aggregate)
  - No stored columns in playlists table (avoid data duplication)
  - Consider Redis caching for playlist metadata (total_duration, songs_count) in future optimization
  - Monitor query performance for 1000-song playlists (should meet 500ms requirement)

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| **Repository Pattern (Selected)** | Separate data access layer with PlaylistRepository | Consistent with music-catalog, testable, clear boundaries | Extra abstraction layer | Aligns with existing architecture |
| Service-Only | Combine business logic and data access in PlaylistService | Less boilerplate, faster development | Tight coupling, harder to test | Not recommended for CRUD with complex logic |
| CQRS-Lite | Separate read/write models (PlaylistCommandService, PlaylistQueryService) | Optimized queries, clear intent | Overkill for playlist CRUD | Future consideration if read/write patterns diverge |

**Selected**: Repository Pattern
- Consistent with music-catalog-management and auth-security-foundation
- Clean separation: Service (business logic) → Repository (data access)
- Testable: Mock repository in unit tests, real DB in integration tests
- Enables future caching layer between service and repository

## Design Decisions

### Decision: Association Table with Surrogate Primary Key
- **Context**: Requirement 12 allows duplicate songs in playlists, requiring many-to-many with position ordering
- **Alternatives Considered**:
  1. **Surrogate key (id)** - Allows duplicates, supports per-instance removal
  2. **Composite key (playlist_id, song_id)** - Enforces uniqueness, prevents duplicates
  3. **Composite key + occurrence count** - Track count field, complex to manage
- **Selected Approach**: Surrogate primary key (id) with position ordering
  ```sql
  CREATE TABLE playlist_songs (
    id SERIAL PRIMARY KEY,
    playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    song_id INTEGER NOT NULL REFERENCES songs(id) ON DELETE RESTRICT,
    position INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
  );
  CREATE INDEX idx_playlist_songs_playlist_position ON playlist_songs(playlist_id, position);
  ```
- **Rationale**:
  - Surrogate key enables multiple instances of same song in playlist
  - position field provides explicit ordering (not relying on id sequence)
  - ON DELETE CASCADE simplifies playlist deletion (removes all songs)
  - Index on (playlist_id, position) optimizes position-based queries
- **Trade-offs**:
  - **Benefit**: Flexible duplicate handling, simple removal by id
  - **Compromise**: Larger table (extra id column), no constraint preventing duplicates
- **Follow-up**: Monitor position uniqueness (should be unique per playlist, enforced by application logic)

### Decision: Ownership Verification via FastAPI Dependency
- **Context**: Requirement 10 requires ownership verification for all mutations
- **Alternatives Considered**:
  1. **FastAPI dependency** - Reusable, composable with get_current_user
  2. **Service method check** - Manual check in each service method
  3. **Database trigger** - Enforce at DB level (overkill, adds latency)
- **Selected Approach**: Custom FastAPI dependency
  ```python
  async def verify_playlist_ownership(
      playlist_id: int,
      current_user: User = Depends(get_current_user),
      db: AsyncSession = Depends(get_db)
  ) -> Playlist:
      playlist = await PlaylistRepository.get_by_id(playlist_id)
      if not playlist:
          raise HTTPException(status_code=404, detail="Playlist not found")
      if playlist.owner_user_id != current_user.id:
          raise HTTPException(status_code=403, detail="You do not own this playlist")
      return playlist
  ```
- **Rationale**:
  - FastAPI dependency injection provides clean, reusable pattern
  - Composes with get_current_user from auth-security-foundation
  - Single source of truth for ownership verification
  - Easy to test (mock dependency in route tests)
- **Trade-offs**:
  - **Benefit**: Declarative, reusable, testable
  - **Compromise**: Extra database query to fetch playlist (can be optimized with caching)
- **Follow-up**: Consider caching playlist ownership in Redis for high-traffic scenarios

### Decision: Position Reordering with Row-Level Locking
- **Context**: Requirement 7 requires safe song reordering with gap-free positions
- **Alternatives Considered**:
  1. **Row-level locking** - Lock rows during transaction, safe but slower
  2. **Optimistic locking** - Version field, retry on conflict (complex)
  3. **Fractional positions** - Use floats (1.0, 1.5, 2.0) to avoid full reorder (drift risk)
- **Selected Approach**: Row-level locking with transaction
  ```python
  async def reorder_song(playlist_id: int, playlist_song_id: int, new_position: int):
      async with session.begin():
          # Lock all playlist_songs for this playlist
          songs = await session.execute(
              select(PlaylistSong)
              .where(PlaylistSong.playlist_id == playlist_id)
              .order_by(PlaylistSong.position)
              .with_for_update()
          )
          # Move target song to new position, shift others
          # Algorithm: remove from old position, insert at new position, renumber
          await session.commit()
  ```
- **Rationale**:
  - Row-level locking prevents race conditions (two concurrent reorders)
  - PostgreSQL `SELECT FOR UPDATE` locks rows until transaction commits
  - Algorithm ensures gap-free positions (1, 2, 3, ..., N)
  - Meets 200ms performance requirement for playlists up to 1000 songs
- **Trade-offs**:
  - **Benefit**: Safe, consistent, meets performance requirements
  - **Compromise**: Serializes concurrent reorder requests (rare edge case)
- **Follow-up**: Monitor for deadlocks (unlikely, single-playlist scope), add retry logic if needed

### Decision: Soft-Deleted Songs Excluded from Playlist Queries
- **Context**: music-catalog-management uses soft delete for songs, playlists must handle gracefully
- **Alternatives Considered**:
  1. **Exclude soft-deleted songs** - Filter in query (WHERE deleted_at IS NULL)
  2. **Show as unavailable** - Display grayed-out songs with "Unavailable" label
  3. **Cascade soft delete** - When song soft-deleted, remove from all playlists
- **Selected Approach**: Exclude soft-deleted songs from playlist queries
  ```sql
  SELECT ps.*, s.title, s.duration_seconds, a.title AS album_title, ar.name AS artist_name
  FROM playlist_songs ps
  JOIN songs s ON ps.song_id = s.id
  JOIN albums a ON s.album_id = a.id
  JOIN artists ar ON a.artist_id = ar.id
  WHERE ps.playlist_id = ?
    AND s.deleted_at IS NULL  -- Filter soft-deleted songs
  ORDER BY ps.position ASC
  ```
- **Rationale**:
  - Soft-deleted songs should not appear in playlist (catalog removed them)
  - Simpler UX than showing "Unavailable" songs
  - playlist_songs entries remain in database (audit trail) but not displayed
  - songs_count reflects only active songs (not including soft-deleted)
- **Trade-offs**:
  - **Benefit**: Clean UX, respects catalog soft delete
  - **Compromise**: Playlist positions have gaps if songs soft-deleted (acceptable, reordering fills gaps)
- **Follow-up**: Admin cleanup job (future) to remove playlist_songs entries for old soft-deleted songs

### Decision: Pagination with Default 50 Songs, Max 100
- **Context**: Requirement 9 supports playlists up to 1000 songs, requires pagination
- **Alternatives Considered**:
  1. **Offset-based (default 50, max 100)** - Simple, meets requirements
  2. **Cursor-based** - More scalable for very large playlists (future)
  3. **Load all songs** - Simple but fails performance requirement for 1000 songs
- **Selected Approach**: Offset-based pagination
  ```python
  GET /playlists/{id}?page=1&page_size=50
  
  Response:
  {
    "id": 123,
    "title": "My Playlist",
    "songs": [...],  # 50 songs
    "total_songs_count": 234,
    "page": 1,
    "page_size": 50,
    "total_pages": 5
  }
  ```
- **Rationale**:
  - Offset pagination simple, supported by SQLAlchemy (LIMIT/OFFSET)
  - Default 50 songs balances UX (reasonable load time) and API calls
  - Max 100 songs prevents excessive data transfer
  - Meets 500ms performance requirement for 1000-song playlists
- **Trade-offs**:
  - **Benefit**: Simple implementation, meets requirements
  - **Compromise**: Performance degrades for high page numbers (page 20 of 1000 songs slower)
- **Follow-up**: Monitor pagination query latency, migrate to cursor-based if >500ms p95

### Decision: Hard Delete for Playlists (No Soft Delete)
- **Context**: Requirement 4 specifies hard delete for playlists (not soft delete like songs)
- **Alternatives Considered**:
  1. **Hard delete** - Remove playlist and playlist_songs entries (via CASCADE)
  2. **Soft delete** - Add deleted_at column, filter in queries (consistent with songs)
  3. **Archival** - Move to archived_playlists table (complex, not required)
- **Selected Approach**: Hard delete with CASCADE
  ```sql
  DELETE FROM playlists WHERE id = ?;
  -- CASCADE automatically deletes all playlist_songs entries
  ```
- **Rationale**:
  - Requirements explicitly specify hard delete (Requirement 4.7)
  - Playlists are user-owned, not shared catalog data (unlike songs)
  - No audit trail required for deleted playlists (user choice)
  - Simpler than soft delete (no deleted_at filtering needed)
- **Trade-offs**:
  - **Benefit**: Simple, meets requirements, CASCADE simplifies deletion
  - **Compromise**: No recovery after deletion (add confirmation UI to prevent accidents)
- **Follow-up**: Frontend confirms deletion with "Are you sure?" dialog, mention no recovery

## Risks & Mitigations

### Risk 1: Position Gaps from Soft-Deleted Songs
- **Description**: When songs are soft-deleted, playlist_songs entries remain but excluded from queries, creating position gaps
- **Impact**: Playlist positions non-sequential (e.g., 1, 2, 5, 7 instead of 1, 2, 3, 4)
- **Mitigation**:
  - Accept gaps in position numbering (application logic handles gaps gracefully)
  - Reorder operation renumbers all positions to fill gaps (1, 2, 3, ...)
  - Alternative: Background job removes playlist_songs for soft-deleted songs >30 days old
  - Document gap handling in component implementation notes

### Risk 2: Race Conditions in Concurrent Playlist Modifications
- **Description**: Two users adding songs or reordering simultaneously may cause position conflicts or duplicate positions
- **Impact**: Position uniqueness violation, incorrect song order
- **Mitigation**:
  - Use database transactions with row-level locking (SELECT FOR UPDATE)
  - Pessimistic locking prevents concurrent modifications to same playlist
  - Add retry logic for deadlocks (unlikely but possible)
  - Monitor deadlock frequency in production (alert if >1% of requests)

### Risk 3: Performance Degradation with 1000-Song Playlists
- **Description**: Queries joining playlist_songs + songs + albums + artists for 1000 songs may exceed 500ms
- **Impact**: Poor UX for users with large playlists
- **Mitigation**:
  - Implement pagination (default 50 songs per page)
  - Index on (playlist_id, position) for efficient position-based queries
  - Monitor query latency with APM (alert if p95 >500ms)
  - Future optimization: Cache playlist metadata (songs_count, total_duration) in Redis
  - Future optimization: Cursor-based pagination for very large playlists

### Risk 4: Ownership Verification Extra Database Query
- **Description**: verify_playlist_ownership dependency fetches playlist to check owner, adds latency
- **Impact**: Extra 50-100ms per request for ownership verification
- **Mitigation**:
  - Acceptable for MVP (total latency still <300ms per requirement)
  - Optimize: Cache playlist ownership in Redis (TTL 5 minutes)
  - Optimize: Include owner_user_id in JWT token custom claims (avoids DB query, requires auth changes)
  - Monitor latency impact (measure with/without caching)

### Risk 5: Duplicate Song Count Confusion
- **Description**: Users may not realize same song appears multiple times in playlist, confusion during removal
- **Impact**: User removes wrong instance, unexpected playlist state
- **Mitigation**:
  - UI shows playlist_song_id (not just song_id) for removal operations
  - UI displays duplicate indicator (e.g., "Added 2x" badge)
  - API response includes position field for disambiguation
  - Removal endpoint requires playlist_song_id (specific instance), not song_id

## References

### Official Documentation
- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/20/orm/relationships.html) - Many-to-many, association tables
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) - Dependency injection, reusable dependencies
- [PostgreSQL Foreign Keys](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK) - CASCADE options

### Design Patterns
- Repository Pattern - Data access abstraction
- Association Object Pattern - Many-to-many with additional data

### Internal References
- `.sdd/steering/structure.md` - Backend structure patterns, database schema location
- `.sdd/steering/tech.md` - SQLAlchemy ORM, FastAPI async patterns, TDD requirements
- `.sdd/specs/auth-security-foundation/design.md` - JWT authentication, get_current_user dependency
- `.sdd/specs/music-catalog-management/design.md` - Soft delete pattern, pagination strategy
- `src/digital-music-store.sql` - Database schema (playlists table)
