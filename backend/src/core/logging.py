"""Structured logging configuration for the application."""
import logging
import sys
from pathlib import Path

from pythonjsonlogger import jsonlogger


def setup_logging(
    log_level: str = "INFO",
    environment: str = "development",
    log_dir: str | None = None,
) -> logging.Logger:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment name (development, staging, production)
        log_dir: Directory for log files (defaults to ./logs)

    Returns:
        logging.Logger: Configured root logger
    """
    # Create log directory if it doesn't exist
    if log_dir is None:
        log_dir = "logs"
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Format based on environment
    if environment == "production":
        # JSON format for production (better for log aggregation)
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler for all logs
    file_handler = logging.FileHandler(log_path / "app.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # File handler for errors only
    error_handler = logging.FileHandler(log_path / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # Separate audit log with JSON format
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)
    audit_handler = logging.FileHandler(log_path / "audit.log")
    audit_formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    audit_handler.setFormatter(audit_formatter)
    audit_logger.addHandler(audit_handler)
    audit_logger.propagate = False  # Don't propagate to root logger

    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
