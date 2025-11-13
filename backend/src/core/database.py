"""Database connection and session management using SQLAlchemy 2.0 with dual-database support."""
import logging
import time
from collections.abc import Generator
from datetime import datetime, timezone
from functools import wraps
from typing import Callable, TypeVar, Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import types
from sqlalchemy.exc import OperationalError

from src.core.config import settings

logger = logging.getLogger(__name__)

# Type variable for generic function return type
T = TypeVar('T')


class TZDateTime(types.TypeDecorator):
    """
    Custom DateTime type that ensures timezone-aware datetimes for SQLite.

    SQLite stores datetime as TEXT without timezone info, but we need to ensure
    that all datetimes are treated as UTC when read from the database.
    PostgreSQL natively supports TIMESTAMPTZ and handles this automatically.
    """
    impl = types.DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert timezone-aware datetime to UTC before storing."""
        if value is not None:
            if value.tzinfo is None:
                # If naive datetime, assume UTC
                value = value.replace(tzinfo=timezone.utc)
            else:
                # Convert to UTC if not already
                value = value.astimezone(timezone.utc)
            # Store as naive datetime in UTC (SQLite doesn't support TZ)
            return value.replace(tzinfo=None) if dialect.name == 'sqlite' else value
        return value

    def process_result_value(self, value, dialect):
        """Convert datetime from database to timezone-aware UTC."""
        if value is not None and dialect.name == 'sqlite':
            # SQLite returns naive datetime, mark it as UTC
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
        return value


def create_database_engine() -> Engine:
    """
    Create database engine with dialect-specific configuration.

    Supports both SQLite and PostgreSQL with appropriate optimizations
    for each database type.

    Returns:
        Engine: Configured SQLAlchemy engine
    """
    is_sqlite = settings.is_sqlite

    if is_sqlite:
        logger.info("Configuring SQLite database engine")
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={
                "check_same_thread": settings.SQLITE_CHECK_SAME_THREAD,
                "timeout": settings.SQLITE_TIMEOUT,
            },
            poolclass=StaticPool,  # Single connection reuse for SQLite
            echo=settings.DB_ECHO,
        )

        # Configure SQLite for better performance and concurrency
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            """Set SQLite pragmas on connection."""
            cursor = dbapi_conn.cursor()
            # Enable foreign key constraints (critical for CASCADE deletes)
            cursor.execute("PRAGMA foreign_keys=ON")
            # Use Write-Ahead Logging for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            # Faster writes (still safe)
            cursor.execute("PRAGMA synchronous=NORMAL")
            # 64MB cache
            cursor.execute("PRAGMA cache_size=-64000")
            # Store temp tables in memory
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
            logger.debug("SQLite pragmas configured for connection")
    else:
        # PostgreSQL configuration
        logger.info("Configuring PostgreSQL database engine")
        engine = create_engine(
            settings.DATABASE_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            echo=settings.DB_ECHO,
            pool_pre_ping=True,  # Enable connection health checks
            pool_recycle=3600,  # Recycle connections after 1 hour
        )

    logger.info(f"Database engine created: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    return engine


# Create SQLAlchemy engine
engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields a database session and ensures it's closed after use.
    Use with FastAPI's Depends() for automatic session management.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def retry_on_lock(max_retries: int = 3, delay: float = 0.1) -> Callable:
    """
    Decorator to retry database operations on SQLite lock errors.

    This decorator is specifically designed for SQLite's locking behavior.
    When a database is locked, it will retry the operation after a brief delay.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 0.1)

    Returns:
        Decorated function that retries on OperationalError with "locked" message

    Example:
        @retry_on_lock(max_retries=5, delay=0.2)
        def commit_changes(db: Session):
            db.commit()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    last_exception = e
                    # Only retry on database locked errors for SQLite
                    if settings.is_sqlite and "locked" in str(e).lower():
                        if attempt < max_retries - 1:
                            wait_time = delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(
                                f"Database locked, retrying in {wait_time}s "
                                f"(attempt {attempt + 1}/{max_retries})"
                            )
                            time.sleep(wait_time)
                            continue
                    # Re-raise if not a lock error or max retries exceeded
                    raise

            # Should never reach here, but just in case
            raise last_exception if last_exception else Exception("Unknown error in retry logic")

        return wrapper
    return decorator


def commit_with_retry(db: Session, max_retries: int = 3) -> None:
    """
    Commit database session with automatic retry on SQLite lock errors.

    This is a convenience function for the common case of committing a session.
    It uses exponential backoff when retrying.

    Args:
        db: SQLAlchemy database session
        max_retries: Maximum number of retry attempts (default: 3)

    Raises:
        OperationalError: If commit fails after all retries

    Example:
        from src.core.database import commit_with_retry

        dictionary = Dictionary(name="Example")
        db.add(dictionary)
        commit_with_retry(db)
    """
    @retry_on_lock(max_retries=max_retries)
    def _commit():
        db.commit()

    _commit()
