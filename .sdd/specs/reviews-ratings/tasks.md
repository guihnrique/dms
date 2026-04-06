# Implementation Tasks

## Overview
Implementation tasks for Reviews-Ratings module following Test-Driven Development (TDD) methodology. All tasks follow Red-Green-Refactor cycle: write failing test first, implement minimal code to pass, then refactor while keeping tests green.

## Task Breakdown

- [x] 1. Database schema and models setup
- [x] 1.1 (P) Create database migration for reviews table
  - Create migration file with reviews table: id (UUID primary key), user_id (foreign key to users.id), song_id (foreign key to songs.id), rating (integer CHECK 1-5), body (text 0-2000 chars), is_flagged (boolean default false), helpful_count (integer default 0), created_at (timestamp), updated_at (timestamp)
  - Add unique constraint on (user_id, song_id) to enforce one review per user per song
  - Add NOT NULL constraints on user_id, song_id, rating
  - Add CHECK constraint to enforce rating between 1 and 5
  - Add indexes on song_id, user_id, and created_at for query performance
  - _Requirements: 1, 10_

- [x] 1.2 (P) Create database migration for review_votes table
  - Create migration file with review_votes table: id (UUID primary key), user_id (foreign key to users.id), review_id (foreign key to reviews.id), vote_type (varchar: "helpful" or "not_helpful"), created_at (timestamp), updated_at (timestamp)
  - Add unique constraint on (user_id, review_id) to prevent duplicate votes
  - Add NOT NULL constraints on user_id, review_id, vote_type
  - Add index on review_id for vote count queries
  - _Requirements: 7_

- [x] 1.3 (P) Add average rating columns to songs table
  - Create migration to add average_rating (decimal 2,1 nullable) and review_count (integer default 0) columns to songs table
  - Add index on average_rating for sorting songs by rating
  - Initialize existing songs with NULL average_rating and 0 review_count
  - _Requirements: 6, 12_

- [x] 1.4 Define Review and ReviewVote models
  - Write failing tests for Review model with all fields, relationships to User and Song
  - Create Review SQLAlchemy model with user relationship, song relationship, and votes collection
  - Define ReviewVote SQLAlchemy model with user relationship and review relationship
  - Implement __repr__ methods for debugging
  - Verify model relationships load correctly in tests
  - _Requirements: 1, 7_

- [x] 2. Validation and schema definitions
- [x] 2.1 (P) Define Pydantic request schemas with validation
  - Write failing tests for ReviewCreateRequest schema validation (rating 1-5, body 0-2000 chars)
  - Create ReviewCreateRequest schema with rating validation (ge=1, le=5), body validation (max_length=2000, optional)
  - Create ReviewUpdateRequest schema with same validation rules
  - Create VoteRequest schema with vote_type enum ("helpful", "not_helpful")
  - Implement custom validators to trim whitespace from review body and reject whitespace-only strings
  - _Requirements: 1, 11_

- [x] 2.2 (P) Define Pydantic response schemas
  - Define ReviewResponse schema with id, user_id, username, song_id, rating, body, is_flagged, helpful_count, created_at, updated_at
  - Define ReviewListResponse schema with items array, total count, page, page_size
  - Define SongWithReviewsResponse schema extending song details with average_rating, review_count, user's own review
  - Include proper JSON serialization for datetime fields
  - _Requirements: 4, 5, 12_

- [x] 3. Repository layer implementation
- [x] 3.1 Implement ReviewRepository for data access
  - Write failing tests for ReviewRepository.create, get_by_id, get_by_user_and_song, update, delete methods
  - Implement ReviewRepository with AsyncSession injection
  - Create get_reviews_for_song method with pagination (order by created_at DESC, exclude flagged reviews)
  - Create get_reviews_by_user method with pagination (join song and artist for display)
  - Implement get_by_user_and_song to check for existing reviews
  - Handle database errors and return appropriate responses
  - _Requirements: 1, 2, 3, 4, 5_

- [x] 3.2 (P) Implement VoteRepository for helpfulness voting
  - Write failing tests for VoteRepository.create_or_update_vote, get_vote methods
  - Implement VoteRepository with AsyncSession injection
  - Create create_or_update_vote method to handle new votes and vote changes
  - Implement get_vote to check existing user votes on reviews
  - Handle unique constraint violations gracefully
  - _Requirements: 7_

- [x] 3.3 (P) Extend SongRepository for rating updates
  - Write failing tests for SongRepository.update_average_rating method
  - Add update_average_rating method to SongRepository to denormalize rating data
  - Update songs.average_rating and songs.review_count atomically
  - Handle songs with zero reviews (set average_rating to NULL)
  - _Requirements: 6_

