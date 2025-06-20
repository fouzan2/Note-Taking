"""
Authentication endpoints for user registration and login.
"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.schemas.user import UserCreate, UserResponse, Token
from app.services import auth_service
from app.utils.exceptions import AuthenticationError
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        ConflictError: If username or email already exists
    """
    user = await auth_service.create_user(db, user_data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Login user and return access tokens.
    
    Args:
        form_data: OAuth2 login form data
        db: Database session
        
    Returns:
        Access and refresh tokens
        
    Raises:
        AuthenticationError: If credentials are invalid
    """
    # Authenticate user
    user = await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    
    if not user:
        raise AuthenticationError("Incorrect username or password")
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse.model_validate(current_user) 