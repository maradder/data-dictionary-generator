"""
Common schemas for API request/response validation.

This module contains base schemas and utilities used across the application,
including pagination, error responses, and metadata containers.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Generic type variable for paginated responses
T = TypeVar("T")


class PaginationMeta(BaseModel):
    """
    Metadata for paginated responses.

    Attributes:
        total: Total number of items across all pages
        limit: Number of items requested per page
        offset: Number of items skipped
        has_more: Whether there are more items beyond current page
    """

    total: int = Field(..., ge=0, description="Total number of items")
    limit: int = Field(..., ge=1, le=1000, description="Items per page")
    offset: int = Field(..., ge=0, description="Number of items skipped")
    has_more: bool = Field(..., description="More items available")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.

    Used to wrap lists of items with pagination metadata.

    Type Parameters:
        T: The type of items in the data list

    Example:
        ```python
        PaginatedResponse[DictionaryListItem](
            data=[dict1, dict2],
            meta=PaginationMeta(total=100, limit=20, offset=0, has_more=True)
        )
        ```
    """

    data: list[T] = Field(..., description="List of items for current page")
    meta: PaginationMeta = Field(..., description="Pagination metadata")


class ErrorDetail(BaseModel):
    """
    Detailed error information for a specific field or issue.

    Attributes:
        field: Field name or path that caused the error
        issue: Human-readable description of the issue
        code: Optional machine-readable error code
    """

    field: str = Field(..., description="Field that caused the error")
    issue: str = Field(..., description="Description of the issue")
    code: str | None = Field(None, description="Machine-readable error code")


class ErrorResponse(BaseModel):
    """
    Standard error response format for all API errors.

    This provides a consistent structure for error responses across
    all endpoints, making it easier for clients to handle errors.

    Attributes:
        code: Machine-readable error code (e.g., VALIDATION_ERROR)
        message: Human-readable error message
        details: Optional list of detailed error information
        request_id: Optional request tracking ID

    Error Codes:
        - VALIDATION_ERROR (400): Request validation failed
        - NOT_FOUND (404): Resource not found
        - CONFLICT (409): Resource conflict (e.g., duplicate version)
        - INTERNAL_ERROR (500): Internal server error
        - FILE_TOO_LARGE (413): Uploaded file exceeds size limit
        - UNSUPPORTED_FORMAT (415): Unsupported file format
    """

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: list[ErrorDetail] | None = Field(
        None,
        description="Detailed error information"
    )
    request_id: str | None = Field(
        None,
        description="Request tracking ID"
    )


class ResponseMeta(BaseModel):
    """
    Metadata for single-item responses.

    Used for non-paginated responses that need additional metadata.

    Attributes:
        processing_time_ms: Time taken to process the request in milliseconds
        Additional fields can be added as needed
    """

    processing_time_ms: int | None = Field(
        None,
        ge=0,
        description="Processing time in milliseconds"
    )

    model_config = ConfigDict(extra="allow")  # Allow additional fields


class DataResponse(BaseModel, Generic[T]):
    """
    Generic single-item response wrapper with metadata.

    Type Parameters:
        T: The type of the data object

    Example:
        ```python
        DataResponse[DictionaryResponse](
            data=dictionary,
            meta=ResponseMeta(processing_time_ms=2340)
        )
        ```
    """

    data: T = Field(..., description="Response data")
    meta: ResponseMeta | None = Field(None, description="Response metadata")


class HealthResponse(BaseModel):
    """
    Health check response.

    Attributes:
        status: Service status (healthy, degraded, unhealthy)
        version: API version
        timestamp: Current server timestamp
    """

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current server timestamp")
    database: str | None = Field(None, description="Database connection status")
