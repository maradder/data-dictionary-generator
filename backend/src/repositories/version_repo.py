"""Repository for Version entity with schema management operations."""
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session, selectinload

from src.models.version import Version

from .base import BaseRepository


class VersionRepository(BaseRepository[Version]):
    """
    Repository for Version entities with specialized queries.

    Extends BaseRepository with version-specific operations including
    dictionary-based lookups, latest version retrieval, schema hash
    management, and version creation logic.

    Example:
        repo = VersionRepository(db)
        latest = repo.get_latest_version(dictionary_id)
        version = repo.create_new_version(dictionary_id, schema_hash)
    """

    def __init__(self, db: Session):
        """
        Initialize the version repository.

        Args:
            db: Database session
        """
        super().__init__(Version, db)

    def get_by_dictionary(
        self,
        dictionary_id: UUID,
        skip: int = 0,
        limit: int | None = None,
        order_dir: str = "desc",
    ) -> Sequence[Version]:
        """
        Get all versions for a specific dictionary.

        Args:
            dictionary_id: The dictionary UUID
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return (None for all)
            order_dir: Order direction by version number ('asc' or 'desc')

        Returns:
            Sequence of versions ordered by version number

        Example:
            versions = repo.get_by_dictionary(dict_id)
            for version in versions:
                print(f"Version {version.version_number}: {version.created_at}")
        """
        stmt = (
            select(Version)
            .where(Version.dictionary_id == dictionary_id)
            .order_by(
                desc(Version.version_number)
                if order_dir == "desc"
                else Version.version_number
            )
            .offset(skip)
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_latest_version(self, dictionary_id: UUID) -> Version | None:
        """
        Get the latest version for a dictionary.

        Args:
            dictionary_id: The dictionary UUID

        Returns:
            The latest version if found, None otherwise

        Example:
            latest = repo.get_latest_version(dict_id)
            if latest:
                print(f"Latest version: {latest.version_number}")
                print(f"Schema hash: {latest.schema_hash}")
        """
        stmt = (
            select(Version)
            .where(Version.dictionary_id == dictionary_id)
            .order_by(desc(Version.version_number))
            .limit(1)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_latest_version_with_fields(self, dictionary_id: UUID) -> Version | None:
        """
        Get the latest version with fields eagerly loaded.

        Uses eager loading to prevent N+1 queries when accessing fields.

        Args:
            dictionary_id: The dictionary UUID

        Returns:
            The latest version with fields loaded, None if not found

        Example:
            latest = repo.get_latest_version_with_fields(dict_id)
            if latest:
                for field in latest.fields:
                    print(f"{field.field_path}: {field.data_type}")
        """
        stmt = (
            select(Version)
            .where(Version.dictionary_id == dictionary_id)
            .options(selectinload(Version.fields))
            .order_by(desc(Version.version_number))
            .limit(1)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def create_new_version(
        self,
        dictionary_id: UUID,
        schema_hash: str,
        created_by: str | None = None,
        notes: str | None = None,
        processing_stats: dict | None = None,
    ) -> Version:
        """
        Create a new version with auto-incremented version number.

        Automatically determines the next version number by finding the
        highest existing version number and incrementing it.

        Args:
            dictionary_id: The dictionary UUID
            schema_hash: Hash of the schema for this version
            created_by: Optional user who created this version
            notes: Optional notes about this version
            processing_stats: Optional processing statistics

        Returns:
            The newly created version

        Example:
            version = repo.create_new_version(
                dictionary_id=dict_id,
                schema_hash="abc123...",
                created_by="user@example.com",
                notes="Updated schema with new fields"
            )
            print(f"Created version {version.version_number}")
        """
        # Get the latest version number
        latest = self.get_latest_version(dictionary_id)
        next_version_number = (latest.version_number + 1) if latest else 1

        # Create the new version
        version = Version(
            dictionary_id=dictionary_id,
            version_number=next_version_number,
            schema_hash=schema_hash,
            created_by=created_by,
            notes=notes,
            processing_stats=processing_stats,
        )

        self.db.add(version)
        self.db.flush()
        self.db.refresh(version)

        return version

    def get_by_schema_hash(
        self, dictionary_id: UUID, schema_hash: str
    ) -> Version | None:
        """
        Find a version by schema hash within a dictionary.

        Useful for detecting if a schema has been seen before to avoid
        creating duplicate versions.

        Args:
            dictionary_id: The dictionary UUID
            schema_hash: The schema hash to search for

        Returns:
            The version with matching schema hash, None if not found

        Example:
            # Check if schema already exists
            existing = repo.get_by_schema_hash(dict_id, new_hash)
            if existing:
                print(f"Schema unchanged since version {existing.version_number}")
            else:
                # Create new version
                version = repo.create_new_version(dict_id, new_hash)
        """
        stmt = select(Version).where(
            and_(
                Version.dictionary_id == dictionary_id,
                Version.schema_hash == schema_hash,
            )
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_by_version_number(
        self, dictionary_id: UUID, version_number: int
    ) -> Version | None:
        """
        Get a specific version by its number within a dictionary.

        Args:
            dictionary_id: The dictionary UUID
            version_number: The version number to retrieve

        Returns:
            The version if found, None otherwise

        Example:
            version = repo.get_by_version_number(dict_id, 5)
            if version:
                print(f"Version 5 created at {version.created_at}")
        """
        stmt = select(Version).where(
            and_(
                Version.dictionary_id == dictionary_id,
                Version.version_number == version_number,
            )
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_version_with_fields(
        self, dictionary_id: UUID, version_number: int
    ) -> Version | None:
        """
        Get a specific version with fields eagerly loaded.

        Args:
            dictionary_id: The dictionary UUID
            version_number: The version number to retrieve

        Returns:
            The version with fields loaded, None if not found

        Example:
            version = repo.get_version_with_fields(dict_id, 3)
            if version:
                print(f"Version 3 has {len(version.fields)} fields")
        """
        stmt = (
            select(Version)
            .where(
                and_(
                    Version.dictionary_id == dictionary_id,
                    Version.version_number == version_number,
                )
            )
            .options(selectinload(Version.fields))
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def count_by_dictionary(self, dictionary_id: UUID) -> int:
        """
        Count total versions for a dictionary.

        Args:
            dictionary_id: The dictionary UUID

        Returns:
            Total number of versions

        Example:
            count = repo.count_by_dictionary(dict_id)
            print(f"Dictionary has {count} versions")
        """
        stmt = (
            select(func.count())
            .select_from(Version)
            .where(Version.dictionary_id == dictionary_id)
        )
        result = self.db.execute(stmt)
        return result.scalar_one()

    def get_version_range(
        self,
        dictionary_id: UUID,
        start_version: int,
        end_version: int,
    ) -> Sequence[Version]:
        """
        Get versions within a specific range (inclusive).

        Args:
            dictionary_id: The dictionary UUID
            start_version: Starting version number (inclusive)
            end_version: Ending version number (inclusive)

        Returns:
            Sequence of versions in the range, ordered by version number

        Example:
            # Get versions 5 through 10
            versions = repo.get_version_range(dict_id, 5, 10)
            for version in versions:
                print(f"Version {version.version_number}")
        """
        stmt = (
            select(Version)
            .where(
                and_(
                    Version.dictionary_id == dictionary_id,
                    Version.version_number >= start_version,
                    Version.version_number <= end_version,
                )
            )
            .order_by(Version.version_number)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_recent_versions(
        self, dictionary_id: UUID, limit: int = 5
    ) -> Sequence[Version]:
        """
        Get the most recent versions for a dictionary.

        Args:
            dictionary_id: The dictionary UUID
            limit: Maximum number of versions to return (default: 5)

        Returns:
            Sequence of recent versions ordered by version number descending

        Example:
            recent = repo.get_recent_versions(dict_id, limit=3)
            for version in recent:
                print(f"v{version.version_number}: {version.created_at}")
        """
        return self.get_by_dictionary(
            dictionary_id=dictionary_id, limit=limit, order_dir="desc"
        )

    def schema_exists(self, dictionary_id: UUID, schema_hash: str) -> bool:
        """
        Check if a schema hash already exists for a dictionary.

        Args:
            dictionary_id: The dictionary UUID
            schema_hash: The schema hash to check

        Returns:
            True if schema exists, False otherwise

        Example:
            if repo.schema_exists(dict_id, new_hash):
                print("Schema unchanged - no new version needed")
            else:
                print("Schema changed - creating new version")
        """
        stmt = (
            select(func.count())
            .select_from(Version)
            .where(
                and_(
                    Version.dictionary_id == dictionary_id,
                    Version.schema_hash == schema_hash,
                )
            )
        )
        result = self.db.execute(stmt)
        return result.scalar_one() > 0

    def update_processing_stats(
        self, id: UUID, processing_stats: dict
    ) -> Version | None:
        """
        Update processing statistics for a version.

        Args:
            id: The version UUID
            processing_stats: New processing stats to merge or replace

        Returns:
            Updated version if found, None otherwise

        Example:
            stats = {
                "records_processed": 10000,
                "processing_time_ms": 5432,
                "errors": 0
            }
            version = repo.update_processing_stats(version_id, stats)
        """
        version = self.get_by_id(id)
        if version is None:
            return None

        # Merge with existing stats if present
        if version.processing_stats:
            version.processing_stats.update(processing_stats)
        else:
            version.processing_stats = processing_stats

        self.db.flush()
        self.db.refresh(version)
        return version

    def delete_old_versions(
        self, dictionary_id: UUID, keep_latest: int = 10
    ) -> int:
        """
        Delete old versions, keeping only the latest N versions.

        Args:
            dictionary_id: The dictionary UUID
            keep_latest: Number of latest versions to keep (default: 10)

        Returns:
            Number of versions deleted

        Example:
            # Keep only the 5 most recent versions
            deleted = repo.delete_old_versions(dict_id, keep_latest=5)
            print(f"Deleted {deleted} old versions")
        """
        # Get all versions ordered by version number descending
        versions = self.get_by_dictionary(dictionary_id, order_dir="desc")

        # If we have fewer versions than keep_latest, don't delete anything
        if len(versions) <= keep_latest:
            return 0

        # Delete versions beyond keep_latest
        deleted_count = 0
        for version in versions[keep_latest:]:
            if self.delete(version.id):
                deleted_count += 1

        return deleted_count
