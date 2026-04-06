"""
Test Pydantic schemas for playlists - Task 2.1, 2.2
Requirements: 1, 3, 5, 7, 8
"""
import pytest
from pydantic import ValidationError


def test_playlist_create_request_valid():
    """
    RED phase - Test PlaylistCreateRequest with valid data
    Task 2.1: Define PlaylistCreateRequest schema
    """
    from app.schemas.playlist import PlaylistCreateRequest

    # Valid request
    request = PlaylistCreateRequest(
        title="My Playlist",
        is_public=False
    )

    assert request.title == "My Playlist"
    assert request.is_public == False


def test_playlist_create_request_default_privacy():
    """
    RED phase - Test default is_public=False
    Task 2.1: Default privacy should be private
    Requirement: 8 (Privacy Control)
    """
    from app.schemas.playlist import PlaylistCreateRequest

    request = PlaylistCreateRequest(title="Test")

    assert request.is_public == False, "Default should be private"


def test_playlist_create_request_validates_title_min_length():
    """
    RED phase - Test title minimum length validation
    Task 2.1: Validate title 1-200 chars
    Requirement: 1 (Playlist Creation)
    """
    from app.schemas.playlist import PlaylistCreateRequest

    # Empty title should fail
    with pytest.raises(ValidationError) as exc_info:
        PlaylistCreateRequest(title="")

    errors = exc_info.value.errors()
    assert any("title" in str(err) for err in errors)


def test_playlist_create_request_validates_title_max_length():
    """
    RED phase - Test title maximum length validation
    Task 2.1: Validate title max 200 chars
    """
    from app.schemas.playlist import PlaylistCreateRequest

    # 201 character title should fail
    long_title = "A" * 201
    with pytest.raises(ValidationError) as exc_info:
        PlaylistCreateRequest(title=long_title)

    errors = exc_info.value.errors()
    assert any("title" in str(err) for err in errors)


def test_playlist_create_request_trims_whitespace():
    """
    RED phase - Test whitespace trimming
    Task 2.1: Trim whitespace from title
    """
    from app.schemas.playlist import PlaylistCreateRequest

    request = PlaylistCreateRequest(title="  Padded Title  ")

    assert request.title == "Padded Title", "Should trim whitespace"


def test_playlist_create_request_rejects_whitespace_only():
    """
    RED phase - Test whitespace-only rejection
    Task 2.1: Reject whitespace-only strings
    """
    from app.schemas.playlist import PlaylistCreateRequest

    with pytest.raises(ValidationError) as exc_info:
        PlaylistCreateRequest(title="   ")

    errors = exc_info.value.errors()
    assert any("title" in str(err) for err in errors)


def test_playlist_update_request_optional_fields():
    """
    RED phase - Test PlaylistUpdateRequest with optional fields
    Task 2.1: Both title and is_public should be optional
    Requirement: 3 (Playlist Update)
    """
    from app.schemas.playlist import PlaylistUpdateRequest

    # Update only title
    request1 = PlaylistUpdateRequest(title="New Title")
    assert request1.title == "New Title"
    assert request1.is_public is None

    # Update only privacy
    request2 = PlaylistUpdateRequest(is_public=True)
    assert request2.title is None
    assert request2.is_public == True

    # Update both
    request3 = PlaylistUpdateRequest(title="Another", is_public=False)
    assert request3.title == "Another"
    assert request3.is_public == False


def test_add_song_request_validation():
    """
    RED phase - Test AddSongRequest schema
    Task 2.1: Define AddSongRequest with song_id
    Requirement: 5 (Add Song to Playlist)
    """
    from app.schemas.playlist import AddSongRequest

    request = AddSongRequest(song_id=42)

    assert request.song_id == 42
    assert isinstance(request.song_id, int)


def test_reorder_song_request_validation():
    """
    RED phase - Test ReorderSongRequest schema
    Task 2.1: Define ReorderSongRequest with position >= 1
    Requirement: 7 (Reorder Songs)
    """
    from app.schemas.playlist import ReorderSongRequest

    # Valid position
    request = ReorderSongRequest(new_position=5)
    assert request.new_position == 5

    # Position must be >= 1
    with pytest.raises(ValidationError) as exc_info:
        ReorderSongRequest(new_position=0)

    errors = exc_info.value.errors()
    assert any(err['type'] == 'greater_than_equal' for err in errors)

    # Negative position should fail
    with pytest.raises(ValidationError):
        ReorderSongRequest(new_position=-1)


def test_playlist_response_schema():
    """
    RED phase - Test PlaylistResponse schema
    Task 2.2: Define PlaylistResponse with all fields
    Requirement: 2 (Playlist Retrieval)
    """
    from app.schemas.playlist import PlaylistResponse
    from datetime import datetime

    response = PlaylistResponse(
        id=1,
        title="Test Playlist",
        owner_user_id=42,
        is_public=False,
        songs_count=10,
        total_duration_seconds=1800,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    assert response.id == 1
    assert response.title == "Test Playlist"
    assert response.owner_user_id == 42
    assert response.is_public == False
    assert response.songs_count == 10
    assert response.total_duration_seconds == 1800
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)


def test_playlist_song_response_schema():
    """
    RED phase - Test PlaylistSongResponse schema
    Task 2.2: Define PlaylistSongResponse with full song details
    Requirement: 11 (Playlist Song Details)
    """
    from app.schemas.playlist import PlaylistSongResponse

    response = PlaylistSongResponse(
        playlist_song_id=1,
        position=1,
        song_id=42,
        song_title="Test Song",
        artist_name="Test Artist",
        album_title="Test Album",
        duration_seconds=180
    )

    assert response.playlist_song_id == 1
    assert response.position == 1
    assert response.song_id == 42
    assert response.song_title == "Test Song"
    assert response.artist_name == "Test Artist"
    assert response.album_title == "Test Album"
    assert response.duration_seconds == 180


def test_playlist_list_response_schema():
    """
    RED phase - Test PlaylistListResponse for pagination
    Task 2.2: Define PlaylistListResponse with pagination
    Requirement: 2 (Playlist Retrieval)
    """
    from app.schemas.playlist import PlaylistListResponse, PlaylistResponse
    from datetime import datetime

    playlist = PlaylistResponse(
        id=1,
        title="Test",
        owner_user_id=1,
        is_public=False,
        songs_count=0,
        total_duration_seconds=0,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    response = PlaylistListResponse(
        items=[playlist],
        total=1,
        page=1,
        page_size=20,
        total_pages=1
    )

    assert len(response.items) == 1
    assert response.total == 1
    assert response.page == 1
    assert response.page_size == 20
    assert response.total_pages == 1
