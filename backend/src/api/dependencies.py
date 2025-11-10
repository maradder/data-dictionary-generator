"""Dependency injection for FastAPI routes."""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.services.analysis_service import AnalysisService
from src.services.dictionary_service import DictionaryService
from src.services.export_service import ExportService
from src.services.version_service import VersionService

# Type alias for database session dependency
DatabaseSession = Annotated[Session, Depends(get_db)]


def get_current_user() -> str:
    """
    Get current authenticated user.

    Placeholder implementation for Phase 1.
    TODO: Implement proper authentication in Phase 2.

    Returns:
        str: User identifier
    """
    return "system"


def get_dictionary_service(db: DatabaseSession) -> DictionaryService:
    """
    Create DictionaryService instance.

    Args:
        db: Database session

    Returns:
        DictionaryService: Service instance
    """
    return DictionaryService(db=db)


def get_version_service(db: DatabaseSession) -> VersionService:
    """
    Create VersionService instance.

    Args:
        db: Database session

    Returns:
        VersionService: Service instance
    """
    return VersionService(db=db)


def get_export_service(db: DatabaseSession) -> ExportService:
    """
    Create ExportService instance.

    Args:
        db: Database session

    Returns:
        ExportService: Service instance
    """
    return ExportService(db=db)


def get_analysis_service(db: DatabaseSession) -> AnalysisService:
    """
    Create AnalysisService instance.

    Args:
        db: Database session

    Returns:
        AnalysisService: Service instance
    """
    return AnalysisService(db=db)
