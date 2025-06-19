"""
Tag management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.tag import TagWithNoteCount
from app.services import tag_service
from app.api.deps import get_current_user, PaginationParams
from app.models.user import User

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=List[TagWithNoteCount])
async def get_tags(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TagWithNoteCount]:
    """
    Get all tags used by the current user with note counts.
    
    Args:
        pagination: Pagination parameters
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of tags with note counts
    """
    tags, _ = await tag_service.get_all_tags(
        db,
        current_user.id,
        skip=pagination.offset,
        limit=pagination.limit
    )
    
    return [
        TagWithNoteCount(
            id=tag["id"],
            name=tag["name"],
            created_at=tag["created_at"],
            note_count=tag["note_count"]
        )
        for tag in tags
    ] 