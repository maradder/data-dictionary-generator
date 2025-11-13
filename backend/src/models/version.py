"""Version model - represents a version of a dictionary."""
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.core.database import TZDateTime

if TYPE_CHECKING:
    from models.dictionary import Dictionary
    from models.field import Field


class Version(Base):
    """
    Version model representing a specific version of a dictionary.

    Versions track schema changes over time and enable historical analysis.
    """

    __tablename__ = "versions"

    # Use String(36) for UUID to support both SQLite and PostgreSQL
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dictionary_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("dictionaries.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    # Use TZDateTime for cross-database timezone-aware datetimes
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=lambda: datetime.now(timezone.utc)
    )
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Use generic JSON type (works with both PostgreSQL and SQLite JSON1 extension)
    processing_stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    dictionary: Mapped["Dictionary"] = relationship("Dictionary", back_populates="versions")
    fields: Mapped[list["Field"]] = relationship(
        "Field", back_populates="version", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Version."""
        return f"<Version(id={self.id}, dictionary_id={self.dictionary_id}, version={self.version_number})>"
