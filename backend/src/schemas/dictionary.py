"""
Dictionary schemas for API request/response validation.

This module contains all Pydantic schemas related to data dictionary
operations, including creation, updates, and response formats.
"""

import re
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DictionaryCreate(BaseModel):
    """
    Request schema for creating a new data dictionary.

    This schema validates the multipart form data submitted when
    creating a dictionary. The file itself is handled separately
    by FastAPI's UploadFile.

    Attributes:
        name: Display name for the dictionary (1-255 chars)
        description: Optional detailed description
        created_by: Email of the user creating the dictionary
        generate_ai_descriptions: Whether to generate AI descriptions for fields
        metadata: Optional custom metadata as JSON object
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Dictionary name (1-255 characters)"
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Detailed description of the dictionary"
    )
    created_by: str | None = Field(
        None,
        description="Email address of creator"
    )
    generate_ai_descriptions: bool = Field(
        True,
        description="Generate AI descriptions for fields"
    )
    metadata: dict[str, Any] | None = Field(
        None,
        description="Custom metadata as JSON object"
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Validate that name is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_not_whitespace(cls, v: str | None) -> str | None:
        """Strip whitespace from description if provided."""
        if v is not None:
            stripped = v.strip()
            return stripped if stripped else None
        return v

    @field_validator("created_by")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        """Validate email format if provided."""
        if v is not None and v.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError("Invalid email format")
            return v.strip()
        return v


class DictionaryUpdate(BaseModel):
    """
    Request schema for updating an existing dictionary.

    All fields are optional - only provided fields will be updated.

    Attributes:
        name: New display name
        description: New description (can be set to null to clear)
        metadata: Updated metadata (merges with existing)
    """

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated dictionary name"
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Updated description"
    )
    metadata: dict[str, Any] | None = Field(
        None,
        description="Updated metadata (merges with existing)"
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        """Validate that name is not empty or whitespace only."""
        if v is not None:
            if not v.strip():
                raise ValueError("Name cannot be empty or whitespace")
            return v.strip()
        return v


class VersionSummary(BaseModel):
    """
    Summary information for a dictionary version.

    Used in nested contexts where full version details aren't needed.

    Attributes:
        id: Version UUID
        version_number: Sequential version number (1, 2, 3, ...)
        field_count: Number of fields in this version
        created_at: When this version was created
        created_by: Email of user who created the version
    """

    id: UUID = Field(..., description="Version unique identifier")
    version_number: int = Field(..., ge=1, description="Sequential version number")
    field_count: int = Field(..., ge=0, description="Number of fields in version")
    created_at: datetime = Field(..., description="Version creation timestamp")
    created_by: str | None = Field(None, description="Creator email address")

    model_config = ConfigDict(from_attributes=True)


class DictionaryResponse(BaseModel):
    """
    Full response schema for a data dictionary.

    Returned when getting details for a specific dictionary.

    Attributes:
        id: Dictionary UUID
        name: Display name
        description: Detailed description
        source_file_name: Original uploaded filename
        source_file_size: File size in bytes
        total_records_analyzed: Number of JSON records analyzed
        created_at: Creation timestamp
        created_by: Creator email
        updated_at: Last update timestamp
        metadata: Custom metadata
        latest_version: Summary of the most recent version
        versions: List of all version summaries (in detail view)
    """

    id: UUID = Field(..., description="Dictionary unique identifier")
    name: str = Field(..., description="Dictionary name")
    description: str | None = Field(None, description="Dictionary description")
    source_file_name: str | None = Field(
        None,
        description="Original source filename"
    )
    source_file_size: int | None = Field(
        None,
        ge=0,
        description="Source file size in bytes"
    )
    total_records_analyzed: int | None = Field(
        None,
        ge=0,
        description="Number of records analyzed"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: str | None = Field(None, description="Creator email")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: dict[str, Any] | None = Field(
        None,
        description="Custom metadata"
    )
    latest_version: VersionSummary | None = Field(
        None,
        description="Most recent version summary"
    )
    versions: list[VersionSummary] | None = Field(
        None,
        description="All versions (only in detail view)"
    )

    model_config = ConfigDict(from_attributes=True)


class DictionaryListItem(BaseModel):
    """
    Condensed dictionary information for list endpoints.

    Optimized schema for listing many dictionaries with less data per item.

    Attributes:
        id: Dictionary UUID
        name: Display name
        description: Short description
        created_at: Creation timestamp
        created_by: Creator email
        version_count: Total number of versions
        latest_version_number: Most recent version number
        field_count: Number of fields in latest version
    """

    id: UUID = Field(..., description="Dictionary unique identifier")
    name: str = Field(..., description="Dictionary name")
    description: str | None = Field(None, description="Dictionary description")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: str | None = Field(None, description="Creator email")
    version_count: int = Field(..., ge=0, description="Total number of versions")
    latest_version_number: int = Field(
        ...,
        ge=1,
        description="Latest version number"
    )
    field_count: int = Field(
        ...,
        ge=0,
        description="Fields in latest version"
    )

    model_config = ConfigDict(from_attributes=True)


class DictionaryDelete(BaseModel):
    """
    Response schema for dictionary deletion.

    Attributes:
        success: Whether deletion was successful
        message: Confirmation message
        deleted_id: UUID of the deleted dictionary
    """

    success: bool = Field(..., description="Deletion success status")
    message: str = Field(..., description="Confirmation message")
    deleted_id: UUID = Field(..., description="ID of deleted dictionary")
