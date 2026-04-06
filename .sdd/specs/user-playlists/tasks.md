# Implementation Tasks

## Overview
Implementation tasks for User-Playlists module following Test-Driven Development (TDD) methodology. This feature enables authenticated users to create and manage personalized music collections with song reordering, privacy controls (public/private), and support for up to 1000 songs per playlist. All tasks follow Red-Green-Refactor cycle: write failing test first, implement minimal code to pass, then refactor while keeping tests green.

## Task Breakdown

- [x] 1. Database schema and models setup
- [x] 1.1 (P) Create database migration for playlists table
  - Create migration file with playlists table: id (SERIAL primary key), title (varchar 200 NOT NULL), owner_user_id (integer foreign key to users.id ON DELETE CASCADE), is_public (boolean default FALSE), created_at (timestamptz default NOW), updated_at (timestamptz default NOW)
  - Add index on owner_user_id for querying user's playlists
  - Add partial index on is_public WHERE is_public = TRUE for public playlist queries
  - Add NOT NULL constraints on title and owner_user_id
  - _Requirements: 1, 8_

- [x] 1.2 (P) Create database migration for playlist_songs join table
  - Create migration file with playlist_songs table: id (SERIAL primary key), playlist_id (integer foreign key to playlists.id ON DELETE CASCADE), song_id (integer foreign key to songs.id ON DELETE RESTRICT), position (integer NOT NULL), created_at (timestamptz default NOW)
  - Add composite index on (playlist_id, position) for position-based queries and reordering
  - Add index on song_id for reverse lookups
  - Do NOT add unique constraint on (playlist_id, song_id) to allow duplicate songs
  - Add NOT NULL constraints on playlist_id, song_id, position
  - _Requirements: 5, 12_

- [x] 1.3 Define Playlist and PlaylistSong models
  - Write failing tests for Playlist model with all fields, relationships to User and PlaylistSong
  - Create Playlist SQLAlchemy model with owner relationship, playlist_songs relationship (cascade all, delete-orphan), lazy selectinload
  - Define PlaylistSong SQLAlchemy model with playlist relationship, song relationship
  - Implement __repr__ methods for debugging
  - Verify cascade deletion: deleting playlist removes all playlist_songs entries
  - _Requirements: 1, 4, 5_

- [x] 2. Validation and schema definitions
- [x] 2.1 (P) Define Pydantic request schemas with validation
  - Write failing tests for PlaylistCreateRequest schema validation (title 1-200 chars, is_public boolean optional)
  - Create PlaylistCreateRequest schema with title validation (min_length=1, max_length=200), is_public default False
  - Create PlaylistUpdateRequest schema with optional title and is_public fields
  - Create AddSongRequest schema with song_id integer
  - Create ReorderSongRequest schema with new_position integer validation (ge=1)
  - Implement custom validators to trim whitespace from title and reject whitespace-only strings
  - _Requirements: 1, 3, 5, 7, 8_

- [x] 2.2 (P) Define Pydantic response schemas
  - Define PlaylistResponse schema with id, title, owner_user_id, is_public, songs_count, total_duration_seconds, created_at, updated_at
  - Define PlaylistSongResponse schema with playlist_song_id, position, song_id, song_title, artist_name, album_title, duration_seconds
  - Define PlaylistListResponse schema with items array, total count, page, page_size, total_pages
  - Include proper JSON serialization for datetime fields
  - _Requirements: 2, 11_

