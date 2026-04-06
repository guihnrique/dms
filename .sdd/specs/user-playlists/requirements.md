# Requirements Document

## Project Description (Input)
User Playlists: Playlist creation and management system allowing authenticated users to create, organize, share (public/private), and reorder personal music collections. Includes playlist ownership verification, song addition/removal, duplicate handling, and support for up to 1000 songs per playlist for The Sonic Immersive platform

## Introduction

The User-Playlists module enables authenticated users to create and manage personalized music collections. This system provides playlist CRUD operations, song management within playlists, privacy controls (public/private sharing), song reordering capabilities, and ownership verification. Playlists support up to 1000 songs with duplicate song instances allowed, enabling users to organize their favorite music flexibly.

## Requirements

### Requirement 1: Playlist Creation
**Objective:** As an authenticated user, I want to create playlists, so that I can organize my favorite songs into collections

#### Acceptance Criteria
1. When authenticated user submits playlist creation request, the Playlist Service shall create playlist record in database
2. When creating playlist, the Playlist Service shall validate playlist title is 1-200 characters
3. When creating playlist, the Playlist Service shall set owner_user_id to authenticated user ID
4. When playlist is created successfully, the Playlist Service shall set created_at and updated_at timestamps
5. When playlist is created successfully, the Playlist Service shall set default privacy to private
6. When playlist is created successfully, the Playlist Service shall return 201 Created with playlist details
7. If user is not authenticated, then the Playlist Service shall return 401 Unauthorized
8. If playlist title is empty or exceeds 200 characters, then the Playlist Service shall return 400 Bad Request with validation errors

### Requirement 2: Playlist Retrieval
**Objective:** As a user, I want to view my playlists and discover public playlists, so that I can access and explore music collections

#### Acceptance Criteria
1. When authenticated user requests their playlists, the Playlist Service shall return only playlists owned by user
2. When user requests public playlists, the Playlist Service shall return playlists marked as public
3. When user requests playlist by ID, the Playlist Service shall return playlist with full song details
4. When user requests playlist details, the Playlist Service shall include: id, title, owner_user_id, is_public, songs_count, total_duration_seconds, created_at, updated_at
5. When user requests playlist listing, the Playlist Service shall return paginated results with default page size of 20
6. If playlist ID does not exist, then the Playlist Service shall return 404 Not Found
7. If user requests private playlist owned by another user, then the Playlist Service shall return 403 Forbidden
8. The Playlist Service shall calculate total_duration_seconds by summing all song durations in playlist

### Requirement 3: Playlist Update
**Objective:** As a playlist owner, I want to update my playlists, so that I can change title and privacy settings

#### Acceptance Criteria
1. When authenticated user submits playlist updates, the Playlist Service shall verify user is playlist owner
2. When user is playlist owner, the Playlist Service shall update playlist record
3. When playlist is updated, the Playlist Service shall update updated_at timestamp
4. When playlist privacy is toggled, the Playlist Service shall update is_public field
5. When playlist is updated successfully, the Playlist Service shall return 200 OK with updated playlist details
6. If user is not playlist owner, then the Playlist Service shall return 403 Forbidden with message "You do not own this playlist"
7. If playlist ID does not exist, then the Playlist Service shall return 404 Not Found
8. The Playlist Service shall validate updated title using same rules as playlist creation

### Requirement 4: Playlist Deletion
**Objective:** As a playlist owner, I want to delete my playlists, so that I can remove collections I no longer want

#### Acceptance Criteria
1. When authenticated user requests playlist deletion, the Playlist Service shall verify user is playlist owner
2. When user is playlist owner, the Playlist Service shall delete playlist and all associated song entries
3. When playlist is deleted, the Playlist Service shall remove all records from playlist_songs join table
4. When playlist is deleted successfully, the Playlist Service shall return 204 No Content
5. If user is not playlist owner, then the Playlist Service shall return 403 Forbidden
6. If playlist ID does not exist, then the Playlist Service shall return 404 Not Found
7. The Playlist Service shall NOT perform soft delete for playlists (hard delete required)

### Requirement 5: Add Song to Playlist
**Objective:** As a playlist owner, I want to add songs to my playlists, so that I can build my music collections

#### Acceptance Criteria
1. When authenticated user adds song to playlist, the Playlist Service shall verify user is playlist owner
2. When user is playlist owner, the Playlist Service shall validate song_id exists in catalog
3. When song exists, the Playlist Service shall add song to playlist_songs join table
4. When song is added, the Playlist Service shall set position field to next available position (max + 1)
5. When song is added successfully, the Playlist Service shall return 200 OK with updated playlist details
6. When user adds duplicate song to playlist, the Playlist Service shall allow multiple instances
7. If song_id does not exist, then the Playlist Service shall return 400 Bad Request with message "Song not found"
8. If user is not playlist owner, then the Playlist Service shall return 403 Forbidden

### Requirement 6: Remove Song from Playlist
**Objective:** As a playlist owner, I want to remove songs from my playlists, so that I can curate my collections

#### Acceptance Criteria
1. When authenticated user removes song from playlist, the Playlist Service shall verify user is playlist owner
2. When user is playlist owner, the Playlist Service shall remove specific playlist_song entry by ID
3. When song is removed, the Playlist Service shall reorder remaining songs to fill position gaps
4. When song is removed successfully, the Playlist Service shall return 200 OK with updated playlist details
5. If playlist_song entry ID does not exist, then the Playlist Service shall return 404 Not Found
6. If user is not playlist owner, then the Playlist Service shall return 403 Forbidden
7. The Playlist Service shall support removing specific instance (not all instances of same song)

