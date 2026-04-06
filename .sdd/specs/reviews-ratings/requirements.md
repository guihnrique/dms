# Requirements Document

## Project Description (Input)
Reviews and Ratings: User review and rating system for songs with 1-5 star ratings, review text (0-2000 characters), average rating calculation, review helpfulness voting, content moderation flagging, and user ownership verification for The Sonic Immersive music discovery platform

## Introduction

The Reviews-Ratings module enables authenticated users to rate and review songs in the catalog. This system provides 1-5 star ratings, optional review text (up to 2000 characters), average rating calculation per song, review helpfulness voting (helpful/not helpful), content moderation flagging for inappropriate content, and ownership verification for review updates and deletions. The module supports one review per user per song with update capability.

## Requirements

### Requirement 1: Review Creation
**Objective:** As an authenticated user, I want to rate and review songs, so that I can share my opinion and help others discover quality music

#### Acceptance Criteria
1. When authenticated user submits review, the Review Service shall validate rating is integer between 1 and 5
2. When submitting review, the Review Service shall validate song_id exists in catalog
3. When submitting review, the Review Service shall validate review body is 0-2000 characters
4. When review body is empty, the Review Service shall accept review with rating only (optional text)
5. When review is created successfully, the Review Service shall set created_at and updated_at timestamps
6. When review is created successfully, the Review Service shall return 201 Created with review details
7. If user is not authenticated, then the Review Service shall return 401 Unauthorized
8. If rating is outside 1-5 range, then the Review Service shall return 400 Bad Request with message "Rating must be between 1 and 5"
9. If song_id does not exist, then the Review Service shall return 400 Bad Request with message "Song not found"

### Requirement 2: Review Update
**Objective:** As a review author, I want to update my reviews, so that I can change my rating or text after further listening

#### Acceptance Criteria
1. When user submits review for song already reviewed by same user, the Review Service shall update existing review
2. When review is updated, the Review Service shall update rating, body, and updated_at timestamp
3. When review is updated, the Review Service shall NOT modify created_at timestamp
4. When review is updated successfully, the Review Service shall return 200 OK with updated review details
5. If user attempts to update another user's review, then the Review Service shall return 403 Forbidden
6. The Review Service shall validate updated fields using same rules as review creation

### Requirement 3: Review Deletion
**Objective:** As a review author, I want to delete my reviews, so that I can remove opinions I no longer hold

#### Acceptance Criteria
1. When authenticated user requests review deletion, the Review Service shall verify user is review owner
2. When user is review owner, the Review Service shall perform hard delete (remove from database)
3. When review is deleted successfully, the Review Service shall return 204 No Content
4. When review is deleted, the Review Service shall recalculate song average rating
5. If user is not review owner, then the Review Service shall return 403 Forbidden
6. If review ID does not exist, then the Review Service shall return 404 Not Found

### Requirement 4: Review Retrieval for Song
**Objective:** As a user, I want to read reviews for a song, so that I can learn others' opinions before listening

#### Acceptance Criteria
1. When user requests reviews for song, the Review Service shall return paginated results ordered by created_at DESC
2. When user requests reviews, the Review Service shall include: id, user_id, username, rating, body, helpful_count, created_at, updated_at
3. The Review Service shall use default page size of 10 reviews with maximum 50 reviews per page
4. When user requests reviews, the Review Service shall include total review count for song
5. If song has no reviews, then the Review Service shall return 200 OK with empty items array
6. The Review Service shall NOT return flagged reviews pending moderation

### Requirement 5: Review Retrieval by User
**Objective:** As a user, I want to view all my reviews, so that I can track my opinions and ratings

#### Acceptance Criteria
1. When authenticated user requests their own reviews, the Review Service shall return all reviews by that user
2. When user requests their reviews, the Review Service shall return paginated results ordered by created_at DESC
3. When user requests their reviews, the Review Service shall include song title and artist name for each review
4. The Review Service shall allow users to view only their own reviews (privacy protection)
5. If user attempts to view another user's review list, then the Review Service shall return 403 Forbidden

### Requirement 6: Average Rating Calculation
**Objective:** As a user, I want to see average ratings for songs, so that I can quickly assess song quality

#### Acceptance Criteria
1. When review is created or updated, the Rating Calculation Service shall recalculate average rating for song
2. When review is deleted, the Rating Calculation Service shall recalculate average rating for song
3. The Rating Calculation Service shall calculate average rating as: SUM(rating) / COUNT(reviews)
4. The Rating Calculation Service shall round average rating to 1 decimal place
5. When song has no reviews, the Rating Calculation Service shall return NULL or 0 for average rating
6. When displaying song details, the Song Service shall include average_rating and review_count fields
7. The Rating Calculation Service shall cache average ratings to avoid recalculating on every request

### Requirement 7: Review Helpfulness Voting
**Objective:** As a user, I want to vote on review helpfulness, so that quality reviews are surfaced

