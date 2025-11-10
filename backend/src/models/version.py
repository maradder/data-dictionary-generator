"""Version model - represents a version of a dictionary."""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from models.dictionary import Dictionary
    from models.field import Field


class Version(Base):
    """
    Version model representing a specific version of a dictionary.

    Versions track schema changes over time and enable historical analysis.
    """

    __tablename__ = "versions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    dictionary_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dictionaries.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    schema_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_stats: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    dictionary: Mapped["Dictionary"] = relationship("Dictionary", back_populates="versions")
    fields: Mapped[list["Field"]] = relationship(
        "Field", back_populates="version", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Version."""
        return f"<Version(id={self.id}, dictionary_id={self.dictionary_id}, version={self.version_number})>"
