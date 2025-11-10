"""
Export schemas for API request/response validation.

This module contains schemas for exporting data dictionaries
to various formats (JSON, CSV, Excel, Markdown).
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExportFormat(str, Enum):
    """
    Supported export formats.

    Attributes:
        JSON: JSON format with full metadata
        CSV: Flat CSV format with selected fields
        EXCEL: Excel workbook with multiple sheets
        MARKDOWN: Markdown documentation format
    """

    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    MARKDOWN = "markdown"


class ExportRequest(BaseModel):
    """
    Request schema for exporting a dictionary.

    Attributes:
        format: Desired export format
        version_id: Specific version to export (optional, defaults to latest)
        include_statistics: Include statistical metadata
        include_annotations: Include field annotations
        include_pii_info: Include PII detection information
        fields_filter: Optional list of field paths to include
        pii_only: Only export fields marked as PII
    """

    format: ExportFormat = Field(
        ...,
        description="Export format"
    )
    version_id: UUID | None = Field(
        None,
        description="Specific version to export (defaults to latest)"
    )
    include_statistics: bool = Field(
        True,
        description="Include statistical metadata"
    )
    include_annotations: bool = Field(
        True,
        description="Include field annotations"
    )
    include_pii_info: bool = Field(
        True,
        description="Include PII detection info"
    )
    fields_filter: list[str] | None = Field(
        None,
        description="Specific field paths to include"
    )
    pii_only: bool = Field(
        False,
        description="Only export PII fields"
    )

    @field_validator("fields_filter")
    @classmethod
    def validate_fields_filter(cls, v: list[str] | None) -> list[str] | None:
        """Remove empty field paths."""
        if v is not None:
            cleaned = [f.strip() for f in v if f and f.strip()]
            return cleaned if cleaned else None
        return v


class ExportResponse(BaseModel):
    """
    Response schema for export operations.

    The actual file content is returned as a streaming response
    with appropriate Content-Type headers. This schema represents
    the metadata returned in some export scenarios.

    Attributes:
        dictionary_id: UUID of exported dictionary
        version_number: Version number exported
        format: Export format used
        filename: Suggested filename for download
        file_size: Size of exported file in bytes
        generated_at: When export was generated
        expires_at: When download link expires (if applicable)
        download_url: Temporary download URL (if async export)
    """

    dictionary_id: UUID = Field(..., description="Exported dictionary ID")
    version_number: int = Field(..., ge=1, description="Version number")
    format: ExportFormat = Field(..., description="Export format")
    filename: str = Field(..., description="Suggested filename")
    file_size: int | None = Field(
        None,
        ge=0,
        description="File size in bytes"
    )
    generated_at: datetime = Field(..., description="Generation timestamp")
    expires_at: datetime | None = Field(
        None,
        description="Download link expiration"
    )
    download_url: str | None = Field(
        None,
        description="Temporary download URL"
    )

    model_config = ConfigDict(from_attributes=True)


class ExportMetadata(BaseModel):
    """
    Metadata included in exported files.

    This is embedded in JSON exports and as a header in other formats.

    Attributes:
        dictionary_name: Name of the dictionary
        dictionary_id: UUID of the dictionary
        version_number: Version number
        exported_at: Export timestamp
        exported_by: Email of user who requested export
        total_fields: Number of fields included
        format: Export format
        filters_applied: Description of any filters applied
    """

    dictionary_name: str = Field(..., description="Dictionary name")
    dictionary_id: UUID = Field(..., description="Dictionary UUID")
    version_number: int = Field(..., ge=1, description="Version number")
    exported_at: datetime = Field(..., description="Export timestamp")
    exported_by: str | None = Field(None, description="Exporter email")
    total_fields: int = Field(..., ge=0, description="Fields included")
    format: ExportFormat = Field(..., description="Export format")
    filters_applied: dict[str, Any] | None = Field(
        None,
        description="Filters applied"
    )


class CSVExportOptions(BaseModel):
    """
    Additional options for CSV export format.

    Attributes:
        delimiter: CSV delimiter character
        include_header: Include column headers
        quote_all: Quote all fields (not just strings)
        columns: Specific columns to include in order
    """

    delimiter: str = Field(
        ",",
        min_length=1,
        max_length=1,
        description="CSV delimiter"
    )
    include_header: bool = Field(
        True,
        description="Include column headers"
    )
    quote_all: bool = Field(
        False,
        description="Quote all fields"
    )
    columns: list[str] | None = Field(
        None,
        description="Columns to include (in order)"
    )


class ExcelExportOptions(BaseModel):
    """
    Additional options for Excel export format.

    Attributes:
        sheet_name: Name for the main worksheet
        include_summary_sheet: Include summary/metadata sheet
        freeze_header: Freeze header row
        auto_filter: Enable auto-filter on headers
        column_width_auto: Auto-adjust column widths
    """

    sheet_name: str = Field(
        "Data Dictionary",
        max_length=31,  # Excel sheet name limit
        description="Worksheet name"
    )
    include_summary_sheet: bool = Field(
        True,
        description="Include summary sheet"
    )
    freeze_header: bool = Field(
        True,
        description="Freeze header row"
    )
    auto_filter: bool = Field(
        True,
        description="Enable auto-filter"
    )
    column_width_auto: bool = Field(
        True,
        description="Auto-adjust column widths"
    )


class MarkdownExportOptions(BaseModel):
    """
    Additional options for Markdown export format.

    Attributes:
        include_toc: Include table of contents
        group_by_parent: Group fields by parent path
        include_examples: Include sample values as examples
        heading_level: Starting heading level (1-6)
    """

    include_toc: bool = Field(
        True,
        description="Include table of contents"
    )
    group_by_parent: bool = Field(
        True,
        description="Group fields by parent"
    )
    include_examples: bool = Field(
        True,
        description="Include sample values"
    )
    heading_level: int = Field(
        1,
        ge=1,
        le=6,
        description="Starting heading level"
    )


class BatchExportRequest(BaseModel):
    """
    Request schema for exporting multiple dictionaries at once.

    Attributes:
        dictionary_ids: List of dictionary UUIDs to export
        format: Export format (all dictionaries use same format)
        include_statistics: Include statistics
        include_annotations: Include annotations
        archive_format: Archive format for multiple files (zip, tar.gz)
    """

    dictionary_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Dictionary IDs to export"
    )
    format: ExportFormat = Field(..., description="Export format")
    include_statistics: bool = Field(True, description="Include statistics")
    include_annotations: bool = Field(True, description="Include annotations")
    archive_format: str | None = Field(
        "zip",
        description="Archive format (zip or tar.gz)"
    )

    @field_validator("archive_format")
    @classmethod
    def validate_archive_format(cls, v: str | None) -> str | None:
        """Validate archive format."""
        if v is not None:
            allowed = {"zip", "tar.gz", "tgz"}
            if v not in allowed:
                raise ValueError(f"archive_format must be one of {allowed}")
        return v


class BatchExportResponse(BaseModel):
    """
    Response for batch export operations.

    Attributes:
        export_id: Unique identifier for this batch export
        total_dictionaries: Number of dictionaries being exported
        status: Export status (pending, processing, completed, failed)
        created_at: When export was initiated
        download_url: URL to download archive when completed
        expires_at: When download expires
    """

    export_id: UUID = Field(..., description="Batch export ID")
    total_dictionaries: int = Field(..., ge=1, description="Dictionaries count")
    status: str = Field(..., description="Export status")
    created_at: datetime = Field(..., description="Creation timestamp")
    download_url: str | None = Field(None, description="Download URL")
    expires_at: datetime | None = Field(None, description="Expiration time")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value."""
        allowed = {"pending", "processing", "completed", "failed"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v
