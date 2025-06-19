"""
Note model with support for tags.
"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from app.core.database import Base


# Association table for many-to-many relationship between notes and tags
note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)


class Note(Base):
    """Note model for storing user notes."""
    
    __tablename__ = "notes"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notes")
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=note_tags,
        back_populates="notes",
        lazy="selectin"  # Eager loading for tags
    )
    
    def __repr__(self) -> str:
        return f"<Note(id={self.id}, title={self.title}, user_id={self.user_id})>" 