"""
Tests for note CRUD operations.
"""
import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_create_note(authenticated_client: AsyncClient):
    """Test creating a new note."""
    note_data = {
        "title": "Test Note",
        "content": "This is a test note content",
        "tags": ["test", "python", "fastapi"]
    }
    
    response = await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json=note_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert len(data["tags"]) == 3
    assert all(tag["name"] in note_data["tags"] for tag in data["tags"])
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_note_without_tags(authenticated_client: AsyncClient):
    """Test creating a note without tags."""
    note_data = {
        "title": "Note Without Tags",
        "content": "This note has no tags"
    }
    
    response = await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json=note_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert data["tags"] == []


@pytest.mark.asyncio
async def test_create_note_validation_errors(authenticated_client: AsyncClient):
    """Test note creation with invalid data."""
    # Missing required fields
    response = await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json={}
    )
    assert response.status_code == 422
    
    # Empty title
    response = await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "", "content": "Content"}
    )
    assert response.status_code == 422
    
    # Empty content
    response = await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "Title", "content": ""}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_note(authenticated_client: AsyncClient):
    """Test retrieving a single note."""
    # Create a note first
    note_data = {
        "title": "Note to Retrieve",
        "content": "This note will be retrieved",
        "tags": ["retrieval", "test"]
    }
    
    create_response = await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json=note_data
    )
    created_note = create_response.json()
    note_id = created_note["id"]
    
    # Retrieve the note
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/{note_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == note_data["title"]
    assert data["content"] == note_data["content"]
    assert len(data["tags"]) == 2


@pytest.mark.asyncio
async def test_get_nonexistent_note(authenticated_client: AsyncClient):
    """Test retrieving a note that doesn't exist."""
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/999999"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_all_notes(authenticated_client: AsyncClient):
    """Test retrieving all notes with pagination."""
    # First, check if there are any existing notes and clean them up
    response = await authenticated_client.get(f"{settings.API_V1_STR}/notes/")
    if response.status_code == 200:
        existing_notes = response.json()["notes"]
        # Delete any existing notes to ensure clean test
        for note in existing_notes:
            await authenticated_client.delete(f"{settings.API_V1_STR}/notes/{note['id']}")
    
    # Create multiple notes
    for i in range(5):
        note_data = {
            "title": f"Note {i}",
            "content": f"Content for note {i}",
            "tags": [f"tag{i}"]
        }
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Get all notes
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["notes"]) == 5
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["per_page"] == 20  # Default per_page is 20
    assert data["total_pages"] == 1


@pytest.mark.asyncio
async def test_get_notes_pagination(authenticated_client: AsyncClient):
    """Test note pagination."""
    # First, check if there are any existing notes and clean them up
    response = await authenticated_client.get(f"{settings.API_V1_STR}/notes/")
    if response.status_code == 200:
        existing_notes = response.json()["notes"]
        # Delete any existing notes to ensure clean test
        for note in existing_notes:
            await authenticated_client.delete(f"{settings.API_V1_STR}/notes/{note['id']}")
    
    # Create 15 notes
    for i in range(15):
        note_data = {
            "title": f"Note {i}",
            "content": f"Content for note {i}"
        }
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Get first page with per_page=10
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/?page=1&per_page=10"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["notes"]) == 10
    assert data["total"] == 15
    assert data["total_pages"] == 2
    assert data["per_page"] == 10
    
    # Get second page
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/?page=2&per_page=10"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["notes"]) == 5
    assert data["page"] == 2
    assert data["per_page"] == 10


@pytest.mark.asyncio
async def test_update_note(authenticated_client: AsyncClient):
    """Test updating a note."""
    # Create a note
    note_data = {
        "title": "Original Title",
        "content": "Original content",
        "tags": ["original"]
    }
    
    create_response = await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json=note_data
    )
    note_id = create_response.json()["id"]
    
    # Update the note
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "tags": ["updated", "modified"]
    }
    
    response = await authenticated_client.put(
        f"{settings.API_V1_STR}/notes/{note_id}",
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]
    assert len(data["tags"]) == 2
    assert all(tag["name"] in update_data["tags"] for tag in data["tags"])


@pytest.mark.asyncio
async def test_delete_note(authenticated_client: AsyncClient):
    """Test deleting a note."""
    # Create a note
    note_data = {
        "title": "Note to Delete",
        "content": "This note will be deleted"
    }
    
    create_response = await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json=note_data
    )
    note_id = create_response.json()["id"]
    
    # Delete the note
    response = await authenticated_client.delete(
        f"{settings.API_V1_STR}/notes/{note_id}"
    )
    
    assert response.status_code == 204
    
    # Verify the note is deleted
    get_response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/{note_id}"
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_note(authenticated_client: AsyncClient):
    """Test deleting a note that doesn't exist."""
    response = await authenticated_client.delete(
        f"{settings.API_V1_STR}/notes/999999"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_note_access(client: AsyncClient):
    """Test accessing notes without authentication."""
    # Try to create a note without auth
    note_data = {
        "title": "Unauthorized Note",
        "content": "This should fail"
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/notes/",
        json=note_data
    )
    assert response.status_code == 401
    
    # Try to get notes without auth
    response = await client.get(f"{settings.API_V1_STR}/notes/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_note_isolation(client: AsyncClient):
    """Test that users can only access their own notes."""
    # Create first user and note
    user1_data = {
        "username": "user1",
        "email": "user1@example.com",
        "password": "Password123!"
    }
    
    await client.post(f"{settings.API_V1_STR}/auth/register", json=user1_data)
    login_response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": user1_data["username"], "password": user1_data["password"]}
    )
    user1_token = login_response.json()["access_token"]
    
    # Create note as user1
    headers1 = {"Authorization": f"Bearer {user1_token}"}
    note_response = await client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "User1 Note", "content": "Private note"},
        headers=headers1
    )
    user1_note_id = note_response.json()["id"]
    
    # Create second user
    user2_data = {
        "username": "user2",
        "email": "user2@example.com",
        "password": "Password123!"
    }
    
    await client.post(f"{settings.API_V1_STR}/auth/register", json=user2_data)
    login_response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": user2_data["username"], "password": user2_data["password"]}
    )
    user2_token = login_response.json()["access_token"]
    
    # Try to access user1's note as user2
    headers2 = {"Authorization": f"Bearer {user2_token}"}
    response = await client.get(
        f"{settings.API_V1_STR}/notes/{user1_note_id}",
        headers=headers2
    )
    # The API returns 403 when trying to access another user's note
    assert response.status_code == 403
    
    # Verify user2 doesn't see user1's notes in list
    response = await client.get(
        f"{settings.API_V1_STR}/notes/",
        headers=headers2
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0 