- [x] 3. Repository layer implementation
- [x] 3.1 Implement PlaylistRepository for data access
  - Write failing tests for PlaylistRepository.create with title, owner_user_id, is_public parameters
  - Implement create method inserting playlist record with timestamps
  - Write failing tests for PlaylistRepository.get_by_id with optional eager loading of songs
  - Implement get_by_id method with selectinload for playlist_songs relationship
  - Write failing tests for PlaylistRepository.get_by_owner with pagination
  - Implement get_by_owner method querying WHERE owner_user_id = ? with LIMIT/OFFSET pagination
  - Write failing tests for PlaylistRepository.get_public with pagination
  - Implement get_public method querying WHERE is_public = TRUE with pagination
  - Write failing tests for PlaylistRepository.update with optional title and is_public
  - Implement update method updating fields and updated_at timestamp
  - Write failing tests for PlaylistRepository.delete performing hard delete
  - Implement delete method removing playlist record (CASCADE deletes playlist_songs automatically)
  - _Requirements: 1, 2, 3, 4, 8_

- [x] 3.2 Implement PlaylistSongRepository for join table access
  - Write failing tests for PlaylistSongRepository.add_song assigning next position (max + 1)
  - Implement add_song method querying max position, creating playlist_song with position = max + 1
  - Allow duplicate songs by using surrogate key (no uniqueness constraint)
  - Write failing tests for PlaylistSongRepository.remove_song by playlist_song_id
  - Implement remove_song method deleting playlist_song entry, calling _reorder_positions to fill gaps
  - Write failing tests for PlaylistSongRepository.get_songs with pagination and soft-delete filtering
  - Implement get_songs method joining with songs, albums, artists WHERE deleted_at IS NULL, order by position ASC
  - Return full song details: playlist_song_id, position, song_id, song_title, artist_name, album_title, duration_seconds
  - Write failing tests for PlaylistSongRepository.get_max_position
  - Implement get_max_position method returning max(position) for playlist
  - _Requirements: 5, 6, 11, 12_

- [x] 3.3 Implement PlaylistSongRepository reordering logic
  - Write failing tests for PlaylistSongRepository.reorder_song moving song to new position
  - Implement reorder_song method with transaction: BEGIN, SELECT ... FOR UPDATE (row-level locking), remove target from list, insert at new position, renumber all positions sequentially (1, 2, 3, ...), COMMIT
  - Write failing tests for _reorder_positions filling gaps after removal
  - Implement _reorder_positions internal method querying playlist_songs ORDER BY position, renumbering sequentially
  - Handle edge cases: new_position == old_position (no-op), new_position out of bounds (raise ValueError)
  - _Requirements: 6, 7_

- [x] 4. Business logic services
- [x] 4.1 Implement PlaylistService for CRUD operations
  - Write failing tests for PlaylistService.create_playlist with title validation (1-200 chars)
  - Implement create_playlist validating title length, calling PlaylistRepository.create with owner_user_id, default is_public=False
  - Write failing tests for PlaylistService.get_playlist_by_id with privacy enforcement (private → owner only)
  - Implement get_playlist_by_id fetching playlist, checking if private and current_user_id != owner_user_id (raise 403)
  - Calculate songs_count and total_duration_seconds from playlist_songs relationship
  - Write failing tests for PlaylistService.get_user_playlists with pagination
  - Implement get_user_playlists calling PlaylistRepository.get_by_owner with page, page_size (default 20)
  - Write failing tests for PlaylistService.get_public_playlists with pagination
  - Implement get_public_playlists calling PlaylistRepository.get_public with pagination
  - _Requirements: 1, 2, 8_

- [x] 4.2 Implement PlaylistService for update and delete
  - Write failing tests for PlaylistService.update_playlist with optional title and is_public
  - Implement update_playlist validating title if provided (1-200 chars), calling PlaylistRepository.update
  - Update updated_at timestamp on changes
  - Write failing tests for PlaylistService.delete_playlist performing hard delete
  - Implement delete_playlist calling PlaylistRepository.delete (CASCADE removes playlist_songs)
  - Return 204 No Content on successful deletion
  - _Requirements: 3, 4_

