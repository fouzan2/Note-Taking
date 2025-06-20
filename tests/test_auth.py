"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "SecurePassword123!"
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=user_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user: dict):
    """Test registration with duplicate username."""
    user_data = {
        "username": test_user["user"]["username"],
        "email": "different@example.com",
        "password": "DifferentPassword123!"
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=user_data
    )
    
    assert response.status_code == 409
    error_data = response.json()
    assert error_data["success"] is False
    assert "Username already registered" in error_data["error"]["message"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: dict):
    """Test successful login."""
    login_data = {
        "username": test_user["user"]["username"],
        "password": test_user["user"]["password"]
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data
    )
    
    assert response.status_code == 401
    error_data = response.json()
    assert error_data["success"] is False
    assert "Incorrect username or password" in error_data["error"]["message"]


@pytest.mark.asyncio
async def test_get_current_user(authenticated_client: AsyncClient):
    """Test getting current user information."""
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/auth/me"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "username" in data
    assert "email" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected endpoint without authentication."""
    response = await client.get(
        f"{settings.API_V1_STR}/auth/me"
    )
    
    assert response.status_code == 401 