- [x] 4. Content moderation service
- [x] 4.1 (P) Implement ModerationService with profanity filtering
  - Write failing tests for ModerationService.check_profanity method with profane and clean text
  - Install and configure better-profanity library (version 0.7+)
  - Implement check_profanity method that returns boolean is_flagged
  - Configure profanity filter with custom word list if needed
  - Log all flagged reviews with reason and timestamp
  - Ensure detection completes within 1 second as per NFR
  - _Requirements: 8_

- [x] 5. Business logic services
- [x] 5.1 Implement ReviewService for CRUD operations
  - Write failing tests for ReviewService.create_or_update_review covering new review and update existing review scenarios
  - Implement create_or_update_review that checks for existing review via ReviewRepository.get_by_user_and_song
  - Validate song_id exists using SongRepository before creating review
  - Call ModerationService.check_profanity to set is_flagged field
  - Handle new review creation and existing review update in single method
  - Return clear message "You have already reviewed this song. Your review has been updated." for updates
  - _Requirements: 1, 2, 8, 10_

- [x] 5.2 Implement average rating recalculation
  - Write failing tests for ReviewService.recalculate_average_rating with various scenarios (multiple reviews, single review, zero reviews)
  - Implement recalculate_average_rating method that queries all non-flagged reviews for song
  - Calculate average as SUM(rating) / COUNT(reviews) rounded to 1 decimal place
  - Call SongRepository.update_average_rating to denormalize data
  - Handle edge case where all reviews are flagged (set average to NULL)
  - Complete calculation within 100ms as per NFR
  - _Requirements: 6_

- [x] 5.3 Implement review deletion with rating recalculation
  - Write failing tests for ReviewService.delete_review
  - Implement delete_review method that performs hard delete via ReviewRepository
  - Trigger recalculate_average_rating after successful deletion
  - Return 204 No Content on success
  - _Requirements: 3, 6_

- [x] 5.4 (P) Implement VotingService for helpfulness voting
  - Write failing tests for VotingService.vote covering new vote, vote change, and duplicate vote scenarios
  - Implement vote method that checks existing vote via VoteRepository.get_vote
  - Calculate helpful_count adjustment based on vote change (increment/decrement)
  - Update ReviewRepository to increment/decrement helpful_count
  - Prevent users from voting on their own reviews
  - Return 400 Bad Request if user votes same type twice
  - _Requirements: 7_

- [x] 6. Ownership verification and dependencies
- [x] 6.1 (P) Implement verify_review_ownership dependency
  - Write failing tests for verify_review_ownership with owner, non-owner, and non-existent review scenarios
  - Create FastAPI dependency function that takes review_id and current_user
  - Query review from ReviewRepository and verify review.user_id matches current_user.id
  - Return 403 Forbidden with message "You do not own this review" if ownership fails
  - Return 404 Not Found if review_id does not exist
  - _Requirements: 9_

- [x] 7. API routes and endpoints
- [x] 7.1 Implement POST /reviews endpoint for review creation
  - Write failing integration tests for POST /reviews with valid data, invalid rating, non-existent song, and duplicate review scenarios
  - Create POST /reviews route with get_current_user dependency for authentication
  - Validate request using ReviewCreateRequest schema
  - Call ReviewService.create_or_update_review
  - Return 201 Created for new review, 200 OK for update
  - Return 401 Unauthorized if user not authenticated
  - Return 400 Bad Request for validation errors
  - _Requirements: 1, 10_

- [x] 7.2 Implement PUT /reviews/{review_id} endpoint for review update
  - Write failing integration tests for PUT /reviews/{id} with owner update, non-owner attempt, and validation error scenarios
  - Create PUT /reviews/{review_id} route with verify_review_ownership dependency
  - Validate request using ReviewUpdateRequest schema
  - Call ReviewService to update review and recalculate rating
  - Return 200 OK with updated review
  - Return 403 Forbidden if ownership verification fails
  - _Requirements: 2, 9_

- [x] 7.3 Implement DELETE /reviews/{review_id} endpoint
  - Write failing integration tests for DELETE /reviews/{id} with owner deletion, non-owner attempt, and non-existent review scenarios
  - Create DELETE /reviews/{review_id} route with verify_review_ownership dependency
  - Call ReviewService.delete_review
  - Return 204 No Content on successful deletion
  - Return 403 Forbidden if ownership fails, 404 Not Found if review does not exist
  - _Requirements: 3, 9_

- [x] 7.4 Implement GET /songs/{song_id}/reviews endpoint
  - Write failing integration tests for GET /songs/{song_id}/reviews with pagination, flagged review exclusion, and empty results scenarios
  - Create GET /songs/{song_id}/reviews route (public, no auth required)
  - Implement pagination with default page_size 10, max 50
  - Order results by created_at DESC
  - Exclude reviews where is_flagged = true
  - Return ReviewListResponse with items, total, page, page_size
  - Include username via join with users table
  - _Requirements: 4_

