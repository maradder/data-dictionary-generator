"""Repository for Annotation entity with bulk operations."""
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from src.models.annotation import Annotation

from .base import BaseRepository


class AnnotationRepository(BaseRepository[Annotation]):
    """
    Repository for Annotation entities with specialized queries.

    Extends BaseRepository with annotation-specific operations including
    field-based lookups, bulk create/update operations, and filtering
    by AI-generated status.

    Example:
        repo = AnnotationRepository(db)
        annotations = repo.get_by_field(field_id)
        repo.bulk_create_annotations(annotation_data_list)
        repo.update_annotation(annotation_id, description="New description")
    """

    def __init__(self, db: Session):
        """
        Initialize the annotation repository.

        Args:
            db: Database session
        """
        super().__init__(Annotation, db)

    def get_by_field(
        self, field_id: UUID, skip: int = 0, limit: int | None = None
    ) -> Sequence[Annotation]:
        """
        Get all annotations for a specific field.

        Args:
            field_id: The field UUID
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return (None for all)

        Returns:
            Sequence of annotations for the field

        Example:
            annotations = repo.get_by_field(field_id)
            for annotation in annotations:
                print(f"{annotation.business_name}: {annotation.description}")
        """
        stmt = (
            select(Annotation)
            .where(Annotation.field_id == field_id)
            .order_by(Annotation.created_at.desc())
            .offset(skip)
        )

        if limit is not None:
            stmt = stmt.limit(limit)

        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_latest_by_field(self, field_id: UUID) -> Annotation | None:
        """
        Get the most recent annotation for a field.

        Args:
            field_id: The field UUID

        Returns:
            The latest annotation if found, None otherwise

        Example:
            latest = repo.get_latest_by_field(field_id)
            if latest:
                print(f"Latest annotation: {latest.description}")
        """
        stmt = (
            select(Annotation)
            .where(Annotation.field_id == field_id)
            .order_by(Annotation.created_at.desc())
            .limit(1)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def bulk_create_annotations(self, annotations_data: list[dict]) -> list[Annotation]:
        """
        Bulk create multiple annotations efficiently.

        Uses SQLAlchemy's bulk insert optimization for better performance
        when creating many annotations at once.

        Args:
            annotations_data: List of dictionaries containing annotation data

        Returns:
            List of created Annotation instances

        Example:
            annotations_data = [
                {
                    "field_id": field1_id,
                    "description": "User email address",
                    "business_name": "Email",
                    "is_ai_generated": True,
                    "ai_model_version": "gpt-4",
                },
                {
                    "field_id": field2_id,
                    "description": "User's age in years",
                    "business_name": "Age",
                    "is_ai_generated": False,
                    "created_by": "user@example.com",
                },
            ]
            annotations = repo.bulk_create_annotations(annotations_data)
            print(f"Created {len(annotations)} annotations")
        """
        # Create Annotation instances
        annotations = [Annotation(**data) for data in annotations_data]

        # Add all to session
        self.db.add_all(annotations)
        self.db.flush()

        # Refresh to get IDs and defaults
        for annotation in annotations:
            self.db.refresh(annotation)

        return annotations

    def update_annotation(
        self,
        id: UUID,
        description: str | None = None,
        business_name: str | None = None,
        business_owner: str | None = None,
        tags: dict | None = None,
        updated_by: str | None = None,
    ) -> Annotation | None:
        """
        Update an annotation with new values.

        Args:
            id: The annotation UUID
            description: New description (optional)
            business_name: New business name (optional)
            business_owner: New business owner (optional)
            tags: New tags dictionary (optional)
            updated_by: User making the update (optional)

        Returns:
            Updated annotation if found, None otherwise

        Example:
            annotation = repo.update_annotation(
                annotation_id,
                description="Updated user email address",
                business_name="Primary Email",
                updated_by="admin@example.com"
            )
        """
        annotation = self.get_by_id(id)
        if annotation is None:
            return None

        if description is not None:
            annotation.description = description
        if business_name is not None:
            annotation.business_name = business_name
        if business_owner is not None:
            annotation.business_owner = business_owner
        if tags is not None:
            annotation.tags = tags
        if updated_by is not None:
            annotation.updated_by = updated_by

        self.db.flush()
        self.db.refresh(annotation)
        return annotation

    def get_ai_generated(
        self, skip: int = 0, limit: int = 100
    ) -> Sequence[Annotation]:
        """
        Get all AI-generated annotations.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of AI-generated annotations

        Example:
            ai_annotations = repo.get_ai_generated(limit=50)
            for annotation in ai_annotations:
                print(f"AI ({annotation.ai_model_version}): {annotation.description}")
        """
        stmt = (
            select(Annotation)
            .where(Annotation.is_ai_generated)
            .order_by(Annotation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_user_generated(
        self, skip: int = 0, limit: int = 100
    ) -> Sequence[Annotation]:
        """
        Get all user-generated (non-AI) annotations.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of user-generated annotations

        Example:
            user_annotations = repo.get_user_generated(limit=50)
            for annotation in user_annotations:
                print(f"Created by {annotation.created_by}: {annotation.description}")
        """
        stmt = (
            select(Annotation)
            .where(not Annotation.is_ai_generated)
            .order_by(Annotation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_by_model_version(
        self, model_version: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Annotation]:
        """
        Get annotations generated by a specific AI model version.

        Args:
            model_version: The AI model version (e.g., "gpt-4", "claude-3")
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of annotations from the specified model

        Example:
            gpt4_annotations = repo.get_by_model_version("gpt-4")
            print(f"Found {len(gpt4_annotations)} GPT-4 annotations")
        """
        stmt = (
            select(Annotation)
            .where(
                and_(
                    Annotation.is_ai_generated,
                    Annotation.ai_model_version == model_version,
                )
            )
            .order_by(Annotation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_by_business_owner(
        self, business_owner: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Annotation]:
        """
        Get annotations by business owner.

        Args:
            business_owner: The business owner name
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of annotations for the business owner

        Example:
            annotations = repo.get_by_business_owner("Data Team")
            for annotation in annotations:
                print(f"{annotation.business_name}: {annotation.description}")
        """
        stmt = (
            select(Annotation)
            .where(Annotation.business_owner == business_owner)
            .order_by(Annotation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def search_by_description(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Annotation]:
        """
        Search annotations by description (case-insensitive partial match).

        Args:
            search_term: Search term to match against descriptions
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of matching annotations

        Example:
            results = repo.search_by_description("email")
            # Matches descriptions containing "email", "Email", "EMAIL", etc.
        """
        stmt = (
            select(Annotation)
            .where(Annotation.description.ilike(f"%{search_term}%"))
            .order_by(Annotation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def search_by_business_name(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> Sequence[Annotation]:
        """
        Search annotations by business name (case-insensitive partial match).

        Args:
            search_term: Search term to match against business names
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of matching annotations

        Example:
            results = repo.search_by_business_name("customer")
            # Matches "Customer ID", "customer_name", etc.
        """
        stmt = (
            select(Annotation)
            .where(Annotation.business_name.ilike(f"%{search_term}%"))
            .order_by(Annotation.business_name)
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def get_with_tags(
        self, tag_key: str, tag_value: str | None = None, skip: int = 0, limit: int = 100
    ) -> Sequence[Annotation]:
        """
        Get annotations with specific tags.

        Args:
            tag_key: The tag key to search for
            tag_value: Optional tag value to match (None to match any value)
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            Sequence of annotations with matching tags

        Example:
            # Get annotations with "category" tag
            categorized = repo.get_with_tags("category")

            # Get annotations with specific category
            pii_annotations = repo.get_with_tags("category", "pii")
        """
        # This is a simplified version - for production use, consider
        # using PostgreSQL JSONB operators for better performance
        all_annotations = self.get_all(skip=0, limit=10000)  # Get a large batch

        filtered = []
        for annotation in all_annotations:
            if annotation.tags and tag_key in annotation.tags:
                if tag_value is None or annotation.tags[tag_key] == tag_value:
                    filtered.append(annotation)
                    if len(filtered) >= limit:
                        break

        return filtered[skip:skip + limit] if skip < len(filtered) else []

    def update_tags(self, id: UUID, tags: dict) -> Annotation | None:
        """
        Update tags for an annotation.

        Args:
            id: The annotation UUID
            tags: New tags dictionary to merge with existing

        Returns:
            Updated annotation if found, None otherwise

        Example:
            new_tags = {"category": "pii", "sensitivity": "high"}
            annotation = repo.update_tags(annotation_id, new_tags)
        """
        annotation = self.get_by_id(id)
        if annotation is None:
            return None

        # Merge with existing tags if present
        if annotation.tags:
            annotation.tags.update(tags)
        else:
            annotation.tags = tags

        self.db.flush()
        self.db.refresh(annotation)
        return annotation

    def delete_by_field(self, field_id: UUID) -> int:
        """
        Delete all annotations for a specific field.

        Args:
            field_id: The field UUID

        Returns:
            Number of annotations deleted

        Example:
            deleted = repo.delete_by_field(field_id)
            print(f"Deleted {deleted} annotations")
        """
        annotations = self.get_by_field(field_id)
        count = 0
        for annotation in annotations:
            if self.delete(annotation.id):
                count += 1
        return count

    def count_by_field(self, field_id: UUID) -> int:
        """
        Count annotations for a specific field.

        Args:
            field_id: The field UUID

        Returns:
            Total number of annotations

        Example:
            count = repo.count_by_field(field_id)
            print(f"Field has {count} annotations")
        """
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(Annotation)
            .where(Annotation.field_id == field_id)
        )
        result = self.db.execute(stmt)
        return result.scalar_one()

    def count_ai_generated(self) -> int:
        """
        Count total AI-generated annotations.

        Returns:
            Total number of AI-generated annotations

        Example:
            ai_count = repo.count_ai_generated()
            print(f"Total AI annotations: {ai_count}")
        """
        return self.count({"is_ai_generated": True})

    def count_user_generated(self) -> int:
        """
        Count total user-generated annotations.

        Returns:
            Total number of user-generated annotations

        Example:
            user_count = repo.count_user_generated()
            print(f"Total user annotations: {user_count}")
        """
        return self.count({"is_ai_generated": False})
