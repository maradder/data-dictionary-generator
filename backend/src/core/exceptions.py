"""Custom exception hierarchy for the Data Dictionary Generator."""
from typing import Any


class DataDictException(Exception):
    """
    Base exception for all application errors.

    All custom exceptions should inherit from this base class to allow
    for centralized error handling and logging.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(DataDictException):
    """
    Input validation errors.

    Raised when user input fails validation rules.
    Maps to HTTP 400 Bad Request.
    """

    pass


class NotFoundError(DataDictException):
    """
    Resource not found errors.

    Raised when a requested resource does not exist.
    Maps to HTTP 404 Not Found.
    """

    pass


class ProcessingError(DataDictException):
    """
    Errors during JSON processing.

    Raised when JSON parsing, type inference, or analysis fails.
    Maps to HTTP 422 Unprocessable Entity.
    """

    pass


class ExportError(DataDictException):
    """
    Errors during export generation.

    Raised when Excel or other export formats fail to generate.
    Maps to HTTP 500 Internal Server Error.
    """

    pass


class ExternalServiceError(DataDictException):
    """
    Errors from external services.

    Raised when external API calls fail (e.g., OpenAI API).
    Maps to HTTP 503 Service Unavailable.
    """

    pass


class DatabaseError(DataDictException):
    """
    Database operation errors.

    Raised when database operations fail.
    Maps to HTTP 500 Internal Server Error.
    """

    pass


class AuthenticationError(DataDictException):
    """
    Authentication errors.

    Raised when API key or other authentication fails.
    Maps to HTTP 401 Unauthorized.
    """

    pass


class AuthorizationError(DataDictException):
    """
    Authorization errors.

    Raised when user lacks permission for an operation.
    Maps to HTTP 403 Forbidden.
    """

    pass


class RateLimitError(DataDictException):
    """
    Rate limit exceeded errors.

    Raised when API rate limits are exceeded.
    Maps to HTTP 429 Too Many Requests.
    """

    pass


class ConfigurationError(DataDictException):
    """
    Configuration errors.

    Raised when application configuration is invalid.
    Maps to HTTP 500 Internal Server Error.
    """

    pass
