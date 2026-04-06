# Implementation Tasks

## Overview
Implementation tasks for Music-Catalog-Management following Test-Driven Development (TDD) methodology. All tasks follow Red-Green-Refactor cycle: write failing test first, implement minimal code to pass, then refactor while keeping tests green.

## Task Breakdown

- [x] 1. Database schema and models for catalog entities
- [x] 1.1 (P) Create artists table schema with indexes
  - Define PostgreSQL schema with id, name, country, created_at, updated_at
  - Create trigram GIN index on name column for fast search (pg_trgm extension)
  - Create standard index on country column for filtering
  - Add trigger for automatic updated_at timestamp updates
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.4, 13.4_

- [x] 1.2 (P) Create albums table schema with artist relationship
  - Define schema with id, title, artist_id, release_year, album_cover_url, created_at, updated_at
  - Create foreign key to artists table with ON DELETE RESTRICT
  - Create indexes on artist_id and release_year (DESC) for filtering and sorting
  - Create trigram GIN index on title for search
  - Add updated_at trigger
  - _Requirements: 5.1, 5.2, 5.3, 6.2, 12.2, 12.6, 13.4_

- [x] 1.3 (P) Create songs table schema with album relationship and soft delete
  - Define schema with id, title, album_id, duration_seconds, genre, year, external_links (JSONB), deleted_at, created_at, updated_at
  - Create foreign key to albums table with ON DELETE CASCADE
  - Add CHECK constraint on duration_seconds (1-7200)
  - Create indexes on album_id, deleted_at, genre
  - Create partial index on id WHERE deleted_at IS NULL for active songs
  - Create trigram GIN index on title for search
  - Add updated_at trigger
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 11.1, 11.2, 12.1, 12.4, 12.6, 13.4_

- [x] 1.4 (P) Create SQLAlchemy models for Artist, Album, Song
  - Define Artist model with all columns and relationship to albums
  - Define Album model with relationships to artist and songs
  - Define Song model with relationships to album
  - Configure cascade options for relationships
  - _Requirements: 12.1, 12.2, 12.3_

- [x] 2. Validation service for catalog data quality
- [x] 2.1 (P) Implement country code validation with pycountry
  - Write failing test: test_validate_country_code_accepts_valid_iso_codes
  - Write failing test: test_validate_country_code_rejects_invalid_codes
  - Implement ValidationService.validate_country_code using pycountry.countries
  - Verify ISO 3166-1 alpha-2 format (2 uppercase letters)
  - _Requirements: 1.3, 1.8, 14.3_

- [x] 2.2 (P) Implement release year validation
  - Write failing test: test_validate_release_year_accepts_valid_range
  - Write failing test: test_validate_release_year_rejects_future_years
  - Implement ValidationService.validate_release_year (1900 to current_year + 1)
  - Allow pre-release albums (current_year + 1)
  - _Requirements: 5.4, 14.4_

- [x] 2.3 (P) Implement duration validation
  - Write failing test: test_validate_duration_accepts_valid_seconds
  - Write failing test: test_validate_duration_rejects_invalid_range
  - Implement ValidationService.validate_duration_seconds (1-7200)
  - Verify realistic song length constraint
  - _Requirements: 8.4, 14.5_

- [x] 2.4 (P) Implement URL validation for album covers and external links
  - Write failing test: test_validate_url_accepts_http_https
  - Write failing test: test_validate_url_rejects_javascript_scheme
  - Implement ValidationService.validate_url using regex
  - Verify http/https schemes only
  - _Requirements: 5.9, 14.6_

- [x] 2.5 (P) Implement text field sanitization and trimming
  - Write failing test: test_sanitize_text_trims_whitespace
  - Write failing test: test_sanitize_text_rejects_empty_strings
  - Implement text sanitization (trim leading/trailing whitespace)
  - Reject empty or whitespace-only strings
  - _Requirements: 14.1, 14.2_

- [x] 3. Artist repository with CRUD operations
- [x] 3.1 (P) Implement ArtistRepository base CRUD methods
  - Write failing test: test_artist_repository_create_returns_artist_with_id
  - Write failing test: test_artist_repository_get_by_id_returns_artist
  - Write failing test: test_artist_repository_get_by_id_returns_none_when_not_found
  - Implement create, get_by_id, update methods using SQLAlchemy AsyncSession
  - Verify timestamps automatically set
  - _Requirements: 1.1, 1.4, 1.5, 4.1, 4.2, 4.3_