- [x] 7.5 (P) Implement GET /users/me/reviews endpoint
  - Write failing integration tests for GET /users/me/reviews with authenticated user, empty reviews, and pagination scenarios
  - Create GET /users/me/reviews route with get_current_user dependency
  - Query reviews by current_user.id via ReviewRepository.get_reviews_by_user
  - Include song title and artist name via joins
  - Implement pagination (default 10, max 50)
  - Return 200 OK with ReviewListResponse
  - Return 401 Unauthorized if user not authenticated
  - _Requirements: 5_

- [x] 7.6 (P) Implement POST /reviews/{review_id}/vote endpoint
  - Write failing integration tests for POST /reviews/{id}/vote with helpful vote, vote change, duplicate vote, and own review scenarios
  - Create POST /reviews/{review_id}/vote route with get_current_user dependency
  - Validate request using VoteRequest schema
  - Call VotingService.vote
  - Return 200 OK on successful vote
  - Return 400 Bad Request for duplicate vote or voting on own review
  - Return 401 Unauthorized if user not authenticated
  - _Requirements: 7_

- [x] 7.7 (P) Implement GET /songs/{song_id} extension for reviews
  - Write failing integration tests for GET /songs/{song_id} including average_rating, review_count, and user's own review
  - Extend existing GET /songs/{song_id} endpoint to include average_rating and review_count from songs table
  - If user is authenticated, include user's own review via ReviewRepository.get_by_user_and_song
  - Include review_status: "not_reviewed" if user has not reviewed song
  - Return SongWithReviewsResponse
  - _Requirements: 12_

- [x] 8. Admin moderation endpoints
- [x] 8.1 (P) Implement GET /admin/reviews/flagged endpoint
  - Write failing integration tests for GET /admin/reviews/flagged with admin user and non-admin user scenarios
  - Create GET /admin/reviews/flagged route with admin role requirement
  - Query all reviews where is_flagged = true via ReviewRepository
  - Implement pagination
  - Include full review details and flagging reason from logs
  - Return 403 Forbidden if user lacks admin role
  - _Requirements: 8_

- [x] 8.2 (P) Implement POST /admin/reviews/{review_id}/approve endpoint
  - Write failing integration tests for POST /admin/reviews/{id}/approve with admin approval scenario
  - Create POST /admin/reviews/{review_id}/approve route with admin role requirement
  - Update review to set is_flagged = false
  - Log moderation action (approved) with admin user_id and timestamp
  - Return 200 OK
  - _Requirements: 8_

- [x] 8.3 (P) Implement DELETE /admin/reviews/{review_id} endpoint
  - Write failing integration tests for DELETE /admin/reviews/{id} with admin deletion scenario
  - Create DELETE /admin/reviews/{review_id} route with admin role requirement
  - Call ReviewService.delete_review
  - Log moderation action (deleted) with admin user_id and timestamp
  - Return 204 No Content
  - _Requirements: 8_

- [x] 9. Integration and end-to-end testing
- [x] 9.1* Test complete review lifecycle flow
  - Write integration test for full review lifecycle: create review → vote helpful → update review → delete review
  - Verify average rating updates correctly at each step
  - Verify helpful_count increments correctly
  - Verify ownership enforcement at update and delete
  - Test with multiple users and multiple reviews per song
  - _Requirements: 1, 2, 3, 6, 7_

- [x] 9.2* Test content moderation workflow
  - Write integration test for profanity flagging: create review with profane content → verify is_flagged = true → admin approve → verify is_flagged = false
  - Test flagged review exclusion from public queries
  - Test admin endpoints for viewing and managing flagged reviews
  - _Requirements: 8_

- [x] 9.3* Test one review per user per song enforcement
  - Write integration test attempting to create duplicate review → verify update behavior instead of error
  - Test unique constraint violation handling
  - Verify clear message returned: "You have already reviewed this song. Your review has been updated."
  - _Requirements: 10_

- [x] 9.4* Test performance requirements
  - Write performance tests to verify review CRUD operations complete within 300ms
  - Verify average rating calculation completes within 100ms
  - Verify helpfulness vote operations complete within 200ms
  - Test with songs having 10,000 reviews to verify scalability NFR
  - Test profanity detection completes within 1 second
  - _Requirements: 1, 6, 7, 8_

## Notes
- All tasks follow TDD methodology: Write failing test (Red) → Implement minimal code (Green) → Refactor while keeping tests green
- Tasks marked with `(P)` can be executed in parallel as they have no data dependencies
- Tasks marked with `*` are optional test coverage tasks that can be deferred post-MVP
- Use AsyncSession for all database operations per design.md
- Enforce foreign key constraints and unique constraints at database level
- Average rating calculation is synchronous but should use database transactions
- Profanity filtering uses better-profanity library (lightweight, <1ms detection)
- All mutations (create, update, delete) trigger average rating recalculation
- Pagination uses offset-based strategy (page/page_size params) consistent with user-playlists
- Admin moderation endpoints require admin role from auth-security-foundation
