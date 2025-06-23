"""
API dependencies for authentication and common functionality.
"""
from typing import Optional
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.utils.exceptions import AuthenticationError
from app.schemas.user import TokenData

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extract and validate current user from JWT token.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise AuthenticationError("Invalid authentication credentials")
    
    # Check token type
    token_type = payload.get("type")
    if token_type != "access":
        raise AuthenticationError("Invalid token type")
    
    # Extract user ID
    user_id = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")
    
    # Get user from database
    try:
        user_id = int(user_id)
    except ValueError:
        raise AuthenticationError("Invalid user ID in token")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise AuthenticationError("User not found")
    
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user
        
    Raises:
        AuthenticationError: If user is not active
    """
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user


class PaginationParams:
    """
    Common pagination parameters.
    """
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        per_page: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        """
        Initialize pagination parameters.
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
        """
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page
        self.limit = per_page 