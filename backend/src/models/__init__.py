"""
Models package for Data Dictionary Generator.

This package contains all SQLAlchemy ORM models for the application.
Import models from this package to ensure proper initialization order.

Example:
    from models import Base, Dictionary, Version, Field, Annotation
    from models import create_all_tables
"""

from .annotation import Annotation
from .base import Base
from .dictionary import Dictionary
from .field import Field
from .version import Version

__all__ = [
    "Base",
    "Dictionary",
    "Version",
    "Field",
    "Annotation",
]
