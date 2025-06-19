"""
Pydantic schemas for Note model.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from app.schemas.tag import TagResponse


class NoteBase(BaseModel):
    """Base schema for Note."""
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate note title."""
        title = v.strip()
        if not title:
            raise ValueError('Title cannot be empty')
        return title
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate note content."""
        content = v.strip()
        if not content:
            raise ValueError('Content cannot be empty')
        return content


class NoteCreate(NoteBase):
    """Schema for creating a new note."""
    tags: List[str] = Field(default_factory=list, description="List of tag names")
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate and normalize tags."""
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed per note')
        # Normalize tags: strip whitespace and convert to lowercase
        normalized_tags = []
        seen = set()
        for tag in v:
            normalized = tag.strip().lower()
            if normalized and normalized not in seen:
                normalized_tags.append(normalized)
                seen.add(normalized)
        return normalized_tags


class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = Field(None, description="List of tag names")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate note title if provided."""
        if v is not None:
            title = v.strip()
            if not title:
                raise ValueError('Title cannot be empty')
            return title
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate note content if provided."""
        if v is not None:
            content = v.strip()
            if not content:
                raise ValueError('Content cannot be empty')
            return content
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and normalize tags if provided."""
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 tags allowed per note')
            # Normalize tags
            normalized_tags = []
            seen = set()
            for tag in v:
                normalized = tag.strip().lower()
                if normalized and normalized not in seen:
                    normalized_tags.append(normalized)
                    seen.add(normalized)
            return normalized_tags
        return v


class NoteResponse(NoteBase):
    """Schema for note response."""
    id: int
    user_id: int
    tags: List[TagResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """Schema for paginated note list response."""
    notes: List[NoteResponse]
    total: int
    page: int
    per_page: int
    total_pages: int 