- [x] 4.3 Implement PlaylistService for song management
  - Write failing tests for PlaylistService.add_song_to_playlist validating song exists in catalog
  - Implement add_song_to_playlist checking song_id exists via music-catalog SongRepository, calling PlaylistSongRepository.add_song
  - Check songs_count >= 1000, log warning if exceeded but still allow creation
  - Return updated playlist with new song included
  - Write failing tests for PlaylistService.remove_song_from_playlist by playlist_song_id
  - Implement remove_song_from_playlist calling PlaylistSongRepository.remove_song (specific instance, not all)
  - Positions reordered automatically by repository
  - Return updated playlist after removal
  - _Requirements: 5, 6, 9_

- [x] 4.4 Implement PlaylistService for song reordering
  - Write failing tests for PlaylistService.reorder_song with new_position validation (1 to songs_count)
  - Implement reorder_song validating new_position bounds, calling PlaylistSongRepository.reorder_song
  - Handle transaction with row-level locking to prevent concurrent conflicts
  - Verify positions sequential (1, 2, 3, ...) after reorder
  - Return updated playlist with songs in new order
  - Return 400 Bad Request if new_position out of bounds
  - _Requirements: 7_

- [x] 5. Ownership verification dependency
- [x] 5.1 (P) Implement verify_playlist_ownership FastAPI dependency
  - Write failing tests for verify_playlist_ownership with owner scenario (returns playlist)
  - Create verify_playlist_ownership dependency function taking playlist_id, current_user (Depends on get_current_user), db (AsyncSession)
  - Query playlist from PlaylistRepository by ID
  - Write failing tests for non-owner scenario (raises 403 Forbidden)
  - Compare playlist.owner_user_id with current_user.id, raise HTTPException(403, "You do not own this playlist") if mismatch
  - Write failing tests for non-existent playlist (raises 404 Not Found)
  - Raise HTTPException(404, "Playlist not found") if playlist is None
  - Return verified playlist to route handler (avoids duplicate query)
  - _Requirements: 3, 4, 5, 6, 7, 10_

- [x] 6. API routes and endpoints
- [x] 6.1 Implement POST /playlists endpoint for playlist creation
  - Write failing integration tests for POST /playlists with valid data (returns 201 Created with playlist details)
  - Create POST /playlists route with get_current_user dependency for authentication
  - Validate request using PlaylistCreateRequest schema
  - Call PlaylistService.create_playlist with title, is_public, current_user.id
  - Return 201 Created with PlaylistResponse
  - Write failing tests for unauthenticated request (returns 401 Unauthorized)
  - Write failing tests for invalid title (empty or >200 chars returns 400 Bad Request)
  - _Requirements: 1_

- [x] 6.2 Implement GET /playlists/{id} endpoint for playlist retrieval
  - Write failing integration tests for GET /playlists/{id} with owner scenario (returns 200 OK with full details)
  - Create GET /playlists/{id} route accepting optional page and page_size query parameters (default 50, max 100)
  - Call PlaylistService.get_playlist_by_id with playlist_id and current_user_id (optional)
  - Return 200 OK with PlaylistResponse including paginated songs
  - Write failing tests for private playlist accessed by non-owner (returns 403 Forbidden)
  - Write failing tests for public playlist accessed by guest (returns 200 OK)
  - Write failing tests for non-existent playlist (returns 404 Not Found)
  - Exclude soft-deleted songs from playlist_songs results (WHERE deleted_at IS NULL)
  - _Requirements: 2, 11_

- [x] 6.3 Implement GET /users/me/playlists endpoint
  - Write failing integration tests for GET /users/me/playlists with authenticated user (returns 200 OK with paginated playlists)
  - Create GET /users/me/playlists route with get_current_user dependency
  - Accept optional page and page_size query parameters (default 20)
  - Call PlaylistService.get_user_playlists with current_user.id and pagination
  - Return 200 OK with PlaylistListResponse (items, total, page, page_size, total_pages)
  - Write failing tests for unauthenticated request (returns 401 Unauthorized)
  - _Requirements: 2_

