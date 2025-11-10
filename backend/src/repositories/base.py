"""Base repository with common CRUD operations and pagination support."""
from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

from src.models.base import Base

# Type variable for generic model type
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository implementing common CRUD operations with pagination.

    Provides a consistent interface for data access across all entity types.
    Uses SQLAlchemy 2.0 syntax with proper type hints.

    Type Parameters:
        ModelType: The SQLAlchemy model class this repository manages

    Attributes:
        model: The SQLAlchemy model class
        db: The database session

    Example:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: Session):
                super().__init__(User, db)
    """

    def __init__(self, model: type[ModelType], db: Session):
        """
        Initialize the repository.

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    def get_by_id(self, id: UUID) -> ModelType | None:
        """
        Get a single entity by its ID.

        Args:
            id: The UUID of the entity

        Returns:
            The entity if found, None otherwise

        Example:
            user = repo.get_by_id(user_id)
            if user:
                print(user.name)
        """
        stmt = select(self.model).where(self.model.id == id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_dir: str = "asc",
    ) -> Sequence[ModelType]:
        """
        Get all entities with optional pagination and ordering.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            order_by: Column name to order by
            order_dir: Order direction ('asc' or 'desc')

        Returns:
            Sequence of entities

        Example:
            users = repo.get_all(skip=0, limit=20, order_by="created_at", order_dir="desc")
        """
        stmt = select(self.model)

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            column = getattr(self.model, order_by)
            stmt = stmt.order_by(desc(column) if order_dir == "desc" else asc(column))

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        result = self.db.execute(stmt)
        return result.scalars().all()

    def create(self, **kwargs: Any) -> ModelType:
        """
        Create a new entity.

        Args:
            **kwargs: Field values for the new entity

        Returns:
            The created entity with ID populated

        Example:
            user = repo.create(name="John Doe", email="john@example.com")
            print(user.id)
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.flush()  # Flush to get the ID without committing
        self.db.refresh(instance)
        return instance

    def update(self, id: UUID, **kwargs: Any) -> ModelType | None:
        """
        Update an existing entity.

        Args:
            id: The UUID of the entity to update
            **kwargs: Fields to update with new values

        Returns:
            The updated entity if found, None otherwise

        Example:
            user = repo.update(user_id, name="Jane Doe", email="jane@example.com")
        """
        instance = self.get_by_id(id)
        if instance is None:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.db.flush()
        self.db.refresh(instance)
        return instance

    def delete(self, id: UUID) -> bool:
        """
        Delete an entity by ID.

        Args:
            id: The UUID of the entity to delete

        Returns:
            True if entity was deleted, False if not found

        Example:
            if repo.delete(user_id):
                print("User deleted successfully")
        """
        instance = self.get_by_id(id)
        if instance is None:
            return False

        self.db.delete(instance)
        self.db.flush()
        return True

    def count(self, filters: dict[str, Any] | None = None) -> int:
        """
        Count entities matching optional filters.

        Args:
            filters: Dictionary of field names and values to filter by

        Returns:
            Total count of matching entities

        Example:
            active_users = repo.count({"is_active": True})
        """
        stmt = select(func.count()).select_from(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)

        result = self.db.execute(stmt)
        return result.scalar_one()

    def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        order_dir: str = "asc",
    ) -> tuple[Sequence[ModelType], int]:
        """
        Paginate entities with filtering and ordering.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            filters: Dictionary of field names and values to filter by
            order_by: Column name to order by
            order_dir: Order direction ('asc' or 'desc')

        Returns:
            Tuple of (items, total_count)

        Example:
            items, total = repo.paginate(
                page=1,
                page_size=20,
                filters={"is_active": True},
                order_by="created_at",
                order_dir="desc"
            )
            total_pages = (total + page_size - 1) // page_size
        """
        # Build base query
        stmt = select(self.model)

        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    stmt = stmt.where(getattr(self.model, key) == value)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = self.db.execute(count_stmt).scalar_one()

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            column = getattr(self.model, order_by)
            stmt = stmt.order_by(desc(column) if order_dir == "desc" else asc(column))

        # Apply pagination
        skip = (page - 1) * page_size
        stmt = stmt.offset(skip).limit(page_size)

        # Execute query
        result = self.db.execute(stmt)
        items = result.scalars().all()

        return items, total_count

    def exists(self, id: UUID) -> bool:
        """
        Check if an entity exists by ID.

        Args:
            id: The UUID of the entity

        Returns:
            True if entity exists, False otherwise

        Example:
            if repo.exists(user_id):
                print("User exists")
        """
        stmt = select(func.count()).select_from(self.model).where(self.model.id == id)
        result = self.db.execute(stmt)
        return result.scalar_one() > 0

    def filter(
        self,
        filters: dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        order_dir: str = "asc",
    ) -> Sequence[ModelType]:
        """
        Filter entities by multiple criteria.

        Args:
            filters: Dictionary of field names and values to filter by
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            order_by: Column name to order by
            order_dir: Order direction ('asc' or 'desc')

        Returns:
            Sequence of matching entities

        Example:
            active_admins = repo.filter(
                {"is_active": True, "role": "admin"},
                order_by="created_at",
                order_dir="desc"
            )
        """
        stmt = select(self.model)

        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            column = getattr(self.model, order_by)
            stmt = stmt.order_by(desc(column) if order_dir == "desc" else asc(column))

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        result = self.db.execute(stmt)
        return result.scalars().all()

    def _build_select(self) -> Select:
        """
        Build a base select statement for the model.

        Returns:
            Base select statement

        Note:
            Can be overridden in subclasses to add eager loading or joins.
        """
        return select(self.model)
