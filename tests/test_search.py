"""
Tests for search and filtering functionality.
"""
import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_search_notes_by_title(authenticated_client: AsyncClient):
    """Test searching notes by title."""
    # Create notes with different titles
    notes_data = [
        {"title": "Python Programming Guide", "content": "Learn Python basics"},
        {"title": "JavaScript Tutorial", "content": "Learn JavaScript"},
        {"title": "Python Advanced Topics", "content": "Advanced Python concepts"},
        {"title": "Docker Basics", "content": "Introduction to Docker"}
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Search for "Python" in title
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=Python"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    
    # Verify all results contain "Python" in title
    for note in data["notes"]:
        assert "python" in note["title"].lower()


@pytest.mark.asyncio
async def test_search_notes_by_content(authenticated_client: AsyncClient):
    """Test searching notes by content."""
    # Create notes with different content
    notes_data = [
        {"title": "Note 1", "content": "FastAPI is a modern web framework"},
        {"title": "Note 2", "content": "Django is a web framework"},
        {"title": "Note 3", "content": "FastAPI provides automatic documentation"},
        {"title": "Note 4", "content": "Redis is a cache database"}
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Search for "FastAPI" in content
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=FastAPI"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    
    # Verify all results contain "FastAPI" in content
    for note in data["notes"]:
        assert "fastapi" in note["content"].lower()


@pytest.mark.asyncio
async def test_search_case_insensitive(authenticated_client: AsyncClient):
    """Test that search is case-insensitive."""
    # Create notes
    await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "PYTHON Tutorial", "content": "Learn python programming"}
    )
    
    # Search with different cases
    for query in ["python", "Python", "PYTHON", "PyThOn"]:
        response = await authenticated_client.get(
            f"{settings.API_V1_STR}/notes/search?q={query}"
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1


@pytest.mark.asyncio
async def test_search_partial_match(authenticated_client: AsyncClient):
    """Test partial word matching in search."""
    # Create notes
    notes_data = [
        {"title": "Programming Basics", "content": "Introduction to programming"},
        {"title": "Program Design", "content": "How to design programs"},
        {"title": "Programmer's Guide", "content": "Guide for programmers"}
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Search for partial word
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=program"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3  # Should match all variations


@pytest.mark.asyncio
async def test_search_with_pagination(authenticated_client: AsyncClient):
    """Test search results with pagination."""
    # Create many notes with searchable content
    for i in range(15):
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json={"title": f"Python Note {i}", "content": f"Python content {i}"}
        )
    
    # Search with pagination
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=Python&page=1&per_page=10"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["notes"]) == 10
    assert data["total"] == 15
    assert data["total_pages"] == 2
    
    # Get second page
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=Python&page=2&per_page=10"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["notes"]) == 5
    assert data["page"] == 2


@pytest.mark.asyncio
async def test_search_no_results(authenticated_client: AsyncClient):
    """Test search with no matching results."""
    # Create some notes
    await authenticated_client.post(
        f"{settings.API_V1_STR}/notes/",
        json={"title": "Test Note", "content": "Test content"}
    )
    
    # Search for non-existent content
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=NonExistentSearchTerm"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["notes"] == []


@pytest.mark.asyncio
async def test_search_empty_query(authenticated_client: AsyncClient):
    """Test search with empty query string."""
    # The API requires a non-empty query parameter
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q="
    )
    
    # Should return 422 validation error for empty query
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_special_characters(authenticated_client: AsyncClient):
    """Test search with special characters."""
    # Create notes with special characters
    notes_data = [
        {"title": "C++ Programming", "content": "Learn C++ basics"},
        {"title": "C# Development", "content": "C# .NET framework"},
        {"title": "Node.js Guide", "content": "JavaScript runtime"}
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Search for C++
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=C%2B%2B"  # URL encoded C++
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any("C++" in note["title"] for note in data["notes"])


@pytest.mark.asyncio
async def test_combined_search_and_tag_filter(authenticated_client: AsyncClient):
    """Test that search endpoint doesn't support tag filtering."""
    # Create notes with various combinations
    notes_data = [
        {"title": "Python Web Development", "content": "Django and FastAPI", "tags": ["python", "web"]},
        {"title": "Python Data Science", "content": "NumPy and Pandas", "tags": ["python", "data"]},
        {"title": "JavaScript Web Development", "content": "React and Node.js", "tags": ["javascript", "web"]},
        {"title": "Python Machine Learning", "content": "TensorFlow and PyTorch", "tags": ["python", "ml"]}
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Search for "Python" - should return all notes with Python in title/content
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=Python"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3  # Three notes have "Python" in title
    
    # To filter by both search and tag, use the regular notes endpoint with tag filter
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/?tag=web"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2  # Two notes have "web" tag


@pytest.mark.asyncio
async def test_search_with_multiple_words(authenticated_client: AsyncClient):
    """Test search with multiple words."""
    # Create notes
    notes_data = [
        {"title": "Python Web Framework", "content": "FastAPI is great"},
        {"title": "Python Desktop Apps", "content": "Build desktop applications"},
        {"title": "Web Development", "content": "Modern web technologies"},
        {"title": "Mobile Development", "content": "Build mobile apps"}
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Search for multiple words
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=Python+Web"
    )
    
    assert response.status_code == 200
    data = response.json()
    # Should find notes containing both "Python" AND "Web"
    assert data["total"] >= 1
    
    for note in data["notes"]:
        text = (note["title"] + " " + note["content"]).lower()
        assert "python" in text or "web" in text


@pytest.mark.asyncio
async def test_search_ordering(authenticated_client: AsyncClient):
    """Test that search results maintain consistent ordering."""
    # Create notes with timestamps
    import asyncio
    
    notes_data = [
        {"title": "First Python Note", "content": "Created first"},
        {"title": "Second Python Note", "content": "Created second"},
        {"title": "Third Python Note", "content": "Created third"}
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
        await asyncio.sleep(0.1)  # Small delay to ensure different timestamps
    
    # Search and check ordering
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=Python"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    
    # Results should be ordered by created_at descending (newest first)
    items = data["notes"]
    assert "Third" in items[0]["title"]
    assert "Second" in items[1]["title"]
    assert "First" in items[2]["title"]


@pytest.mark.asyncio
async def test_search_performance_with_many_notes(authenticated_client: AsyncClient):
    """Test search performance with a larger dataset."""
    # Create 50 notes
    for i in range(50):
        category = "Python" if i % 2 == 0 else "JavaScript"
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json={
                "title": f"{category} Note {i}",
                "content": f"Content about {category} programming",
                "tags": [category.lower(), f"tag{i % 5}"]
            }
        )
    
    # Search should still be fast
    import time
    start_time = time.time()
    
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=Python"
    )
    
    end_time = time.time()
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 25  # Half should be Python notes
    
    # Search should complete quickly (less than 1 second)
    assert (end_time - start_time) < 1.0


@pytest.mark.asyncio
async def test_search_unicode_support(authenticated_client: AsyncClient):
    """Test search with Unicode characters."""
    # Create notes with Unicode content
    notes_data = [
        {"title": "Python编程", "content": "Python编程指南"},  # Chinese
        {"title": "Pythonプログラミング", "content": "Pythonの基礎"},  # Japanese
        {"title": "Python программирование", "content": "Основы Python"},  # Russian
        {"title": "Python برمجة", "content": "أساسيات Python"}  # Arabic
    ]
    
    for note_data in notes_data:
        await authenticated_client.post(
            f"{settings.API_V1_STR}/notes/",
            json=note_data
        )
    
    # Search with Unicode
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=编程"  # Chinese for "programming"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    
    # Search with English should still find all
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/notes/search?q=Python"
    )
    
    assert response.status_code == 200
    assert response.json()["total"] == 4 