- [x] 3.2 (P) Implement artist pagination with albums count
  - Write failing test: test_artist_repository_list_paginated_returns_20_by_default
  - Write failing test: test_artist_repository_list_paginated_respects_max_100
  - Implement list_paginated with albums_count aggregation
  - Use default page_size=20, max page_size=100
  - Return (items, total) tuple
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.7_

- [x] 3.3 Implement artist search with trigram index
  - Write failing test: test_artist_repository_search_case_insensitive_partial_match
  - Write failing test: test_artist_repository_search_returns_paginated_results
  - Implement search method using ILIKE with trigram GIN index
  - Perform case-insensitive partial match
  - Return results within 200ms for 10k artists
  - Order by relevance (exact match first, then partial)
  - _Requirements: 3.1, 3.3, 3.4, 3.5, 3.6, 13.1_

- [x] 4. Artist service with business logic
- [x] 4.1 Create artist creation service method
  - Write failing test: test_artist_service_create_validates_name_length
  - Write failing test: test_artist_service_create_validates_country_code
  - Implement ArtistService.create_artist
  - Validate name length (1-200 characters)
  - Validate country code using ValidationService
  - Sanitize name (trim whitespace)
  - Return ArtistResponse with albums_count=0
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 14.1, 14.2_

- [x] 4.2 Implement artist retrieval by ID
  - Write failing test: test_artist_service_get_by_id_includes_albums_count
  - Implement ArtistService.get_artist_by_id
  - Include albums_count field from aggregation
  - Return None if artist not found
  - _Requirements: 2.1, 2.7_

- [x] 4.3 Implement artist search service method
  - Write failing test: test_artist_service_search_rejects_short_query
  - Write failing test: test_artist_service_search_sanitizes_input
  - Implement ArtistService.search_artists
  - Reject queries less than 2 characters (400 Bad Request)
  - Sanitize search input to prevent SQL injection
  - Return paginated results
  - _Requirements: 3.1, 3.2, 3.3, 3.5, 3.6_

- [x] 4.4 Implement artist update service method
  - Write failing test: test_artist_service_update_modifies_updated_at
  - Write failing test: test_artist_service_update_preserves_created_at
  - Implement ArtistService.update_artist
  - Apply same validation rules as creation
  - Update updated_at timestamp automatically (trigger)
  - Do not modify created_at
  - _Requirements: 4.1, 4.2, 4.3, 4.7_

- [x] 5. Artist API endpoints with authorization
- [x] 5.1 Create artist creation endpoint
  - Write integration test: test_create_artist_requires_artist_or_admin_role
  - Write integration test: test_create_artist_returns_201_with_valid_data
  - Implement POST /api/v1/artists route
  - Require admin or artist role using require_role dependency
  - Validate request using Pydantic ArtistCreateRequest schema
  - Return 201 Created with artist details
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 5.2 Add artist creation error handling
  - Write integration test: test_create_artist_returns_403_for_user_role
  - Write integration test: test_create_artist_returns_400_for_invalid_name
  - Write integration test: test_create_artist_returns_400_for_invalid_country
  - Return 403 Forbidden for insufficient permissions
  - Return 400 Bad Request for validation errors with field details
  - _Requirements: 1.6, 1.7, 1.8_

- [x] 5.3 Create artist retrieval endpoints
  - Write integration test: test_get_artist_by_id_returns_200_with_albums_count
  - Write integration test: test_get_artist_by_id_returns_404_when_not_found
  - Write integration test: test_list_artists_allows_guest_access
  - Implement GET /api/v1/artists/{id} and GET /api/v1/artists
  - Allow guest and authenticated users (no role restriction)
  - Return 404 Not Found for missing artist
  - _Requirements: 2.1, 2.6, 2.8_

- [x] 5.4 Create artist search endpoint
  - Write integration test: test_search_artists_returns_paginated_results
  - Write integration test: test_search_artists_returns_400_for_short_query
  - Write integration test: test_search_artists_returns_empty_array_when_no_results
  - Implement GET /api/v1/artists/search
  - Accept query parameter (min 2 characters)
  - Support pagination parameters (page, page_size)
  - Return 200 OK with empty items array when no results
  - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [x] 5.5 Create artist update endpoint
  - Write integration test: test_update_artist_returns_200_with_updated_data
  - Write integration test: test_update_artist_returns_403_for_user_role
  - Write integration test: test_update_artist_returns_404_for_invalid_id
  - Implement PUT /api/v1/artists/{id}
  - Require admin or artist role
  - Apply same validation as creation
  - Return 200 OK with updated artist
  - _Requirements: 4.1, 4.4, 4.5, 4.6, 4.7_