#### Acceptance Criteria
1. When authenticated user votes review as helpful, the Voting Service shall increment helpful_count
2. When authenticated user votes review as not helpful, the Voting Service shall decrement helpful_count (minimum 0)
3. The Voting Service shall track votes in review_votes table with user_id, review_id, vote_type
4. When user changes vote, the Voting Service shall update vote_type and adjust helpful_count
5. When user votes on same review twice with same vote_type, the Voting Service shall return 400 Bad Request
6. If user is not authenticated, then the Voting Service shall return 401 Unauthorized
7. The Voting Service shall prevent users from voting on their own reviews

### Requirement 8: Content Moderation Flagging
**Objective:** As a content moderator, I want inappropriate reviews flagged, so that I can review and remove harmful content

#### Acceptance Criteria
1. When review contains profanity or inappropriate content, the Moderation Service shall flag review for review
2. When review is flagged, the Moderation Service shall set is_flagged field to true
3. When review is flagged, the Moderation Service shall NOT display review to public users
4. When admin reviews flagged content, the Moderation Service shall allow approve or delete actions
5. The Moderation Service shall use profanity filter library to detect inappropriate words
6. The Moderation Service shall log all flagged reviews with reason and timestamp
7. When user reports review manually, the Moderation Service shall flag review and notify moderators

### Requirement 9: Review Ownership Verification
**Objective:** As a security officer, I want ownership verified for review mutations, so that users cannot modify others' reviews

#### Acceptance Criteria
1. When user attempts to update review, the Ownership Service shall verify author_user_id matches authenticated user ID
2. When user attempts to delete review, the Ownership Service shall verify author_user_id matches authenticated user ID
3. If ownership verification fails, then the Ownership Service shall return 403 Forbidden with message "You do not own this review"
4. The Ownership Service shall extract user ID from JWT token payload
5. The Ownership Service shall perform ownership check before executing any mutation

### Requirement 10: One Review Per User Per Song
**Objective:** As a system administrator, I want one review limit enforced, so that users cannot spam multiple reviews

#### Acceptance Criteria
1. When user creates review for song, the Review Service shall check if user already reviewed that song
2. If user already reviewed song, then the Review Service shall update existing review instead of creating new one
3. The Database Service shall enforce unique constraint on (user_id, song_id) in reviews table
4. When duplicate review is attempted, the Database Service shall return constraint violation error
5. The Review Service shall provide clear message: "You have already reviewed this song. Your review has been updated."

### Requirement 11: Review Text Validation
**Objective:** As a content quality officer, I want review text validated, so that reviews are meaningful and appropriate

#### Acceptance Criteria
1. When review body is provided, the Validation Service shall reject empty or whitespace-only strings
2. The Validation Service shall trim leading and trailing whitespace from review body
3. The Validation Service shall validate review body does not exceed 2000 characters
4. The Validation Service shall allow reviews with rating only (no text required)
5. The Validation Service shall reject reviews containing only special characters or numbers
6. If validation fails, then the Validation Service shall return 400 Bad Request with detailed error messages

### Requirement 12: Review Display in Song Details
**Objective:** As a user, I want to see reviews and average rating on song pages, so that I can assess song quality

#### Acceptance Criteria
1. When user requests song details, the Song Service shall include average_rating and review_count fields
2. When user views song page, the Frontend shall display star rating visualization (filled/empty stars)
3. When user views song page, the Frontend shall display recent reviews (top 3 by helpful_count)
4. When user clicks "See all reviews", the Frontend shall navigate to full review list page
5. The Song Service shall include user's own review (if exists) in song details response
6. When user has not reviewed song, the Song Service shall indicate review_status: "not_reviewed"

## Non-Functional Requirements

### Performance
1. The Review Service shall complete review CRUD operations within 300ms for 95% of requests
2. The Rating Calculation Service shall complete average rating calculation within 100ms
3. The Voting Service shall complete helpfulness vote operations within 200ms

### Scalability
1. The Review Service shall support songs with up to 10,000 reviews without degradation
2. The Rating Calculation Service shall cache average ratings with 5-minute TTL

### Data Integrity
1. The Database Service shall enforce foreign key constraints: user_id → users.id, song_id → songs.id
2. The Database Service shall enforce unique constraint on (user_id, song_id) in reviews table
3. The Database Service shall enforce NOT NULL constraints on user_id, song_id, rating
4. The Database Service shall use CHECK constraint to enforce rating between 1 and 5

### Content Quality
1. The Moderation Service shall flag reviews within 1 second of creation
2. The Moderation Service shall maintain profanity filter with regular updates
3. The Moderation Service shall log all moderation actions for audit trail

### Usability
1. The Review UI shall support inline editing of reviews
2. The Review UI shall show character count during review composition
3. The Review UI shall provide star rating widget for intuitive rating input
4. The Review UI shall highlight user's own review in song review list
