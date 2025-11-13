"""Database management API endpoints."""
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.services.database_service import DatabaseService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Database Management"])


def get_database_service(db: Session = Depends(get_db)) -> DatabaseService:
    """Dependency to get database service instance."""
    return DatabaseService(db)


@router.get("/stats", summary="Get database statistics")
async def get_database_stats(
    db_service: DatabaseService = Depends(get_database_service),
) -> dict[str, Any]:
    """
    Get comprehensive database statistics.

    Returns:
        Database statistics including:
        - database_type: "sqlite" or "postgresql"
        - database_size: Size in bytes (SQLite only)
        - table_counts: Record counts for each table
        - total_records: Total records across all tables
        - last_updated: Most recent update timestamp

    Example:
        ```
        GET /api/v1/database/stats
        ```
    """
    try:
        stats = db_service.get_database_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve database statistics: {str(e)}",
        )


@router.get("/health", summary="Check database health")
async def check_database_health(
    db_service: DatabaseService = Depends(get_database_service),
) -> dict[str, Any]:
    """
    Check database health and connectivity.

    Returns:
        Health check results including:
        - status: "healthy" or "unhealthy"
        - connection: Connection test result
        - integrity: Database integrity check (SQLite only)
        - checked_at: Timestamp of health check

    Example:
        ```
        GET /api/v1/database/health
        ```
    """
    try:
        health = db_service.get_database_health()
        return health
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "connection": False,
            "error": str(e),
        }


@router.get("/tables", summary="Get table statistics")
async def get_table_statistics(
    db_service: DatabaseService = Depends(get_database_service),
) -> dict[str, Any]:
    """
    Get detailed statistics for each table.

    Returns:
        Per-table statistics including:
        - row_count: Number of rows in table
        - columns: Number of columns
        - avg_per_parent: Average records per parent entity

    Example:
        ```
        GET /api/v1/database/tables
        ```
    """
    try:
        stats = db_service.get_table_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get table statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve table statistics: {str(e)}",
        )


@router.post("/clear", summary="Clear all database data")
async def clear_database(
    confirm: str,
    db_service: DatabaseService = Depends(get_database_service),
) -> dict[str, Any]:
    """
    Clear all data from the database.

    **WARNING:** This will delete all dictionaries, versions, fields, and annotations.
    This operation cannot be undone.

    Args:
        confirm: Must be exactly "DELETE_ALL_DATA" to proceed

    Returns:
        Results of the clear operation including counts of deleted records

    Raises:
        HTTPException: If confirmation string is incorrect or operation fails

    Example:
        ```
        POST /api/v1/database/clear?confirm=DELETE_ALL_DATA
        ```
    """
    if confirm != "DELETE_ALL_DATA":
        raise HTTPException(
            status_code=400,
            detail='Confirmation failed. You must pass confirm="DELETE_ALL_DATA" to proceed.',
        )

    try:
        result = db_service.clear_database()
        return result
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear database: {str(e)}",
        )


@router.get("/backup", summary="Create database backup")
async def backup_database(
    db_service: DatabaseService = Depends(get_database_service),
) -> dict[str, Any]:
    """
    Create a backup of the database.

    Currently only supported for SQLite databases.
    Creates a timestamped copy of the database file in the backups directory.

    Returns:
        Backup information including:
        - status: "success" or "error"
        - backup_path: Path to the backup file
        - backup_size: Size in bytes
        - created_at: Timestamp when backup was created

    Raises:
        HTTPException: If backup operation fails or database type not supported

    Example:
        ```
        GET /api/v1/database/backup
        ```
    """
    try:
        result = db_service.backup_database()
        return result
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail=str(e),
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create backup: {str(e)}",
        )


@router.get("/backup/download", summary="Download database backup file")
async def download_database_backup(
    db_service: DatabaseService = Depends(get_database_service),
) -> Response:
    """
    Download the SQLite database file directly.

    Returns the database file as a downloadable attachment.
    Only available for SQLite databases.

    Returns:
        FileResponse: The database file

    Raises:
        HTTPException: If database type not supported or file not found

    Example:
        ```
        GET /api/v1/database/backup/download
        ```
    """
    from fastapi.responses import FileResponse
    from src.core.config import settings

    if not settings.is_sqlite:
        raise HTTPException(
            status_code=501,
            detail="Direct download is only supported for SQLite databases.",
        )

    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if not db_path.startswith("/"):
        import os
        db_path = os.path.join(os.getcwd(), db_path)

    import os
    if not os.path.exists(db_path):
        raise HTTPException(
            status_code=404,
            detail="Database file not found",
        )

    # Create filename with timestamp
    from datetime import datetime, timezone
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"database_backup_{timestamp}.db"

    return FileResponse(
        path=db_path,
        filename=filename,
        media_type="application/x-sqlite3",
    )
