"""
Note management endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import RedisCache
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, NoteListResponse
from app.services import note_service
from app.api.deps import get_current_user, PaginationParams
from app.models.user import User

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=NoteResponse, status_code=201)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteResponse:
    """
    Create a new note with associated tags.
    
    Args:
        note_data: Note creation data including title, content, and tags
        current_user: Authenticated user from JWT token
        db: Database session dependency
        
    Returns:
        Created note with associated metadata
        
    Raises:
        ValidationError: Invalid input data
        AuthenticationError: Invalid or expired token
    """
    note = await note_service.create_note(db, note_data, current_user.id)
    
    # Cache the created note
    cache_key = f"note:{note.id}:user:{current_user.id}"
    await RedisCache.set(cache_key, note.__dict__, ttl=600)  # Cache for 10 minutes
    
    return NoteResponse.from_orm(note)


@router.get("/", response_model=NoteListResponse)
async def get_notes(
    tag: Optional[str] = Query(None, description="Filter notes by tag name"),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteListResponse:
    """
    Get all notes for the current user with optional tag filtering.
    
    Args:
        tag: Optional tag name to filter by
        pagination: Pagination parameters
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Paginated list of notes
    """
    # Create cache key for this specific query
    cache_key = f"notes:user:{current_user.id}:page:{pagination.page}:tag:{tag or 'all'}"
    
    # Try to get from cache first
    cached_result = await RedisCache.get(cache_key)
    if cached_result:
        return NoteListResponse(**cached_result)
    
    # Get from database
    notes, total = await note_service.get_notes(
        db,
        current_user.id,
        skip=pagination.offset,
        limit=pagination.limit,
        tag_filter=tag
    )
    
    total_pages = (total + pagination.per_page - 1) // pagination.per_page
    
    result = NoteListResponse(
        notes=[NoteResponse.from_orm(note) for note in notes],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=total_pages
    )
    
    # Cache the result for 5 minutes
    await RedisCache.set(cache_key, result.dict(), ttl=300)
    
    return result


@router.get("/search", response_model=NoteListResponse)
async def search_notes(
    q: str = Query(..., min_length=1, description="Search query"),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteListResponse:
    """
    Search notes by title or content.
    
    Args:
        q: Search query
        pagination: Pagination parameters
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Paginated list of matching notes
    """
    notes, total = await note_service.search_notes(
        db,
        current_user.id,
        q,
        skip=pagination.offset,
        limit=pagination.limit
    )
    
    total_pages = (total + pagination.per_page - 1) // pagination.per_page
    
    return NoteListResponse(
        notes=[NoteResponse.from_orm(note) for note in notes],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        total_pages=total_pages
    )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteResponse:
    """
    Get a specific note by ID with Redis caching.
    
    Args:
        note_id: Note ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Note details
        
    Raises:
        NotFoundError: Note not found
        AuthorizationError: User doesn't own the note
    """
    # Try to get from cache first
    cache_key = f"note:{note_id}:user:{current_user.id}"
    cached_note = await RedisCache.get(cache_key)
    
    if cached_note:
        return NoteResponse(**cached_note)
    
    # Get from database
    note = await note_service.get_note_by_id(db, note_id, current_user.id)
    
    # Cache the note for 10 minutes
    await RedisCache.set(cache_key, note.__dict__, ttl=600)
    
    return NoteResponse.from_orm(note)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteResponse:
    """
    Update a note's title, content, or tags.
    
    Args:
        note_id: Note ID
        note_update: Update data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Updated note
        
    Raises:
        NotFoundError: Note not found
        AuthorizationError: User doesn't own the note
        ValidationError: Invalid update data
    """
    note = await note_service.update_note(db, note_id, note_update, current_user.id)
    
    # Invalidate caches for this note and user's note lists
    cache_key = f"note:{note_id}:user:{current_user.id}"
    await RedisCache.delete(cache_key)
    
    # Clear user's note list caches (all pages and tag filters)
    await RedisCache.clear_pattern(f"notes:user:{current_user.id}:*")
    
    # Cache the updated note
    await RedisCache.set(cache_key, note.__dict__, ttl=600)
    
    return NoteResponse.from_orm(note)


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a note.
    
    Args:
        note_id: Note ID
        current_user: Authenticated user
        db: Database session
        
    Raises:
        NotFoundError: Note not found
        AuthorizationError: User doesn't own the note
    """
    await note_service.delete_note(db, note_id, current_user.id)
    
    # Invalidate caches for this note and user's note lists
    cache_key = f"note:{note_id}:user:{current_user.id}"
    await RedisCache.delete(cache_key)
    
    # Clear user's note list caches (all pages and tag filters)
    await RedisCache.clear_pattern(f"notes:user:{current_user.id}:*") 