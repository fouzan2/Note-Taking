"""
Note service for managing notes and their tags.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.note import Note
from app.models.tag import Tag
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate
from app.utils.exceptions import NotFoundError, AuthorizationError


async def create_note(
    db: AsyncSession,
    note_data: NoteCreate,
    user_id: int
) -> Note:
    """
    Create a new note with tags.
    
    Args:
        db: Database session
        note_data: Note creation data
        user_id: ID of the user creating the note
        
    Returns:
        Created note with tags
    """
    # Create note
    note = Note(
        title=note_data.title,
        content=note_data.content,
        user_id=user_id
    )
    
    # Handle tags
    if note_data.tags:
        # Get or create tags
        for tag_name in note_data.tags:
            # Check if tag exists
            result = await db.execute(
                select(Tag).where(Tag.name == tag_name)
            )
            tag = result.scalar_one_or_none()
            
            if not tag:
                # Create new tag
                tag = Tag(name=tag_name)
                db.add(tag)
            
            note.tags.append(tag)
    
    db.add(note)
    await db.commit()
    await db.refresh(note)
    
    return note


async def get_notes(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    tag_filter: Optional[str] = None
) -> tuple[List[Note], int]:
    """
    Get notes for a user with optional tag filtering.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        tag_filter: Optional tag name to filter by
        
    Returns:
        Tuple of (notes list, total count)
    """
    # Base query
    query = select(Note).where(Note.user_id == user_id)
    count_query = select(func.count()).select_from(Note).where(Note.user_id == user_id)
    
    # Apply tag filter if provided
    if tag_filter:
        query = query.join(Note.tags).where(Tag.name == tag_filter)
        count_query = count_query.join(Note.tags).where(Tag.name == tag_filter)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get notes with pagination
    query = query.options(selectinload(Note.tags)).order_by(Note.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    notes = result.scalars().unique().all()
    
    return notes, total


async def get_note_by_id(
    db: AsyncSession,
    note_id: int,
    user_id: int
) -> Note:
    """
    Get a specific note by ID.
    
    Args:
        db: Database session
        note_id: Note ID
        user_id: User ID (for authorization)
        
    Returns:
        Note if found and authorized
        
    Raises:
        NotFoundError: If note not found
        AuthorizationError: If user doesn't own the note
    """
    result = await db.execute(
        select(Note)
        .where(Note.id == note_id)
        .options(selectinload(Note.tags))
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise NotFoundError(f"Note with id {note_id} not found")
    
    if note.user_id != user_id:
        raise AuthorizationError("You don't have permission to access this note")
    
    return note


async def update_note(
    db: AsyncSession,
    note_id: int,
    note_update: NoteUpdate,
    user_id: int
) -> Note:
    """
    Update a note.
    
    Args:
        db: Database session
        note_id: Note ID
        note_update: Update data
        user_id: User ID (for authorization)
        
    Returns:
        Updated note
        
    Raises:
        NotFoundError: If note not found
        AuthorizationError: If user doesn't own the note
    """
    # Get existing note
    note = await get_note_by_id(db, note_id, user_id)
    
    # Update fields if provided
    if note_update.title is not None:
        note.title = note_update.title
    
    if note_update.content is not None:
        note.content = note_update.content
    
    # Update tags if provided
    if note_update.tags is not None:
        # Clear existing tags
        note.tags.clear()
        
        # Add new tags
        for tag_name in note_update.tags:
            # Check if tag exists
            result = await db.execute(
                select(Tag).where(Tag.name == tag_name)
            )
            tag = result.scalar_one_or_none()
            
            if not tag:
                # Create new tag
                tag = Tag(name=tag_name)
                db.add(tag)
            
            note.tags.append(tag)
    
    await db.commit()
    await db.refresh(note)
    
    return note


async def delete_note(
    db: AsyncSession,
    note_id: int,
    user_id: int
) -> None:
    """
    Delete a note.
    
    Args:
        db: Database session
        note_id: Note ID
        user_id: User ID (for authorization)
        
    Raises:
        NotFoundError: If note not found
        AuthorizationError: If user doesn't own the note
    """
    # Get note (this will check authorization)
    note = await get_note_by_id(db, note_id, user_id)
    
    # Delete note
    await db.delete(note)
    await db.commit()


async def search_notes(
    db: AsyncSession,
    user_id: int,
    query: str,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[Note], int]:
    """
    Search notes by title or content.
    
    Args:
        db: Database session
        user_id: User ID
        query: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Tuple of (notes list, total count)
    """
    # Search in title and content
    search_pattern = f"%{query}%"
    
    # Count query
    count_query = select(func.count()).select_from(Note).where(
        and_(
            Note.user_id == user_id,
            or_(
                Note.title.ilike(search_pattern),
                Note.content.ilike(search_pattern)
            )
        )
    )
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Search query with pagination
    search_query = select(Note).where(
        and_(
            Note.user_id == user_id,
            or_(
                Note.title.ilike(search_pattern),
                Note.content.ilike(search_pattern)
            )
        )
    ).options(selectinload(Note.tags)).order_by(Note.created_at.desc())
    
    search_query = search_query.offset(skip).limit(limit)
    
    result = await db.execute(search_query)
    notes = result.scalars().unique().all()
    
    return notes, total 