- [x] 6. Album repository with CRUD and relationships
- [x] 6.1 (P) Implement AlbumRepository base CRUD methods
  - Write failing test: test_album_repository_create_enforces_foreign_key
  - Write failing test: test_album_repository_get_by_id_includes_artist_name
  - Implement create, get_by_id, update with artist relationship join
  - Verify foreign key constraint enforced
  - Include artist_name in response via join
  - _Requirements: 5.1, 5.3, 5.5, 5.7, 6.1, 12.3, 12.5_

- [x] 6.2 (P) Implement album pagination with sorting and filtering
  - Write failing test: test_album_repository_list_ordered_by_release_year_desc
  - Write failing test: test_album_repository_list_filters_by_artist_id
  - Implement list_paginated with artist_id filter
  - Order by release_year DESC, title ASC
  - Include songs_count and total_duration_seconds aggregation
  - _Requirements: 6.2, 6.3, 6.4, 6.6, 6.7_

- [x] 7. Album service with artist validation
- [x] 7.1 Create album creation service method
  - Write failing test: test_album_service_create_validates_artist_exists
  - Write failing test: test_album_service_create_validates_release_year
  - Write failing test: test_album_service_create_validates_album_cover_url
  - Implement AlbumService.create_album
  - Verify artist_id exists using ArtistRepository
  - Validate release_year using ValidationService
  - Validate album_cover_url if provided
  - Return 400 if artist not found
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6, 5.7, 5.9_

- [x] 7.2 Implement album retrieval service methods
  - Write failing test: test_album_service_get_by_id_calculates_total_duration
  - Implement AlbumService.get_album_by_id and list_albums
  - Calculate total_duration_seconds from SUM(songs.duration_seconds)
  - Include artist_name from join
  - Support artist_id filter for listing
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.7_

- [x] 7.3 Implement album update service method
  - Write failing test: test_album_service_update_validates_album_cover_url
  - Write failing test: test_album_service_update_uses_placeholder_for_unreachable_url
  - Implement AlbumService.update_album
  - Apply same validation as creation
  - Use default placeholder if album_cover_url unreachable
  - _Requirements: 7.1, 7.2, 7.3, 7.6_

- [x] 8. Album API endpoints
- [x] 8.1 Create album creation endpoint
  - Write integration test: test_create_album_returns_201_with_artist_name
  - Write integration test: test_create_album_returns_400_when_artist_not_found
  - Write integration test: test_create_album_returns_403_for_user_role
  - Implement POST /api/v1/albums
  - Require admin or artist role
  - Validate AlbumCreateRequest with Pydantic
  - Return 201 Created with album details including artist_name
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

- [x] 8.2 Create album retrieval endpoints
  - Write integration test: test_get_album_by_id_includes_song_count_and_duration
  - Write integration test: test_list_albums_filters_by_artist_id
  - Write integration test: test_list_albums_orders_by_release_year_desc
  - Implement GET /api/v1/albums/{id} and GET /api/v1/albums
  - Support artist_id query parameter for filtering
  - Return albums ordered by release_year DESC, title ASC
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.7_

- [x] 8.3 Create album update endpoint
  - Write integration test: test_update_album_returns_200_with_updated_data
  - Write integration test: test_update_album_returns_403_for_user_role
  - Write integration test: test_update_album_returns_404_for_invalid_id
  - Implement PUT /api/v1/albums/{id}
  - Require admin or artist role
  - Apply validation rules
  - _Requirements: 7.1, 7.2, 7.4, 7.5, 7.6_

- [x] 9. Song repository with soft delete
- [x] 9.1 (P) Implement SongRepository with soft delete filtering
  - Write failing test: test_song_repository_create_with_album_relationship
  - Write failing test: test_song_repository_get_by_id_excludes_deleted_by_default
  - Write failing test: test_song_repository_get_by_id_includes_deleted_with_flag
  - Implement create, get_by_id with include_deleted parameter
  - Apply deleted_at IS NULL filter automatically
  - Include album and artist names via joins
  - _Requirements: 8.1, 8.3, 8.5, 9.1, 9.4, 11.3, 11.4_

- [x] 9.2 (P) Implement song pagination with album filtering
  - Write failing test: test_song_repository_list_excludes_deleted_songs
  - Write failing test: test_song_repository_list_filters_by_album_id
  - Write failing test: test_song_repository_list_orders_by_title
  - Implement list_paginated with album_id filter
  - Exclude deleted songs by default
  - Order by title when album_id provided
  - _Requirements: 9.2, 9.3, 9.7_

