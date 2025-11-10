"""
Version schemas for API request/response validation.

This module contains schemas for version management, including
version creation, comparison, and change tracking.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VersionCreate(BaseModel):
    """
    Request schema for creating a new version.

    Versions are typically created by uploading a new JSON file
    for an existing dictionary.

    Attributes:
        created_by: Email of user creating the version
        generate_ai_descriptions: Whether to generate AI descriptions
        notes: Optional release notes or change description
    """

    created_by: str | None = Field(
        None,
        description="Email of version creator"
    )
    generate_ai_descriptions: bool = Field(
        True,
        description="Generate AI descriptions for new/changed fields"
    )
    notes: str | None = Field(
        None,
        max_length=5000,
        description="Release notes or change description"
    )


class VersionResponse(BaseModel):
    """
    Full version response schema.

    Attributes:
        id: Version UUID
        dictionary_id: Parent dictionary UUID
        version_number: Sequential version number (1, 2, 3, ...)
        field_count: Number of fields in this version
        created_at: Version creation timestamp
        created_by: Creator email
        notes: Release notes
        source_file_name: Source file for this version
        source_file_size: Source file size in bytes
        total_records_analyzed: Number of records analyzed
        metadata: Custom metadata
    """

    id: UUID = Field(..., description="Version unique identifier")
    dictionary_id: UUID = Field(..., description="Parent dictionary ID")
    version_number: int = Field(..., ge=1, description="Sequential version number")
    field_count: int = Field(..., ge=0, description="Number of fields")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: str | None = Field(None, description="Creator email")
    notes: str | None = Field(None, description="Release notes")
    source_file_name: str | None = Field(
        None,
        description="Source filename"
    )
    source_file_size: int | None = Field(
        None,
        ge=0,
        description="Source file size in bytes"
    )
    total_records_analyzed: int | None = Field(
        None,
        ge=0,
        description="Records analyzed"
    )
    metadata: dict[str, Any] | None = Field(
        None,
        description="Custom metadata"
    )

    model_config = ConfigDict(from_attributes=True)


class VersionListItem(BaseModel):
    """
    Condensed version information for list endpoints.

    Attributes:
        id: Version UUID
        version_number: Sequential version number
        field_count: Number of fields
        created_at: Creation timestamp
        created_by: Creator email
        notes_preview: First 200 chars of notes
    """

    id: UUID = Field(..., description="Version unique identifier")
    version_number: int = Field(..., ge=1, description="Sequential version number")
    field_count: int = Field(..., ge=0, description="Number of fields")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: str | None = Field(None, description="Creator email")
    notes_preview: str | None = Field(
        None,
        max_length=200,
        description="Preview of release notes"
    )

    model_config = ConfigDict(from_attributes=True)


class FieldChangeData(BaseModel):
    """
    Field metadata snapshot for version comparison.

    Contains relevant field properties that can change between versions.

    Attributes:
        data_type: Field data type
        semantic_type: Semantic type
        is_nullable: Nullable flag
        is_array: Array flag
        array_item_type: Array item type
        is_pii: PII flag
        pii_type: PII type
    """

    data_type: str | None = Field(None, description="Data type")
    semantic_type: str | None = Field(None, description="Semantic type")
    is_nullable: bool | None = Field(None, description="Nullable")
    is_array: bool | None = Field(None, description="Is array")
    array_item_type: str | None = Field(None, description="Array item type")
    is_pii: bool | None = Field(None, description="Contains PII")
    pii_type: str | None = Field(None, description="PII type")


class ChangeDetail(BaseModel):
    """
    Detailed information about a single field change between versions.

    Attributes:
        change_type: Type of change (added, removed, modified)
        field_path: Full field path affected
        version_1_data: Field data in version 1 (null if added)
        version_2_data: Field data in version 2 (null if removed)
        is_breaking: Whether this is a breaking change
        description: Human-readable change description
    """

    change_type: str = Field(
        ...,
        description="Type of change (added, removed, modified)"
    )
    field_path: str = Field(..., description="Field path affected")
    version_1_data: FieldChangeData | None = Field(
        None,
        description="Field data in version 1"
    )
    version_2_data: FieldChangeData | None = Field(
        None,
        description="Field data in version 2"
    )
    is_breaking: bool = Field(
        False,
        description="Whether this is a breaking change"
    )
    description: str | None = Field(
        None,
        description="Human-readable change description"
    )

    @field_validator("change_type")
    @classmethod
    def validate_change_type(cls, v: str) -> str:
        """Validate change_type is one of the allowed values."""
        allowed = {"added", "removed", "modified"}
        if v not in allowed:
            raise ValueError(f"change_type must be one of {allowed}")
        return v


class ChangeSummary(BaseModel):
    """
    High-level summary of changes between versions.

    Attributes:
        fields_added: Number of new fields
        fields_removed: Number of deleted fields
        fields_modified: Number of changed fields
        breaking_changes: Number of breaking changes
    """

    fields_added: int = Field(..., ge=0, description="New fields count")
    fields_removed: int = Field(..., ge=0, description="Deleted fields count")
    fields_modified: int = Field(..., ge=0, description="Changed fields count")
    breaking_changes: int = Field(..., ge=0, description="Breaking changes count")


class VersionInfo(BaseModel):
    """
    Basic version information for comparison.

    Attributes:
        id: Version UUID
        version_number: Version number
        created_at: Creation timestamp
    """

    id: UUID = Field(..., description="Version UUID")
    version_number: int = Field(..., ge=1, description="Version number")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class VersionComparisonResponse(BaseModel):
    """
    Complete response for version comparison.

    Shows all differences between two versions of a dictionary.

    Attributes:
        dictionary_id: Parent dictionary UUID
        version_1: Info about first version
        version_2: Info about second version
        summary: High-level change summary
        changes: Detailed list of all changes
    """

    dictionary_id: UUID = Field(..., description="Parent dictionary ID")
    version_1: VersionInfo = Field(..., description="First version info")
    version_2: VersionInfo = Field(..., description="Second version info")
    summary: ChangeSummary = Field(..., description="Change summary")
    changes: list[ChangeDetail] = Field(
        ...,
        description="Detailed list of changes"
    )

    model_config = ConfigDict(from_attributes=True)


class VersionDelete(BaseModel):
    """
    Response schema for version deletion.

    Note: Only the latest version can typically be deleted to maintain
    version history integrity.

    Attributes:
        success: Whether deletion was successful
        message: Confirmation message
        deleted_id: UUID of deleted version
        new_latest_version: New latest version number after deletion
    """

    success: bool = Field(..., description="Deletion success")
    message: str = Field(..., description="Confirmation message")
    deleted_id: UUID = Field(..., description="Deleted version ID")
    new_latest_version: int | None = Field(
        None,
        description="New latest version number"
    )
