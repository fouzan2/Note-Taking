"""
Tag service for managing tags.
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.tag import Tag
from app.models.note import Note


async def get_all_tags(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[dict], int]:
    """
    Get all tags with note counts for a user.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (tags list with counts, total count)
    """
    # Query to get tags with note count for the user
    query = (
        select(
            Tag,
            func.count(Note.id).label("note_count")
        )
        .join(Tag.notes)
        .where(Note.user_id == user_id)
        .group_by(Tag.id)
        .order_by(func.count(Note.id).desc())
    )
    
    # Count query
    count_query = (
        select(func.count(func.distinct(Tag.id)))
        .select_from(Tag)
        .join(Tag.notes)
        .where(Note.user_id == user_id)
    )
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get tags with pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    
    tags_with_counts = []
    for tag, note_count in result:
        tags_with_counts.append({
            "id": tag.id,
            "name": tag.name,
            "created_at": tag.created_at,
            "note_count": note_count
        })
    
    return tags_with_counts, total


async def get_tag_by_name(
    db: AsyncSession,
    tag_name: str
) -> Tag:
    """
    Get tag by name.
    
    Args:
        db: Database session
        tag_name: Tag name
        
    Returns:
        Tag if found, None otherwise
    """
    result = await db.execute(
        select(Tag).where(Tag.name == tag_name)
    )
    return result.scalar_one_or_none() 