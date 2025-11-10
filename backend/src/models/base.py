"""
SQLAlchemy Base configuration for Data Dictionary Generator.

This module provides the declarative base class for all ORM models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    All models should inherit from this class to be properly registered
    with SQLAlchemy's declarative system.
    """
    pass