- [x] 6.4 (P) Implement GET /playlists/public endpoint
  - Write failing integration tests for GET /playlists/public with guest user (returns 200 OK with public playlists)
  - Create GET /playlists/public route (no authentication required)
  - Accept optional page and page_size query parameters (default 20)
  - Call PlaylistService.get_public_playlists with pagination
  - Return 200 OK with PlaylistListResponse
  - Only playlists with is_public=TRUE returned
  - _Requirements: 2, 8_

- [x] 6.5 Implement PUT /playlists/{id} endpoint for playlist update
  - Write failing integration tests for PUT /playlists/{id} with owner updating title (returns 200 OK)
  - Create PUT /playlists/{id} route with verify_playlist_ownership dependency
  - Validate request using PlaylistUpdateRequest schema
  - Call PlaylistService.update_playlist with optional title and is_public
  - Return 200 OK with updated PlaylistResponse
  - Write failing tests for non-owner attempt (returns 403 Forbidden via dependency)
  - Write failing tests for invalid title (returns 400 Bad Request)
  - Updated_at timestamp updated on changes
  - _Requirements: 3, 8, 10_

- [x] 6.6 Implement DELETE /playlists/{id} endpoint
  - Write failing integration tests for DELETE /playlists/{id} with owner deletion (returns 204 No Content)
  - Create DELETE /playlists/{id} route with verify_playlist_ownership dependency
  - Call PlaylistService.delete_playlist
  - Return 204 No Content on successful deletion
  - Write failing tests for non-owner attempt (returns 403 Forbidden via dependency)
  - Write failing tests for non-existent playlist (returns 404 Not Found)
  - Verify CASCADE deletes all playlist_songs entries
  - _Requirements: 4, 10_

- [x] 6.7 Implement POST /playlists/{id}/songs endpoint for adding songs
  - Write failing integration tests for POST /playlists/{id}/songs with valid song_id (returns 200 OK)
  - Create POST /playlists/{id}/songs route with verify_playlist_ownership dependency
  - Validate request using AddSongRequest schema
  - Call PlaylistService.add_song_to_playlist with playlist_id and song_id
  - Return 200 OK with updated PlaylistResponse
  - Write failing tests for invalid song_id (returns 400 Bad Request "Song not found")
  - Write failing tests for non-owner attempt (returns 403 Forbidden)
  - Allow duplicate songs (same song_id added multiple times)
  - Position assigned automatically (max + 1)
  - _Requirements: 5, 10, 12_

- [x] 6.8 Implement DELETE /playlists/{id}/songs/{playlist_song_id} endpoint
  - Write failing integration tests for DELETE /playlists/{id}/songs/{playlist_song_id} with owner (returns 200 OK)
  - Create DELETE /playlists/{id}/songs/{playlist_song_id} route with verify_playlist_ownership dependency
  - Call PlaylistService.remove_song_from_playlist with playlist_song_id
  - Return 200 OK with updated PlaylistResponse
  - Write failing tests for non-existent playlist_song_id (returns 404 Not Found)
  - Write failing tests for non-owner attempt (returns 403 Forbidden)
  - Verify positions reordered to fill gaps after removal
  - Remove specific instance (not all instances of same song)
  - _Requirements: 6, 10_

- [x] 6.9 Implement PATCH /playlists/{id}/songs/{playlist_song_id}/reorder endpoint
  - Write failing integration tests for PATCH /playlists/{id}/songs/{playlist_song_id}/reorder with new_position (returns 200 OK)
  - Create PATCH /playlists/{id}/songs/{playlist_song_id}/reorder route with verify_playlist_ownership dependency
  - Validate request using ReorderSongRequest schema
  - Call PlaylistService.reorder_song with playlist_id, playlist_song_id, new_position
  - Return 200 OK with updated PlaylistResponse
  - Write failing tests for new_position out of bounds (returns 400 Bad Request)
  - Write failing tests for non-owner attempt (returns 403 Forbidden)
  - Verify positions sequential (1, 2, 3, ...) after reorder
  - Handle concurrent reorder requests with row-level locking (transaction isolation)
  - _Requirements: 7, 10_

