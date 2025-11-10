"""Repository for Field entity with optimized queries and bulk operations."""
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from src.models.field import Field

from .base import BaseRepository


class FieldRepository(BaseRepository[Field]):
    """
    Repository for Field entities with specialized queries.

    Extends BaseRepository with field-specific operations including
    version-based lookups, filtering by type/PII status, and bulk operations
    with optimized queries to avoid N+1 problems.

    Example:
        repo = FieldRepository(db)
        fields = repo.get_by_version(version_id)
        pii_fields = repo.get_pii_fields(version_id)
        repo.bulk_insert_fields(field_data_list)
    """

    def __init__(self, db: Session):
        """
        Initialize the field repository.

        Args:
            db: Database session
        """
        super().__init__(Field, db)

    def get_by_version(
        self,
        version_id: UUID,
        skip: int = 0,
        limit: int | None = None,
        order_by: str = "position",
    ) -> Sequence[Field]:
        """
        Get all fields for a specific version.

        Args:
            version_id: The version UUID
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return (None for all)
            order_by: Column to order by (default: position)

        Returns:
            Sequence of fields for the version

        Example:
            fields = repo.get_by_version(version_id, limit=100)
            for field in fields:
                print(f"{field.field_path}: {field.data_type}")
        """
        stmt = select(Field).where(Field.version_id == version_id)

        # Apply ordering
        if order_by and hasattr(Field, order_by):
            stmt = stmt.order_by(getattr(Field, order_by))

        # Apply pagination
        stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_fields_with_annotations(
        self, version_id: UUID, skip: int = 0, limit: int | None = None
    ) -> Sequence[Field]:
        """
        Get fields with annotations eagerly loaded to prevent N+1 queries.

        Args:
            version_id: The version UUID
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return (None for all)

        Returns:
            Sequence of fields with annotations loaded

        Example:
            fields = repo.get_fields_with_annotations(version_id)
            for field in fields:
                for annotation in field.annotations:
                    print(f"{field.field_path}: {annotation.description}")
        """
        stmt = (
            select(Field)
            .where(Field.version_id == version_id)
            .options(selectinload(Field.annotations))
            .order_by(Field.position)
            .offset(skip)
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        result = self.db.execute(stmt)
        return result.scalars().all()

    def bulk_insert_fields(self, fields_data: list[dict]) -> list[Field]:
        """
        Bulk insert multiple fields efficiently.

        Uses SQLAlchemy's bulk insert optimization for better performance
        when inserting many fields at once.

        Args:
            fields_data: List of dictionaries containing field data

        Returns:
            List of created Field instances

        Example:
            fields_data = [
                {
                    "version_id": version_id,
                    "field_path": "user.name",
                    "field_name": "name",
                    "data_type": "string",
                    "position": 0,
                },
                {
                    "version_id": version_id,
                    "field_path": "user.age",
                    "field_name": "age",
                    "data_type": "integer",
                    "position": 1,
                },
            ]
            fields = repo.bulk_insert_fields(fields_data)
        """
        # Create Field instances
        fields = [Field(**data) for data in fields_data]

        # Add all to session
        self.db.add_all(fields)
        self.db.flush()

        # Refresh to get IDs and defaults
        for field in fields:
            self.db.refresh(field)

        return fields

    def get_by_type(
        self, version_id: UUID, data_type: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Field]:
        """
        Get fields of a specific data type within a version.

        Args:
            version_id: The version UUID
            data_type: The data type to filter by (e.g., "string", "integer")
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of fields with the specified data type

        Example:
            string_fields = repo.get_by_type(version_id, "string")
            numeric_fields = repo.get_by_type(version_id, "integer")
        """
        stmt = (
            select(Field)
            .where(and_(Field.version_id == version_id, Field.data_type == data_type))
            .order_by(Field.position)
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_by_semantic_type(
        self, version_id: UUID, semantic_type: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Field]:
        """
        Get fields of a specific semantic type within a version.

        Args:
            version_id: The version UUID
            semantic_type: The semantic type to filter by (e.g., "email", "phone")
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of fields with the specified semantic type

        Example:
            email_fields = repo.get_by_semantic_type(version_id, "email")
            date_fields = repo.get_by_semantic_type(version_id, "date")
        """
        stmt = (
            select(Field)
            .where(
                and_(
                    Field.version_id == version_id, Field.semantic_type == semantic_type
                )
            )
            .order_by(Field.position)
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_pii_fields(
        self, version_id: UUID, skip: int = 0, limit: int | None = None
    ) -> Sequence[Field]:
        """
        Get all PII (Personally Identifiable Information) fields in a version.

        Args:
            version_id: The version UUID
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return (None for all)

        Returns:
            Sequence of PII fields

        Example:
            pii_fields = repo.get_pii_fields(version_id)
            for field in pii_fields:
                print(f"PII: {field.field_path} ({field.pii_type})")
        """
        stmt = (
            select(Field)
            .where(and_(Field.version_id == version_id, Field.is_pii))
            .order_by(Field.confidence_score.desc())
            .offset(skip)
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_by_pii_type(
        self, version_id: UUID, pii_type: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Field]:
        """
        Get fields of a specific PII type within a version.

        Args:
            version_id: The version UUID
            pii_type: The PII type to filter by (e.g., "email", "ssn", "phone")
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of fields with the specified PII type

        Example:
            ssn_fields = repo.get_by_pii_type(version_id, "ssn")
            credit_card_fields = repo.get_by_pii_type(version_id, "credit_card")
        """
        stmt = (
            select(Field)
            .where(
                and_(
                    Field.version_id == version_id,
                    Field.is_pii,
                    Field.pii_type == pii_type,
                )
            )
            .order_by(Field.confidence_score.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_nullable_fields(
        self, version_id: UUID, skip: int = 0, limit: int | None = None
    ) -> Sequence[Field]:
        """
        Get all nullable fields in a version.

        Args:
            version_id: The version UUID
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return (None for all)

        Returns:
            Sequence of nullable fields

        Example:
            nullable = repo.get_nullable_fields(version_id)
        """
        stmt = (
            select(Field)
            .where(and_(Field.version_id == version_id, Field.is_nullable))
            .order_by(Field.null_percentage.desc())
            .offset(skip)
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_array_fields(
        self, version_id: UUID, skip: int = 0, limit: int | None = None
    ) -> Sequence[Field]:
        """
        Get all array fields in a version.

        Args:
            version_id: The version UUID
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return (None for all)

        Returns:
            Sequence of array fields

        Example:
            arrays = repo.get_array_fields(version_id)
            for field in arrays:
                print(f"Array: {field.field_path} of {field.array_item_type}")
        """
        stmt = (
            select(Field)
            .where(and_(Field.version_id == version_id, Field.is_array))
            .order_by(Field.position)
            .offset(skip)
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_by_nesting_level(
        self, version_id: UUID, nesting_level: int, skip: int = 0, limit: int = 100
    ) -> Sequence[Field]:
        """
        Get fields at a specific nesting level within a version.

        Args:
            version_id: The version UUID
            nesting_level: The nesting level (0 for top-level)
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of fields at the specified nesting level

        Example:
            top_level = repo.get_by_nesting_level(version_id, 0)
            nested = repo.get_by_nesting_level(version_id, 2)
        """
        stmt = (
            select(Field)
            .where(
                and_(
                    Field.version_id == version_id,
                    Field.nesting_level == nesting_level,
                )
            )
            .order_by(Field.position)
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_by_field_path(self, version_id: UUID, field_path: str) -> Field | None:
        """
        Get a field by its exact field path within a version.

        Args:
            version_id: The version UUID
            field_path: The exact field path (e.g., "user.address.city")

        Returns:
            The field if found, None otherwise

        Example:
            field = repo.get_by_field_path(version_id, "user.email")
            if field:
                print(f"Type: {field.data_type}, PII: {field.is_pii}")
        """
        stmt = select(Field).where(
            and_(Field.version_id == version_id, Field.field_path == field_path)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def search_by_name(
        self, version_id: UUID, search_term: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Field]:
        """
        Search fields by name (case-insensitive partial match) within a version.

        Args:
            version_id: The version UUID
            search_term: Search term to match against field names
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of matching fields

        Example:
            results = repo.search_by_name(version_id, "email")
            # Matches "email", "user_email", "primary_email_address", etc.
        """
        stmt = (
            select(Field)
            .where(
                and_(
                    Field.version_id == version_id,
                    Field.field_name.ilike(f"%{search_term}%"),
                )
            )
            .order_by(Field.field_name)
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_high_cardinality_fields(
        self,
        version_id: UUID,
        threshold: float = 0.9,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Field]:
        """
        Get fields with high cardinality ratio (potential unique identifiers).

        Args:
            version_id: The version UUID
            threshold: Minimum cardinality ratio (default: 0.9)
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of high cardinality fields

        Example:
            unique_fields = repo.get_high_cardinality_fields(version_id, 0.95)
            for field in unique_fields:
                print(f"{field.field_path}: {field.cardinality_ratio}")
        """
        stmt = (
            select(Field)
            .where(
                and_(
                    Field.version_id == version_id,
                    Field.cardinality_ratio >= threshold,
                )
            )
            .order_by(Field.cardinality_ratio.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def bulk_update_pii_status(
        self, field_ids: list[UUID], is_pii: bool, pii_type: str | None = None
    ) -> int:
        """
        Bulk update PII status for multiple fields.

        Args:
            field_ids: List of field UUIDs to update
            is_pii: PII status to set
            pii_type: Optional PII type to set

        Returns:
            Number of fields updated

        Example:
            # Mark fields as PII
            count = repo.bulk_update_pii_status(
                [field1_id, field2_id],
                is_pii=True,
                pii_type="email"
            )
        """
        count = 0
        for field_id in field_ids:
            field = self.get_by_id(field_id)
            if field:
                field.is_pii = is_pii
                if pii_type is not None:
                    field.pii_type = pii_type
                count += 1

        self.db.flush()
        return count

    def count_by_version(self, version_id: UUID) -> int:
        """
        Count total fields in a version.

        Args:
            version_id: The version UUID

        Returns:
            Total number of fields

        Example:
            total_fields = repo.count_by_version(version_id)
            print(f"Version has {total_fields} fields")
        """
        from sqlalchemy import func

        stmt = (
            select(func.count()).select_from(Field).where(Field.version_id == version_id)
        )
        result = self.db.execute(stmt)
        return result.scalar_one()

    def global_search(
        self,
        query: str | None = None,
        limit: int = 20,
        offset: int = 0,
        additional_filters: list | None = None,
        dictionary_id: UUID | None = None,
    ) -> tuple[Sequence[Field], int]:
        """
        Global search for fields across all versions.

        This method enables searching fields across all dictionaries and versions,
        supporting text search on field names/paths and additional filtering criteria.

        Args:
            query: Text search for field name/path (case-insensitive partial match)
            limit: Max results to return
            offset: Number of results to skip (for pagination)
            additional_filters: List of additional SQLAlchemy filter expressions
            dictionary_id: Optional UUID to filter by specific dictionary

        Returns:
            Tuple of (fields, total_count) where fields is the result list and
            total_count is the total number of matching records

        Example:
            # Search for 'email' fields
            fields, total = repo.global_search(query="email", limit=10)

            # Search with additional filters
            from models.field import Field
            filters = [Field.is_pii == True, Field.data_type == "string"]
            fields, total = repo.global_search(
                query="user",
                limit=20,
                offset=0,
                additional_filters=filters
            )

            # Search within a specific dictionary
            fields, total = repo.global_search(
                query="user",
                dictionary_id=dict_uuid
            )
        """
        from sqlalchemy import func, or_

        from src.models.version import Version

        # Base query
        stmt = select(Field)

        # Join with Version if we need to filter by dictionary_id
        if dictionary_id:
            stmt = stmt.join(Version, Field.version_id == Version.id)
            stmt = stmt.where(Version.dictionary_id == dictionary_id)

        # Apply text search on field_name and field_path
        if query:
            stmt = stmt.where(
                or_(
                    Field.field_name.ilike(f"%{query}%"),
                    Field.field_path.ilike(f"%{query}%"),
                )
            )

        # Apply additional filters
        if additional_filters:
            for filter_expr in additional_filters:
                stmt = stmt.filter(filter_expr)

        # Get total count before pagination
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        # Apply ordering and pagination
        stmt = stmt.order_by(Field.field_path).offset(offset).limit(limit)

        # Execute query
        result = self.db.execute(stmt)
        fields = result.scalars().all()

        return fields, total