- [x] 9.3 Implement soft delete and restore methods
  - Write failing test: test_song_repository_soft_delete_sets_timestamp
  - Write failing test: test_song_repository_restore_clears_timestamp
  - Implement soft_delete (set deleted_at to NOW())
  - Implement restore (set deleted_at to NULL)
  - Verify record not removed from database
  - _Requirements: 11.1, 11.2, 11.6_

- [x] 10. Song service with album validation
- [x] 10.1 Create song creation service method
  - Write failing test: test_song_service_create_validates_album_exists
  - Write failing test: test_song_service_create_validates_duration
  - Write failing test: test_song_service_create_validates_title_length
  - Implement SongService.create_song
  - Verify album_id exists using AlbumRepository
  - Validate duration_seconds using ValidationService
  - Validate title length (1-200 characters)
  - Return 400 if album not found
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.6, 8.7, 8.9_

- [x] 10.2 Implement song retrieval service methods
  - Write failing test: test_song_service_get_by_id_includes_artist_and_album
  - Write failing test: test_song_service_list_excludes_deleted_songs
  - Implement SongService.get_song_by_id and list_songs
  - Include album_title, artist_id, artist_name via joins
  - Exclude soft-deleted songs by default
  - Support album_id filter
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.7_

- [x] 10.3 Implement song update service method
  - Write failing test: test_song_service_update_validates_fields
  - Implement SongService.update_song
  - Apply same validation rules as creation
  - Update updated_at timestamp
  - _Requirements: 10.1, 10.2, 10.5_

- [x] 10.4 Implement song soft delete and restore service methods
  - Write failing test: test_song_service_soft_delete_sets_deleted_at
  - Write failing test: test_song_service_soft_delete_returns_404_when_not_found
  - Write failing test: test_song_service_restore_clears_deleted_at
  - Implement soft_delete_song
  - Implement restore_song (admin only)
  - Verify soft-deleted songs return 404 for regular users
  - Allow admin to retrieve with include_deleted parameter
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

- [x] 11. Song API endpoints with soft delete
- [x] 11.1 Create song creation endpoint
  - Write integration test: test_create_song_returns_201_with_artist_and_album
  - Write integration test: test_create_song_returns_400_when_album_not_found
  - Write integration test: test_create_song_returns_403_for_user_role
  - Implement POST /api/v1/songs
  - Require admin or artist role
  - Validate SongCreateRequest with Pydantic
  - Return 201 Created with song, album, and artist details
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

- [x] 11.2 Create song retrieval endpoints
  - Write integration test: test_get_song_by_id_returns_404_for_deleted
  - Write integration test: test_list_songs_excludes_deleted_songs
  - Write integration test: test_list_songs_filters_by_album_id
  - Implement GET /api/v1/songs/{id} and GET /api/v1/songs
  - Exclude deleted songs from listing
  - Return 404 for deleted songs unless admin with include_deleted
  - Support album_id filter
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.7_

- [x] 11.3 Create song update endpoint
  - Write integration test: test_update_song_returns_200_with_updated_data
  - Write integration test: test_update_song_returns_403_for_user_role
  - Write integration test: test_update_song_returns_404_for_deleted_song
  - Implement PUT /api/v1/songs/{id}
  - Require admin or artist role
  - Apply validation rules
  - Return 404 if song is deleted
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 11.4 Create song soft delete endpoint
  - Write integration test: test_delete_song_sets_deleted_at_timestamp
  - Write integration test: test_delete_song_returns_403_for_non_admin
  - Write integration test: test_deleted_song_excluded_from_listing
  - Implement DELETE /api/v1/songs/{id}
  - Require admin role only
  - Set deleted_at timestamp (soft delete)
  - Return 204 No Content on success
  - _Requirements: 11.1, 11.2, 11.3, 11.7_

- [x] 11.5 Create song restore endpoint
  - Write integration test: test_restore_song_clears_deleted_at
  - Write integration test: test_restore_song_returns_403_for_non_admin
  - Implement POST /api/v1/songs/{id}/restore
  - Require admin role only
  - Clear deleted_at timestamp
  - Return 200 OK with restored song
  - _Requirements: 11.4, 11.5, 11.6_

- [x] 12. Referential integrity and cascade behavior
- [x] 12.1 Test album deletion cascades to songs
  - Write integration test: test_delete_album_cascades_to_songs
  - Verify DELETE album removes all associated songs (hard delete)
  - Confirm ON DELETE CASCADE constraint enforced
  - _Requirements: 12.1, 12.4_

