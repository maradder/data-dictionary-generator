"""Dictionary model - represents a data dictionary."""
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import BigInteger, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.core.database import TZDateTime

if TYPE_CHECKING:
    from models.version import Version


class Dictionary(Base):
    """
    Dictionary model representing a data dictionary.

    A dictionary is the top-level entity that contains metadata about
    a JSON data source and its analyzed structure across versions.
    """

    __tablename__ = "dictionaries"

    # Use String(36) for UUID to support both SQLite and PostgreSQL
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_file_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    total_records_analyzed: Mapped[int | None] = mapped_column(Integer, nullable=True)
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
    # Use generic JSON type (works with both PostgreSQL and SQLite JSON1 extension)
    custom_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    versions: Mapped[list["Version"]] = relationship(
        "Version", back_populates="dictionary", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Dictionary."""
        return f"<Dictionary(id={self.id}, name={self.name})>"
