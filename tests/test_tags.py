"""
Tests for tag management operations.
"""
import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_get_all_tags(authenticated_client: AsyncClient):
    """Test getting all tags for a user."""
    # Create notes with various tags
    notes_data = [
        {
            "title": "Python Note",
            "content": "Python programming",
            "tags": ["python", "programming", "backend"]
        },
        {
            "title": "FastAPI Note",
            "content": "FastAPI framework",
            "tags": ["fastapi", "python", "web"]
        },
        {
            "title": "Docker Note",
            "content": "Docker containers",
            "tags": ["docker", "devops", "containers"]
        }
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Get all tags
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/tags/"
    )
    
    assert response.status_code == 200
    tags = response.json()
    
    # Should have 8 unique tags
    assert len(tags) == 8
    
    # Check that all tags are present
    tag_names = [tag["name"] for tag in tags]
    expected_tags = ["python", "programming", "backend", "fastapi", "web", "docker", "devops", "containers"]
    assert all(tag in tag_names for tag in expected_tags)
    
    # Each tag should have id, name, and note_count
    for tag in tags:
        assert "id" in tag
        assert "name" in tag
        assert "note_count" in tag


@pytest.mark.asyncio
async def test_tag_usage_count(authenticated_client: AsyncClient):
    """Test that tag usage count is correct."""
    # Create notes with overlapping tags
    notes_data = [
        {"title": "Note 1", "content": "Content 1", "tags": ["python", "test"]},
        {"title": "Note 2", "content": "Content 2", "tags": ["python", "web"]},
        {"title": "Note 3", "content": "Content 3", "tags": ["python", "test", "web"]},
        {"title": "Note 4", "content": "Content 4", "tags": ["docker"]}
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Get all tags
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/tags/"
    )
    
    assert response.status_code == 200
    tags = response.json()
    
    # Create a dict for easy lookup
    tag_counts = {tag["name"]: tag["note_count"] for tag in tags}
    
    # Verify usage counts
    assert tag_counts["python"] == 3
    assert tag_counts["test"] == 2
    assert tag_counts["web"] == 2
    assert tag_counts["docker"] == 1


@pytest.mark.asyncio
async def test_filter_notes_by_single_tag(authenticated_client: AsyncClient):
    """Test filtering notes by a single tag."""
    # Create notes with different tags
    notes_data = [
        {"title": "Python Tutorial", "content": "Learn Python", "tags": ["python", "tutorial"]},
        {"title": "JavaScript Guide", "content": "Learn JS", "tags": ["javascript", "tutorial"]},
        {"title": "Python Web Dev", "content": "Python for web", "tags": ["python", "web"]},
        {"title": "Docker Basics", "content": "Docker intro", "tags": ["docker", "devops"]}
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Filter by 'python' tag
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/?tag=python"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    
    # Verify all returned notes have the 'python' tag
    for note in data["notes"]:
        tag_names = [tag["name"] for tag in note["tags"]]
        assert "python" in tag_names


@pytest.mark.asyncio
async def test_filter_notes_by_nonexistent_tag(authenticated_client: AsyncClient):
    """Test filtering notes by a tag that doesn't exist."""
    # Create some notes
    note_data = {
        "title": "Test Note",
        "content": "Test content",
        "tags": ["existing", "tag"]
    }
    
    await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json=note_data
    )
    
    # Filter by non-existent tag
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/?tag=nonexistent"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["notes"] == []


@pytest.mark.asyncio
async def test_tags_case_insensitive(authenticated_client: AsyncClient):
    """Test that tags are case-insensitive."""
    # Create notes with different case tags
    notes_data = [
        {"title": "Note 1", "content": "Content", "tags": ["Python"]},
        {"title": "Note 2", "content": "Content", "tags": ["python"]},
        {"title": "Note 3", "content": "Content", "tags": ["PYTHON"]}
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Get all tags
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/tags/"
    )
    
    assert response.status_code == 200
    tags = response.json()
    
    # Should only have one 'python' tag (lowercase)
    python_tags = [tag for tag in tags if tag["name"].lower() == "python"]
    assert len(python_tags) == 1
    assert python_tags[0]["note_count"] == 3


