"""Repository for Dictionary entity with optimized queries."""
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from src.models.dictionary import Dictionary
from src.models.version import Version

from .base import BaseRepository


class DictionaryRepository(BaseRepository[Dictionary]):
    """
    Repository for Dictionary entities with specialized queries.

    Extends BaseRepository with dictionary-specific operations including
    name-based lookups and optimized queries with eager loading of versions.

    Example:
        repo = DictionaryRepository(db)
        dictionary = repo.get_by_name("customer_data")
        dictionaries = repo.list_with_latest_version()
    """

    def __init__(self, db: Session):
        """
        Initialize the dictionary repository.

        Args:
            db: Database session
        """
        super().__init__(Dictionary, db)

    def get_by_name(self, name: str) -> Dictionary | None:
        """
        Get a dictionary by its name.

        Args:
            name: The dictionary name

        Returns:
            The dictionary if found, None otherwise

        Example:
            dictionary = repo.get_by_name("customer_data")
            if dictionary:
                print(f"Found: {dictionary.description}")
        """
        stmt = select(Dictionary).where(Dictionary.name == name)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_id_with_versions(self, id: UUID) -> Dictionary | None:
        """
        Get a dictionary by ID with all versions eagerly loaded.

        Uses eager loading to prevent N+1 queries when accessing versions.

        Args:
            id: The dictionary UUID

        Returns:
            The dictionary with versions loaded, None if not found

        Example:
            dictionary = repo.get_by_id_with_versions(dict_id)
            for version in dictionary.versions:
                print(f"Version {version.version_number}")
        """
        stmt = (
            select(Dictionary)
            .where(Dictionary.id == id)
            .options(selectinload(Dictionary.versions))
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def list_with_latest_version(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_dir: str = "desc",
    ) -> Sequence[Dictionary]:
        """
        List dictionaries with their latest version eagerly loaded.

        Optimized query that loads dictionaries and their most recent version
        to avoid N+1 queries. Uses subquery to identify latest versions.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            order_by: Column name to order by (default: created_at)
            order_dir: Order direction ('asc' or 'desc', default: desc)

        Returns:
            Sequence of dictionaries with latest version loaded

        Example:
            dictionaries = repo.list_with_latest_version(limit=20)
            for dict in dictionaries:
                if dict.versions:
                    latest = dict.versions[0]
                    print(f"{dict.name} - v{latest.version_number}")
        """
        # Subquery to get latest version for each dictionary
        latest_version_subq = (
            select(
                Version.dictionary_id,
                func.max(Version.version_number).label("max_version"),
            )
            .group_by(Version.dictionary_id)
            .subquery()
        )

        # Main query with eager loading
        stmt = (
            select(Dictionary)
            .outerjoin(
                Version,
                (Version.dictionary_id == Dictionary.id),
            )
            .outerjoin(
                latest_version_subq,
                (latest_version_subq.c.dictionary_id == Dictionary.id)
                & (Version.version_number == latest_version_subq.c.max_version),
            )
            .options(selectinload(Dictionary.versions))
        )

        # Apply ordering
        if order_by and hasattr(Dictionary, order_by):
            from sqlalchemy import asc
            from sqlalchemy import desc as desc_func

            column = getattr(Dictionary, order_by)
            stmt = stmt.order_by(
                desc_func(column) if order_dir == "desc" else asc(column)
            )

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        result = self.db.execute(stmt)
        return result.scalars().unique().all()

    def search_by_name(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Dictionary]:
        """
        Search dictionaries by name (case-insensitive partial match).

        Args:
            search_term: Search term to match against dictionary names
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of matching dictionaries

        Example:
            results = repo.search_by_name("customer")
            # Matches "customer_data", "Customer Records", etc.
        """
        stmt = (
            select(Dictionary)
            .where(Dictionary.name.ilike(f"%{search_term}%"))
            .order_by(Dictionary.name)
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_with_version_count(self, id: UUID) -> tuple[Dictionary | None, int]:
        """
        Get a dictionary with its total version count.

        Args:
            id: The dictionary UUID

        Returns:
            Tuple of (dictionary, version_count). Dictionary is None if not found.

        Example:
            dictionary, count = repo.get_with_version_count(dict_id)
            if dictionary:
                print(f"{dictionary.name} has {count} versions")
        """
        dictionary = self.get_by_id(id)
        if dictionary is None:
            return None, 0

        # Count versions
        stmt = (
            select(func.count())
            .select_from(Version)
            .where(Version.dictionary_id == id)
        )
        result = self.db.execute(stmt)
        count = result.scalar_one()

        return dictionary, count

    def exists_by_name(self, name: str, exclude_id: UUID | None = None) -> bool:
        """
        Check if a dictionary with the given name exists.

        Args:
            name: The dictionary name to check
            exclude_id: Optional UUID to exclude (useful for updates)

        Returns:
            True if a dictionary with this name exists, False otherwise

        Example:
            # Check for duplicate before creating
            if repo.exists_by_name("customer_data"):
                raise ValueError("Dictionary name already exists")

            # Check for duplicate before updating
            if repo.exists_by_name("new_name", exclude_id=current_id):
                raise ValueError("Dictionary name already exists")
        """
        stmt = select(func.count()).select_from(Dictionary).where(Dictionary.name == name)

        if exclude_id:
            stmt = stmt.where(Dictionary.id != exclude_id)

        result = self.db.execute(stmt)
        return result.scalar_one() > 0

    def get_recent(self, limit: int = 10) -> Sequence[Dictionary]:
        """
        Get most recently created dictionaries.

        Args:
            limit: Maximum number of dictionaries to return (default: 10)

        Returns:
            Sequence of dictionaries ordered by created_at descending

        Example:
            recent = repo.get_recent(5)
            for dict in recent:
                print(f"{dict.name} - {dict.created_at}")
        """
        stmt = (
            select(Dictionary)
            .order_by(Dictionary.created_at.desc())
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def update_metadata(self, id: UUID, metadata: dict[str, Any]) -> Dictionary | None:
        """
        Update dictionary metadata field.

        Args:
            id: The dictionary UUID
            metadata: New metadata dictionary to merge or replace

        Returns:
            Updated dictionary if found, None otherwise

        Example:
            metadata = {"source": "api", "environment": "production"}
            dictionary = repo.update_metadata(dict_id, metadata)
        """
        dictionary = self.get_by_id(id)
        if dictionary is None:
            return None

        # Merge with existing metadata if present
        if dictionary.custom_metadata:
            dictionary.custom_metadata.update(metadata)
        else:
            dictionary.custom_metadata = metadata

        self.db.flush()
        self.db.refresh(dictionary)
        return dictionary

    def bulk_delete(self, ids: list[UUID]) -> int:
        """
        Delete multiple dictionaries by their IDs.

        Args:
            ids: List of dictionary UUIDs to delete

        Returns:
            Number of dictionaries deleted

        Example:
            deleted_count = repo.bulk_delete([id1, id2, id3])
            print(f"Deleted {deleted_count} dictionaries")
        """
        count = 0
        for id in ids:
            if self.delete(id):
                count += 1
        return count
