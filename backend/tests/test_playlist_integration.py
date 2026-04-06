"""
Integration and End-to-End Tests - Task 7 (Optional)
Complete playlist lifecycle and edge case testing
Requirements: 1-12
"""
import pytest
from httpx import AsyncClient
from datetime import datetime


class TestPlaylistLifecycle:
    """Test complete playlist lifecycle - Task 7.1"""

    @pytest.mark.asyncio
    async def test_complete_playlist_lifecycle(self, async_client: AsyncClient, test_song):
        """
        Task 7.1: Complete lifecycle test
        Create → Add songs → Reorder → Remove → Toggle privacy → Delete
        """
        # Register and login user
        register_data = {
            "email": "lifecycle@test.com",
            "password": "TestPass123!"
        }
        await async_client.post("/auth/register", json=register_data)

        login_response = await async_client.post("/auth/login", json=register_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create playlist
        create_response = await async_client.post(
            "/playlists",
            json={"title": "My Lifecycle Playlist", "is_public": False},
            headers=headers
        )
        assert create_response.status_code == 201
        playlist_id = create_response.json()["id"]

        # 2. Add 3 songs
        song_ids = []
        for i in range(3):
            add_response = await async_client.post(
                f"/playlists/{playlist_id}/songs",
                json={"song_id": test_song.id},
                headers=headers
            )
            assert add_response.status_code == 200
            songs = add_response.json()["songs_count"]
            assert songs == i + 1

        # 3. Get playlist and extract playlist_song_ids
        get_response = await async_client.get(f"/playlists/{playlist_id}", headers=headers)
        assert get_response.status_code == 200
        songs_list = get_response.json()["songs"]
        assert len(songs_list) == 3

        # Verify positions are sequential
        positions = [s["position"] for s in songs_list]
        assert positions == [1, 2, 3]

        # 4. Reorder: move position 3 to position 1
        playlist_song_id_3 = songs_list[2]["playlist_song_id"]
        reorder_response = await async_client.patch(
            f"/playlists/{playlist_id}/songs/{playlist_song_id_3}/reorder",
            json={"new_position": 1},
            headers=headers
        )
        assert reorder_response.status_code == 200

        # Verify new order
        get_response = await async_client.get(f"/playlists/{playlist_id}", headers=headers)
        songs_reordered = get_response.json()["songs"]
        new_order_ids = [s["playlist_song_id"] for s in songs_reordered]
        assert new_order_ids[0] == playlist_song_id_3

        # 5. Remove a song
        playlist_song_id_to_remove = songs_reordered[1]["playlist_song_id"]
        remove_response = await async_client.delete(
            f"/playlists/{playlist_id}/songs/{playlist_song_id_to_remove}",
            headers=headers
        )
        assert remove_response.status_code == 200
        assert remove_response.json()["songs_count"] == 2

        # 6. Toggle privacy (private → public)
        update_response = await async_client.put(
            f"/playlists/{playlist_id}",
            json={"is_public": True},
            headers=headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["is_public"] == True

        # 7. Delete playlist
        delete_response = await async_client.delete(f"/playlists/{playlist_id}", headers=headers)
        assert delete_response.status_code == 204

        # Verify deleted
        get_after_delete = await async_client.get(f"/playlists/{playlist_id}", headers=headers)
        assert get_after_delete.status_code == 404


class TestPlaylistPrivacy:
    """Test playlist privacy enforcement - Task 7.2"""

    @pytest.mark.asyncio
    async def test_privacy_enforcement(self, async_client: AsyncClient):
        """
        Task 7.2: Privacy control test
        Owner creates private → Guest gets 403 → Toggle public → Guest gets 200
        """
        # Register owner
        owner_data = {"email": "owner@test.com", "password": "TestPass123!"}
        await async_client.post("/auth/register", json=owner_data)
        login_owner = await async_client.post("/auth/login", json=owner_data)
        owner_token = login_owner.json()["access_token"]
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        # Register guest
        guest_data = {"email": "guest@test.com", "password": "TestPass123!"}
        await async_client.post("/auth/register", json=guest_data)
        login_guest = await async_client.post("/auth/login", json=guest_data)
        guest_token = login_guest.json()["access_token"]
        guest_headers = {"Authorization": f"Bearer {guest_token}"}

        # Owner creates private playlist
        create_response = await async_client.post(
            "/playlists",
            json={"title": "Private Playlist", "is_public": False},
            headers=owner_headers
        )
        playlist_id = create_response.json()["id"]

        # Guest tries to access private playlist → 403
        guest_access = await async_client.get(f"/playlists/{playlist_id}", headers=guest_headers)
        assert guest_access.status_code == 403

        # Owner toggles to public
        await async_client.put(
            f"/playlists/{playlist_id}",
            json={"is_public": True},
            headers=owner_headers
        )

        # Guest can now access → 200
        guest_access_public = await async_client.get(f"/playlists/{playlist_id}", headers=guest_headers)
        assert guest_access_public.status_code == 200

    @pytest.mark.asyncio
    async def test_public_playlist_listing(self, async_client: AsyncClient):
        """
        Task 7.2: Public listing test
        Create 5 playlists (3 public, 2 private) → GET /playlists/public returns 3
        """
        # Register user
        user_data = {"email": "listtest@test.com", "password": "TestPass123!"}
        await async_client.post("/auth/register", json=user_data)
        login_response = await async_client.post("/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create 3 public playlists
        for i in range(3):
            await async_client.post(
                "/playlists",
                json={"title": f"Public {i+1}", "is_public": True},
                headers=headers
            )

        # Create 2 private playlists
        for i in range(2):
            await async_client.post(
                "/playlists",
                json={"title": f"Private {i+1}", "is_public": False},
                headers=headers
            )

        # Get public playlists
        public_response = await async_client.get("/playlists/public")
        assert public_response.status_code == 200
        public_data = public_response.json()
        assert public_data["total"] == 3


class TestDuplicateSongs:
    """Test duplicate song handling - Task 7.3"""

    @pytest.mark.asyncio
    async def test_duplicate_song_handling(self, async_client: AsyncClient, test_song):
        """
        Task 7.3: Duplicate songs test
        Add same song 3 times → Verify 3 distinct entries → Remove 1 → Verify 2 remain
        """
        # Setup user
        user_data = {"email": "duptest@test.com", "password": "TestPass123!"}
        await async_client.post("/auth/register", json=user_data)
        login_response = await async_client.post("/auth/login", json=user_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create playlist
        create_response = await async_client.post(
            "/playlists",
            json={"title": "Duplicate Test"},
            headers=headers
        )
        playlist_id = create_response.json()["id"]

        # Add same song 3 times
        playlist_song_ids = []
        for i in range(3):
            add_response = await async_client.post(
                f"/playlists/{playlist_id}/songs",
                json={"song_id": test_song.id},
                headers=headers
            )
            assert add_response.status_code == 200

        # Get songs and verify 3 distinct entries
        get_response = await async_client.get(f"/playlists/{playlist_id}", headers=headers)
        songs = get_response.json()["songs"]
        assert len(songs) == 3

        # All have same song_id but different playlist_song_ids
        assert all(s["song_id"] == test_song.id for s in songs)
        playlist_song_ids = [s["playlist_song_id"] for s in songs]
        assert len(set(playlist_song_ids)) == 3  # All unique

        # Remove 1 instance
        remove_response = await async_client.delete(
            f"/playlists/{playlist_id}/songs/{playlist_song_ids[1]}",
            headers=headers
        )
        assert remove_response.status_code == 200
        assert remove_response.json()["songs_count"] == 2

        # Reorder 1 instance
        reorder_response = await async_client.patch(
            f"/playlists/{playlist_id}/songs/{playlist_song_ids[2]}/reorder",
            json={"new_position": 1},
            headers=headers
        )
        assert reorder_response.status_code == 200


class TestOwnershipEnforcement:
    """Test ownership verification - Task 7.1 (multiple users)"""

    @pytest.mark.asyncio
    async def test_non_owner_cannot_mutate(self, async_client: AsyncClient):
        """
        Task 7.1: Ownership enforcement
        Owner can mutate, non-owner receives 403
        """
        # Register owner
        owner_data = {"email": "owner2@test.com", "password": "TestPass123!"}
        await async_client.post("/auth/register", json=owner_data)
        login_owner = await async_client.post("/auth/login", json=owner_data)
        owner_token = login_owner.json()["access_token"]
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        # Register non-owner
        non_owner_data = {"email": "nonowner@test.com", "password": "TestPass123!"}
        await async_client.post("/auth/register", json=non_owner_data)
        login_non_owner = await async_client.post("/auth/login", json=non_owner_data)
        non_owner_token = login_non_owner.json()["access_token"]
        non_owner_headers = {"Authorization": f"Bearer {non_owner_token}"}

        # Owner creates playlist
        create_response = await async_client.post(
            "/playlists",
            json={"title": "Owner Test"},
            headers=owner_headers
        )
        playlist_id = create_response.json()["id"]

        # Non-owner tries to update → 403
        update_attempt = await async_client.put(
            f"/playlists/{playlist_id}",
            json={"title": "Hacked"},
            headers=non_owner_headers
        )
        assert update_attempt.status_code == 403

        # Non-owner tries to delete → 403
        delete_attempt = await async_client.delete(
            f"/playlists/{playlist_id}",
            headers=non_owner_headers
        )
        assert delete_attempt.status_code == 403

        # Owner can update
        owner_update = await async_client.put(
            f"/playlists/{playlist_id}",
            json={"title": "Updated by Owner"},
            headers=owner_headers
        )
        assert owner_update.status_code == 200
