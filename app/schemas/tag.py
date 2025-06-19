"""
Pydantic schemas for Tag model.
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class TagBase(BaseModel):
    """Base schema for Tag."""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    
    @field_validator('name')
    @classmethod
    def validate_and_normalize_name(cls, v: str) -> str:
        """Validate and normalize tag name."""
        # Remove extra whitespace and convert to lowercase
        normalized = v.strip().lower()
        if not normalized:
            raise ValueError('Tag name cannot be empty')
        if len(normalized) > 50:
            raise ValueError('Tag name cannot exceed 50 characters')
        return normalized


class TagCreate(TagBase):
    """Schema for creating a new tag."""
    pass


class TagResponse(TagBase):
    """Schema for tag response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TagWithNoteCount(TagResponse):
    """Schema for tag with note count."""
    note_count: int = Field(..., description="Number of notes associated with this tag") 