- [x] 12.2 Test artist deletion restriction with albums
  - Write integration test: test_delete_artist_with_albums_returns_409
  - Verify DELETE artist with albums returns 409 Conflict
  - Confirm ON DELETE RESTRICT constraint enforced
  - _Requirements: 12.2, 12.3_

- [x] 12.3 Test foreign key validation on creation
  - Write integration test: test_create_album_with_invalid_artist_id_returns_400
  - Write integration test: test_create_song_with_invalid_album_id_returns_400
  - Verify foreign key violations return 400 Bad Request
  - _Requirements: 12.4, 12.5, 12.6_

- [x] 13. Integration and system testing
- [x] 13.1 Test complete catalog workflow
  - Write integration test: test_catalog_workflow_create_artist_album_song
  - Create artist → create album → create song
  - Retrieve artist with albums_count
  - Retrieve album with songs_count and total_duration
  - Retrieve song with artist and album details
  - Verify all relationships correct
  - _Requirements: 1.1, 5.1, 8.1, 2.1, 6.1, 9.1_

- [x] 13.2 Test soft delete and restore workflow
  - Write integration test: test_soft_delete_restore_workflow
  - Create song → soft delete → verify 404
  - Admin restore → verify 200
  - Verify song appears in listings again
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.6_

- [x] 13.3 Test pagination consistency across entities
  - Write integration test: test_pagination_consistency_artist_album_song
  - Create 50 artists, 50 albums, 50 songs
  - Verify page 1 + page 2 items = first 40 items (default page_size 20)
  - Test max page_size 100 enforcement
  - _Requirements: 2.3, 2.4, 6.7, 9.6_

- [x] 13.4 Test search functionality across entities
  - Write integration test: test_search_artists_case_insensitive
  - Write integration test: test_search_returns_empty_for_no_match
  - Verify case-insensitive partial match
  - Verify empty results return 200 with empty items array
  - _Requirements: 3.1, 3.3, 3.5_

- [x] 14. Performance and validation testing
- [x] 14.1* Validate search performance targets
  - Create 10,000 artist records
  - Test search query completes within 200ms (p95)
  - Verify trigram GIN index used (EXPLAIN ANALYZE)
  - _Requirements: 3.4, 13.1, Non-functional Performance 1_

- [x] 14.2* Validate pagination performance for deep pages
  - Create 100,000 album records
  - Test page 100 query completes within 500ms
  - Verify album listing with filters completes within 300ms (p95)
  - _Requirements: 13.2, Non-functional Performance 2_

- [x] 14.3* Validate song listing performance with soft delete filter
  - Create 1,000,000 song records with 10% soft-deleted
  - Test song listing completes within 300ms (p95)
  - Verify partial index on active songs used
  - _Requirements: 13.3, Non-functional Performance 3_

- [x] 14.4* Validate data quality with comprehensive validation suite
  - Test all validation rules (country codes, release year, duration, URLs)
  - Verify detailed validation errors returned with field names
  - Test whitespace trimming and empty string rejection
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7_

- [x] 14.5* Load test catalog operations under concurrent requests
  - Test 100 concurrent create operations (artists, albums, songs)
  - Test 1000 concurrent read operations
  - Verify connection pooling (10-20 connections) handles load
  - Verify no deadlocks or race conditions
  - _Requirements: Non-functional Scalability 1, 2_

- [x] 14.6* Validate ACID transaction behavior
  - Test concurrent updates to same entity
  - Verify foreign key constraints enforced in all scenarios
  - Verify created_at and updated_at timestamps accurate
  - _Requirements: Non-functional Data Integrity 1, 2, 3_

## Notes
- All tasks follow TDD methodology: Write failing test (Red) → Implement minimal code (Green) → Refactor while keeping tests green
- Tasks marked with `(P)` can be executed in parallel as they have no data dependencies
- Tasks marked with `*` are optional test coverage tasks that can be deferred post-MVP
- Minimum test coverage: 80% backend (pytest-cov)
- Use pytest for backend testing with factory_boy for test fixtures
- PostgreSQL pg_trgm extension required for trigram search indexes
- Foreign key constraints: artist → albums (RESTRICT), album → songs (CASCADE)
- Soft delete: Songs only (deleted_at timestamp), not artists or albums
- Pagination: Default 20 items/page, max 100 items/page
- Performance targets: <200ms artist search, <300ms album/song queries for large datasets
