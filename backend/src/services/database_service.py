"""Database management service for stats, health checks, backup, and clear operations."""
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.config import settings
from src.models.annotation import Annotation
from src.models.dictionary import Dictionary
from src.models.field import Field
from src.models.version import Version

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database management operations."""

    def __init__(self, db: Session):
        """
        Initialize database service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_database_stats(self) -> dict[str, Any]:
        """
        Get comprehensive database statistics.

        Returns:
            dict: Database statistics including:
                - database_type: "sqlite" or "postgresql"
                - database_size: Size in bytes (SQLite only)
                - database_path: File path (SQLite only)
                - table_counts: Record counts for each table
                - total_records: Total records across all tables
                - last_updated: Most recent update timestamp
        """
        stats = {
            "database_type": "sqlite" if settings.is_sqlite else "postgresql",
            "table_counts": {},
            "total_records": 0,
            "last_updated": None,
        }

        # Get record counts for each table
        stats["table_counts"]["dictionaries"] = self.db.query(Dictionary).count()
        stats["table_counts"]["versions"] = self.db.query(Version).count()
        stats["table_counts"]["fields"] = self.db.query(Field).count()
        stats["table_counts"]["annotations"] = self.db.query(Annotation).count()

        stats["total_records"] = sum(stats["table_counts"].values())

        # Get most recent update timestamp
        last_dict_update = (
            self.db.query(Dictionary.updated_at)
            .order_by(Dictionary.updated_at.desc())
            .first()
        )
        last_annotation_update = (
            self.db.query(Annotation.updated_at)
            .order_by(Annotation.updated_at.desc())
            .first()
        )

        if last_dict_update or last_annotation_update:
            timestamps = [
                ts
                for ts in [
                    last_dict_update[0] if last_dict_update else None,
                    last_annotation_update[0] if last_annotation_update else None,
                ]
                if ts
            ]
            if timestamps:
                stats["last_updated"] = max(timestamps)

        # SQLite-specific stats
        if settings.is_sqlite:
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            # Handle relative paths
            if not db_path.startswith("/"):
                db_path = os.path.join(os.getcwd(), db_path)

            stats["database_path"] = db_path

            if os.path.exists(db_path):
                stats["database_size"] = os.path.getsize(db_path)
                stats["database_size_mb"] = round(stats["database_size"] / (1024 * 1024), 2)
            else:
                stats["database_size"] = 0
                stats["database_size_mb"] = 0

        logger.info(f"Database stats retrieved: {stats['total_records']} total records")
        return stats

    def get_database_health(self) -> dict[str, Any]:
        """
        Check database health and connectivity.

        Returns:
            dict: Health check results including:
                - status: "healthy" or "unhealthy"
                - connection: Connection test result
                - integrity: Database integrity check (SQLite only)
                - checked_at: Timestamp of health check
        """
        health = {
            "status": "healthy",
            "connection": False,
            "checked_at": datetime.now(timezone.utc),
        }

        try:
            # Test connection with simple query
            result = self.db.execute(text("SELECT 1"))
            result.fetchone()
            health["connection"] = True
            logger.debug("Database connection test passed")

            # SQLite-specific integrity check
            if settings.is_sqlite:
                integrity_result = self.db.execute(text("PRAGMA integrity_check"))
                integrity = integrity_result.fetchone()[0]
                health["integrity"] = integrity == "ok"
                if integrity != "ok":
                    health["status"] = "unhealthy"
                    health["integrity_details"] = integrity
                    logger.warning(f"SQLite integrity check failed: {integrity}")
            else:
                # PostgreSQL: Enhanced health check
                try:
                    # Check if database is accepting connections
                    self.db.execute(text("SELECT COUNT(*) FROM dictionaries"))

                    # Check database stats for additional health information
                    stats_query = text("""
                        SELECT
                            pg_database_size(current_database()) as db_size,
                            pg_is_in_recovery() as is_replica,
                            (SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()) as active_connections
                    """)
                    stats = self.db.execute(stats_query).fetchone()

                    health["integrity"] = True
                    health["database_size_bytes"] = stats[0] if stats else None
                    health["is_replica"] = stats[1] if stats else False
                    health["active_connections"] = stats[2] if stats else None

                    logger.debug(f"PostgreSQL health: size={stats[0]}, connections={stats[2]}")
                except Exception as pg_error:
                    # If detailed stats fail, just mark integrity as true if basic query works
                    health["integrity"] = True
                    logger.debug(f"PostgreSQL detailed stats unavailable: {pg_error}")

        except Exception as e:
            health["status"] = "unhealthy"
            health["connection"] = False
            health["error"] = str(e)
            logger.error(f"Database health check failed: {e}")

        return health

    def clear_database(self) -> dict[str, Any]:
        """
        Clear all data from the database.

        WARNING: This will delete all dictionaries, versions, fields, and annotations.
        This operation cannot be undone.

        Returns:
            dict: Results of the clear operation including counts of deleted records
        """
        logger.warning("Starting database clear operation")

        deleted_counts = {
            "dictionaries": 0,
            "versions": 0,
            "fields": 0,
            "annotations": 0,
        }

        try:
            # Count records before deletion
            deleted_counts["dictionaries"] = self.db.query(Dictionary).count()
            deleted_counts["versions"] = self.db.query(Version).count()
            deleted_counts["fields"] = self.db.query(Field).count()
            deleted_counts["annotations"] = self.db.query(Annotation).count()

            # Delete all records (cascade will handle relationships)
            # Delete in reverse order of dependencies
            self.db.query(Annotation).delete()
            self.db.query(Field).delete()
            self.db.query(Version).delete()
            self.db.query(Dictionary).delete()

            self.db.commit()

            logger.warning(
                f"Database cleared: {sum(deleted_counts.values())} records deleted"
            )

            return {
                "status": "success",
                "deleted_counts": deleted_counts,
                "total_deleted": sum(deleted_counts.values()),
                "cleared_at": datetime.now(timezone.utc),
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to clear database: {e}")
            raise

    def backup_database(self, backup_dir: str | None = None) -> dict[str, Any]:
        """
        Create a backup of the database.

        For SQLite: Copies the database file
        For PostgreSQL: Would need pg_dump (not implemented)

        Args:
            backup_dir: Directory to store backup (optional)

        Returns:
            dict: Backup information including path and size
        """
        if not settings.is_sqlite:
            raise NotImplementedError(
                "Backup is currently only supported for SQLite databases. "
                "For PostgreSQL, use pg_dump directly."
            )

        # Determine backup directory
        if backup_dir is None:
            backup_dir = os.getenv("BACKUP_DIR", "./backups")

        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)

        # Get source database path
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        if not db_path.startswith("/"):
            db_path = os.path.join(os.getcwd(), db_path)

        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")

        # Create backup filename with timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_filename = f"database_backup_{timestamp}.db"
        backup_file_path = backup_path / backup_filename

        # Copy database file
        shutil.copy2(db_path, backup_file_path)

        backup_size = os.path.getsize(backup_file_path)

        logger.info(f"Database backup created: {backup_file_path} ({backup_size} bytes)")

        return {
            "status": "success",
            "backup_path": str(backup_file_path),
            "backup_size": backup_size,
            "backup_size_mb": round(backup_size / (1024 * 1024), 2),
            "created_at": datetime.now(timezone.utc),
        }

    def get_table_statistics(self) -> dict[str, Any]:
        """
        Get detailed statistics for each table.

        Returns:
            dict: Per-table statistics including row counts and storage info
        """
        tables_stats = {}

        # Dictionaries table stats
        dict_count = self.db.query(Dictionary).count()
        tables_stats["dictionaries"] = {
            "row_count": dict_count,
            "columns": 10,
        }

        # Versions table stats
        version_count = self.db.query(Version).count()
        avg_versions_per_dict = version_count / dict_count if dict_count > 0 else 0
        tables_stats["versions"] = {
            "row_count": version_count,
            "columns": 8,
            "avg_per_dictionary": round(avg_versions_per_dict, 2),
        }

        # Fields table stats
        field_count = self.db.query(Field).count()
        avg_fields_per_version = field_count / version_count if version_count > 0 else 0
        tables_stats["fields"] = {
            "row_count": field_count,
            "columns": 28,
            "avg_per_version": round(avg_fields_per_version, 2),
        }

        # Annotations table stats
        annotation_count = self.db.query(Annotation).count()
        avg_annotations_per_field = (
            annotation_count / field_count if field_count > 0 else 0
        )
        tables_stats["annotations"] = {
            "row_count": annotation_count,
            "columns": 12,
            "avg_per_field": round(avg_annotations_per_field, 2),
        }

        return tables_stats