### Requirement 7: Reorder Songs in Playlist
**Objective:** As a playlist owner, I want to reorder songs in my playlists, so that I can arrange songs in desired sequence

#### Acceptance Criteria
1. When authenticated user submits reorder request, the Playlist Service shall verify user is playlist owner
2. When user is playlist owner, the Playlist Service shall accept new position for playlist_song entry
3. When new position is specified, the Playlist Service shall update position field and reorder other songs
4. When reordering is complete, the Playlist Service shall ensure all positions are sequential without gaps
5. When song is moved up, the Playlist Service shall shift other songs down
6. When song is moved down, the Playlist Service shall shift other songs up
7. If user is not playlist owner, then the Playlist Service shall return 403 Forbidden
8. If new position is out of bounds, then the Playlist Service shall return 400 Bad Request

### Requirement 8: Playlist Privacy Control
**Objective:** As a playlist owner, I want to control playlist visibility, so that I can share collections publicly or keep them private

#### Acceptance Criteria
1. When authenticated user toggles playlist privacy, the Playlist Service shall verify user is playlist owner
2. When user sets is_public to true, the Playlist Service shall make playlist visible to all users
3. When user sets is_public to false, the Playlist Service shall make playlist visible only to owner
4. When playlist privacy is toggled, the Playlist Service shall update updated_at timestamp
5. When public playlist is requested by guest user, the Playlist Service shall return playlist details
6. When private playlist is requested by non-owner, the Playlist Service shall return 403 Forbidden
7. The Playlist Service shall default new playlists to private (is_public = false)

### Requirement 9: Playlist Song Limit
**Objective:** As a system administrator, I want playlist size limited, so that performance remains acceptable

#### Acceptance Criteria
1. When user adds song to playlist, the Playlist Service shall check current song count
2. When playlist contains 1000 or more songs, the Playlist Service shall return warning but allow creation
3. When playlist exceeds 1000 songs, the Playlist Service shall log warning for performance monitoring
4. The Playlist Service shall return songs_count field in playlist responses
5. The Playlist Service shall support pagination when retrieving playlist songs
6. The Playlist Service shall use default page size of 50 songs with maximum 100 songs per page

### Requirement 10: Playlist Ownership Verification
**Objective:** As a security officer, I want ownership verified for all mutations, so that users cannot modify others' playlists

#### Acceptance Criteria
1. When user attempts to update playlist, the Ownership Service shall verify owner_user_id matches authenticated user ID
2. When user attempts to delete playlist, the Ownership Service shall verify owner_user_id matches authenticated user ID
3. When user attempts to add/remove songs, the Ownership Service shall verify owner_user_id matches authenticated user ID
4. When user attempts to reorder songs, the Ownership Service shall verify owner_user_id matches authenticated user ID
5. If ownership verification fails, then the Ownership Service shall return 403 Forbidden
6. The Ownership Service shall extract user ID from JWT token payload
7. The Ownership Service shall perform ownership check before executing any mutation

### Requirement 11: Playlist Song Details
**Objective:** As a user, I want full song details in playlists, so that I can see artist and album information

#### Acceptance Criteria
1. When user requests playlist by ID, the Playlist Service shall include full song details for each song
2. The Playlist Service shall include for each song: id, title, album_title, artist_name, duration_seconds, position
3. The Playlist Service shall order songs by position field in ascending order
4. The Playlist Service shall join with songs, albums, and artists tables to retrieve complete information
5. The Playlist Service shall NOT include soft-deleted songs in playlist song list
6. If song in playlist has been soft-deleted, then the Playlist Service shall exclude it from results

### Requirement 12: Duplicate Song Handling
**Objective:** As a playlist owner, I want to add the same song multiple times, so that I can create mixtapes with repeated tracks

#### Acceptance Criteria
1. When user adds song that already exists in playlist, the Playlist Service shall create new playlist_song entry
2. The Playlist Service shall NOT prevent duplicate songs in same playlist
3. The Playlist Service shall assign unique position to each playlist_song entry
4. The Playlist Service shall use surrogate key (playlist_song_id) for playlist_songs join table
5. When user removes song, the Playlist Service shall remove only specified instance (not all instances)
6. The Playlist Service shall support querying how many times specific song appears in playlist

## Non-Functional Requirements

### Performance
1. The Playlist Service shall complete playlist CRUD operations within 300ms for 95% of requests
2. The Playlist Service shall complete add/remove song operations within 200ms for 95% of requests
3. The Playlist Service shall retrieve playlists with up to 1000 songs within 500ms

### Scalability
1. The Playlist Service shall support users with up to 100 playlists each
2. The Playlist Service shall handle playlists with up to 1000 songs without degradation

### Data Integrity
1. The Database Service shall enforce foreign key constraint: owner_user_id → users.id
2. The Database Service shall enforce foreign key constraint: song_id → songs.id
3. The Database Service shall enforce NOT NULL constraints on title, owner_user_id
4. The Database Service shall use cascade delete for playlist → playlist_songs relationship

### Usability
1. The Playlist UI shall support drag-and-drop reordering of songs
2. The Playlist UI shall show loading states during mutations
3. The Playlist UI shall provide visual feedback for add/remove operations
