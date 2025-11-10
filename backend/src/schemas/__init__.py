"""
Schemas package for Data Dictionary Generator API.

This package contains all Pydantic schemas (DTOs) for request/response
validation across the application. Schemas are organized by domain:

- common: Base schemas, pagination, error responses
- dictionary: Dictionary creation, update, and response schemas
- field: Field metadata and annotation schemas
- version: Version management and comparison schemas
- export: Export format and options schemas

All schemas use Pydantic 2.x syntax with Field() for validation.
ORM-compatible schemas have `model_config = ConfigDict(from_attributes=True)`.

Example:
    from schemas import DictionaryCreate, DictionaryResponse, PaginatedResponse
    from schemas.field import FieldResponse, AnnotationUpdate
    from schemas.export import ExportFormat, ExportRequest
"""

# Common schemas
from .common import (
    DataResponse,
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    PaginatedResponse,
    PaginationMeta,
    ResponseMeta,
)

# Dictionary schemas
from .dictionary import (
    DictionaryCreate,
    DictionaryDelete,
    DictionaryListItem,
    DictionaryResponse,
    DictionaryUpdate,
    VersionSummary,
)

# Export schemas
from .export import (
    BatchExportRequest,
    BatchExportResponse,
    CSVExportOptions,
    ExcelExportOptions,
    ExportFormat,
    ExportMetadata,
    ExportRequest,
    ExportResponse,
    MarkdownExportOptions,
)

# Field schemas
from .field import (
    AnnotationResponse,
    AnnotationUpdate,
    FieldFilterParams,
    FieldListItem,
    FieldResponse,
)

# Version schemas
from .version import (
    ChangeDetail,
    ChangeSummary,
    FieldChangeData,
    VersionComparisonResponse,
    VersionCreate,
    VersionDelete,
    VersionInfo,
    VersionListItem,
    VersionResponse,
)

__all__ = [
    # Common
    "DataResponse",
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "ResponseMeta",
    # Dictionary
    "DictionaryCreate",
    "DictionaryDelete",
    "DictionaryListItem",
    "DictionaryResponse",
    "DictionaryUpdate",
    "VersionSummary",
    # Field
    "AnnotationResponse",
    "AnnotationUpdate",
    "FieldFilterParams",
    "FieldListItem",
    "FieldResponse",
    # Version
    "ChangeDetail",
    "ChangeSummary",
    "FieldChangeData",
    "VersionComparisonResponse",
    "VersionCreate",
    "VersionDelete",
    "VersionInfo",
    "VersionListItem",
    "VersionResponse",
    # Export
    "BatchExportRequest",
    "BatchExportResponse",
    "CSVExportOptions",
    "ExcelExportOptions",
    "ExportFormat",
    "ExportMetadata",
    "ExportRequest",
    "ExportResponse",
    "MarkdownExportOptions",
]