- [x] 7. Integration and end-to-end testing
- [x] 7.1* Test complete playlist lifecycle flow
  - Write integration test for full playlist lifecycle: create playlist → add 3 songs → reorder song (move position 3 to 1) → remove song → toggle privacy (private to public) → delete playlist
  - Verify positions sequential at each step (1, 2, 3, ...)
  - Verify CASCADE deletion removes all playlist_songs entries
  - Test with multiple users: owner can mutate, non-owner receives 403 Forbidden
  - _Requirements: 1, 2, 3, 4, 5, 6, 7, 8, 10_

- [x] 7.2* Test playlist privacy enforcement
  - Write integration test for privacy control: owner creates private playlist → guest attempts access (403 Forbidden) → owner toggles to public → guest accesses successfully (200 OK)
  - Test public playlist listing: create 5 playlists (3 public, 2 private) → GET /playlists/public returns only 3 public playlists
  - Verify default privacy is private (is_public=false) for new playlists
  - _Requirements: 2, 8_

- [x] 7.3* Test duplicate song handling
  - Write integration test for duplicate songs: add same song 3 times → verify 3 distinct playlist_song entries with different IDs and positions
  - Remove 1 instance → verify 2 remaining instances
  - Reorder 1 instance → verify only that instance moves, others unaffected
  - Query song count per playlist: verify 3 instances counted correctly
  - _Requirements: 5, 6, 12_

- [x] 7.4* Test soft-deleted song exclusion
  - Write integration test for soft-delete handling: add 3 songs to playlist → admin soft-deletes 1 song (sets deleted_at) → retrieve playlist → verify deleted song excluded from results
  - Verify songs_count decremented after soft-delete
  - Verify total_duration_seconds excludes deleted song duration
  - Verify positions NOT reordered (gaps allowed if song soft-deleted)
  - _Requirements: 11_

- [x] 7.5* Test playlist song limit and pagination
  - Write integration test for 1000-song playlist: add 1000 songs → verify warning logged → add 1001st song → verify still allowed but warning logged
  - Test pagination with 1000-song playlist: retrieve page 1 (50 songs) → verify <500ms response time → retrieve page 20 (last page) → verify <500ms response time
  - Test page_size limits: default 50, max 100 → request page_size=150 → verify capped at 100
  - _Requirements: 9_

- [x] 7.6* Test performance requirements
  - Write performance tests for playlist CRUD operations: create, update, delete → verify all complete within 300ms (p95)
  - Test add/remove song operations: add song, remove song → verify both complete within 200ms (p95)
  - Test reorder operation with 1000-song playlist: move song from position 500 to position 1 → verify completes within 300ms
  - Test concurrent reorder requests: 10 simultaneous reorder requests to same playlist → verify no deadlocks, sequential processing with row-level locking
  - _Requirements: 1, 3, 4, 5, 6, 7_

## Notes
- All tasks follow TDD methodology: Write failing test (Red) → Implement minimal code (Green) → Refactor while keeping tests green
- Tasks marked with `(P)` can be executed in parallel as they have no data dependencies
- Tasks marked with `*` are optional test coverage tasks that can be deferred post-MVP
- Use AsyncSession for all database operations per design.md
- Enforce foreign key constraints and CASCADE deletion at database level
- Reorder algorithm uses row-level locking (SELECT FOR UPDATE) to prevent race conditions
- Duplicate songs allowed via surrogate key (no unique constraint on playlist_id, song_id)
- Soft-deleted songs excluded from queries with WHERE deleted_at IS NULL
- Pagination uses offset-based strategy (page/page_size params) consistent with music-catalog-management
- Default page_size: 20 for playlists, 50 for songs (max 100)
- Ownership verification required for all mutations (update, delete, add_song, remove_song, reorder)
- Default privacy: private (is_public=false) for new playlists
- Playlist song limit: 1000 songs (soft limit with warning, still allows creation)
