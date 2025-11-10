"""Dictionary model - represents a data dictionary."""
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from models.version import Version


class Dictionary(Base):
    """
    Dictionary model representing a data dictionary.

    A dictionary is the top-level entity that contains metadata about
    a JSON data source and its analyzed structure across versions.
    """

    __tablename__ = "dictionaries"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_file_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    total_records_analyzed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow
    )
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    custom_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    versions: Mapped[list["Version"]] = relationship(
        "Version", back_populates="dictionary", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Dictionary."""
        return f"<Dictionary(id={self.id}, name={self.name})>"