@pytest.mark.asyncio
async def test_tag_cleanup_on_note_deletion(authenticated_client: AsyncClient):
    """Test that tag usage count updates when notes are deleted."""
    # Create notes with tags
    note1_response = await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "Note 1", "content": "Content", "tags": ["test", "python"]}
    )
    note1_id = note1_response.json()["id"]
    
    await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "Note 2", "content": "Content", "tags": ["test"]}
    )
    
    # Check initial tag counts
    response = await authenticated_client.get(f"{settings.API_V1_STR}/tags/")
    tags = {tag["name"]: tag["note_count"] for tag in response.json()}
    assert tags["test"] == 2
    assert tags["python"] == 1
    
    # Delete first note
    await authenticated_client.delete(f"{settings.API_V1_STR}/notes/{note1_id}")
    
    # Check updated tag counts
    response = await authenticated_client.get(f"{settings.API_V1_STR}/tags/")
    tags = {tag["name"]: tag["note_count"] for tag in response.json()}
    assert tags["test"] == 1
    # 'python' tag should not appear anymore (note_count = 0)
    assert "python" not in tags


@pytest.mark.asyncio
async def test_tag_update_on_note_update(authenticated_client: AsyncClient):
    """Test that tags update correctly when a note is updated."""
    # Create a note
    create_response = await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "Note", "content": "Content", "tags": ["old1", "old2"]}
    )
    note_id = create_response.json()["id"]
    
    # Update the note with new tags
    await authenticated_client.put(
        f"{settings.API_V1_STR}/notes/{note_id}",
        json={"title": "Updated Note", "content": "Updated", "tags": ["new1", "new2", "new3"]}
    )
    
    # Check tags
    response = await authenticated_client.get(f"{settings.API_V1_STR}/tags/")
    tags = {tag["name"]: tag["note_count"] for tag in response.json()}
    
    # Old tags should not exist
    assert "old1" not in tags
    assert "old2" not in tags
    
    # New tags should exist
    assert tags["new1"] == 1
    assert tags["new2"] == 1
    assert tags["new3"] == 1


@pytest.mark.asyncio
async def test_empty_tags_not_created(authenticated_client: AsyncClient):
    """Test that empty or whitespace tags are not created."""
    # Create a note with empty/whitespace tags
    await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "Note", "content": "Content", "tags": ["valid", "", "  ", "another"]}
    )
    
    # Get all tags
    response = await authenticated_client.get(f"{settings.API_V1_STR}/tags/")
    tags = response.json()
    
    # Should only have 2 valid tags
    assert len(tags) == 2
    tag_names = [tag["name"] for tag in tags]
    assert "valid" in tag_names
    assert "another" in tag_names


@pytest.mark.asyncio
async def test_tag_isolation_between_users(client: AsyncClient):
    """Test that users only see their own tags."""
    # Create first user and add notes with tags
    user1_data = {
        "username": "taguser1",
        "email": "taguser1@example.com",
        "password": "Password123!"
    }
    
    await client.post(f"{settings.API_V1_STR}/auth/register", json=user1_data)
    login_response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": user1_data["username"], "password": user1_data["password"]}
    )
    user1_token = login_response.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {user1_token}"}
    
    # User1 creates notes with tags
    await client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "User1 Note", "content": "Content", "tags": ["user1tag", "shared"]},
        headers=headers1
    )
    
    # Create second user
    user2_data = {
        "username": "taguser2",
        "email": "taguser2@example.com",
        "password": "Password123!"
    }
    
    await client.post(f"{settings.API_V1_STR}/auth/register", json=user2_data)
    login_response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": user2_data["username"], "password": user2_data["password"]}
    )
    user2_token = login_response.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {user2_token}"}
    
    # User2 creates notes with tags
    await client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "User2 Note", "content": "Content", "tags": ["user2tag", "shared"]},
        headers=headers2
    )
    
    # User1 should only see their tags
    response = await client.get(f"{settings.API_V1_STR}/tags/", headers=headers1)
    user1_tags = [tag["name"] for tag in response.json()]
    assert "user1tag" in user1_tags
    assert "shared" in user1_tags
    assert "user2tag" not in user1_tags
    
    # User2 should only see their tags
    response = await client.get(f"{settings.API_V1_STR}/tags/", headers=headers2)
    user2_tags = [tag["name"] for tag in response.json()]
    assert "user2tag" in user2_tags
    assert "shared" in user2_tags
    assert "user1tag" not in user2_tags 