"""
Repositories package for Data Dictionary Generator.

This package contains all repository classes that provide data access
abstraction using the repository pattern. Each repository extends
BaseRepository and provides specialized queries for its entity type.

Example:
    from repositories import DictionaryRepository, FieldRepository
    from core.database import get_db

    db = next(get_db())
    dict_repo = DictionaryRepository(db)
    field_repo = FieldRepository(db)

    # Use repositories for data access
    dictionary = dict_repo.get_by_name("customer_data")
    fields = field_repo.get_by_version(version_id)
"""

from .annotation_repo import AnnotationRepository
from .base import BaseRepository
from .dictionary_repo import DictionaryRepository
from .field_repo import FieldRepository
from .version_repo import VersionRepository

__all__ = [
    "BaseRepository",
    "DictionaryRepository",
    "VersionRepository",
    "FieldRepository",
    "AnnotationRepository",
]
