"""Annotation model - represents user or AI-generated annotations for fields."""
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.core.database import TZDateTime

if TYPE_CHECKING:
    from models.field import Field


class Annotation(Base):
    """
    Annotation model for field descriptions and metadata.

    Annotations provide human-readable descriptions, business names,
    and additional context for fields, either user-created or AI-generated.
    """

    __tablename__ = "annotations"

    # Use String(36) for UUID to support both SQLite and PostgreSQL
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    field_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    business_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Use generic JSON type (works with both PostgreSQL and SQLite JSON1 extension)
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Use TZDateTime for cross-database timezone-aware datetimes
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=lambda: datetime.now(timezone.utc)
    )
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        TZDateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    updated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    field: Mapped["Field"] = relationship("Field", back_populates="annotations")

    def __repr__(self) -> str:
        """String representation of Annotation."""
        return f"<Annotation(id={self.id}, field_id={self.field_id}, ai_generated={self.is_ai_generated})>"
