"""Field model - represents a field in a dictionary version."""
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.core.database import TZDateTime

if TYPE_CHECKING:
    from models.annotation import Annotation
    from models.version import Version


class Field(Base):
    """
    Field model representing a field in a dictionary version.

    Fields contain detailed metadata about individual data elements
    including type information, statistics, and quality metrics.
    """

    __tablename__ = "fields"

    # Use String(36) for UUID to support both SQLite and PostgreSQL
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("versions.id", ondelete="CASCADE"), nullable=False
    )
    field_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    nesting_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    data_type: Mapped[str] = mapped_column(String(50), nullable=False)
    semantic_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_nullable: Mapped[bool] = mapped_column(Boolean, default=True)
    is_array: Mapped[bool] = mapped_column(Boolean, default=False)
    array_item_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Use generic JSON type (works with both PostgreSQL and SQLite JSON1 extension)
    sample_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    null_count: Mapped[int] = mapped_column(Integer, default=0)
    null_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    distinct_count: Mapped[int] = mapped_column(Integer, default=0)
    cardinality_ratio: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    min_value: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    max_value: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    mean_value: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    median_value: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    std_dev: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    percentile_25: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    percentile_50: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    percentile_75: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    is_pii: Mapped[bool] = mapped_column(Boolean, default=False)
    pii_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    # Use TZDateTime for cross-database timezone-aware datetimes
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=lambda: datetime.now(timezone.utc)
    )
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    version: Mapped["Version"] = relationship("Version", back_populates="fields")
    annotations: Mapped[list["Annotation"]] = relationship(
        "Annotation", back_populates="field", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Field."""
        return f"<Field(id={self.id}, path={self.field_path}, type={self.data_type})>"
