"""
Field schemas for API request/response validation.

This module contains schemas for field metadata, annotations,
and field-related operations.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnnotationResponse(BaseModel):
    """
    Annotation data attached to a field.

    Annotations provide human-readable and business context for fields,
    including AI-generated or manually entered descriptions.

    Attributes:
        description: Detailed field description
        business_name: Business-friendly name for the field
        is_ai_generated: Whether description was AI-generated
        ai_model_version: AI model used (e.g., 'gpt-4', 'claude-3')
        tags: Categorization tags (e.g., ['pii', 'required', 'deprecated'])
        business_owner: Team or person responsible for this field
        updated_at: When annotation was last updated
        updated_by: Email of user who last updated
    """

    description: str | None = Field(
        None,
        max_length=5000,
        description="Detailed field description"
    )
    business_name: str | None = Field(
        None,
        max_length=255,
        description="Business-friendly field name"
    )
    is_ai_generated: bool = Field(
        False,
        description="Whether description is AI-generated"
    )
    ai_model_version: str | None = Field(
        None,
        max_length=50,
        description="AI model used for generation"
    )
    tags: list[str] | None = Field(
        None,
        description="Categorization tags"
    )
    business_owner: str | None = Field(
        None,
        max_length=255,
        description="Team or person responsible"
    )
    updated_at: datetime | None = Field(
        None,
        description="Last update timestamp"
    )
    updated_by: str | None = Field(
        None,
        description="Email of last updater"
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("tags")
    @classmethod
    def tags_not_empty(cls, v: list[str] | None) -> list[str] | None:
        """Remove empty strings from tags list."""
        if v is not None:
            cleaned = [tag.strip() for tag in v if tag and tag.strip()]
            return cleaned if cleaned else None
        return v


class AnnotationUpdate(BaseModel):
    """
    Request schema for updating field annotations.

    All fields are optional - only provided fields will be updated.

    Attributes:
        description: Updated field description
        business_name: Updated business name
        business_owner: Updated business owner
        tags: Updated tags (replaces existing)
        updated_by: Email of user making the update
    """

    description: str | None = Field(
        None,
        max_length=5000,
        description="Updated field description"
    )
    business_name: str | None = Field(
        None,
        max_length=255,
        description="Updated business name"
    )
    business_owner: str | None = Field(
        None,
        max_length=255,
        description="Updated business owner"
    )
    tags: list[str] | None = Field(
        None,
        description="Updated tags (replaces existing)"
    )
    updated_by: str | None = Field(
        None,
        description="Email of user making update"
    )

    @field_validator("tags")
    @classmethod
    def tags_not_empty(cls, v: list[str] | None) -> list[str] | None:
        """Remove empty strings from tags list."""
        if v is not None:
            cleaned = [tag.strip() for tag in v if tag and tag.strip()]
            return cleaned if cleaned else None
        return v


class FieldResponse(BaseModel):
    """
    Complete field metadata response.

    Contains all available metadata for a field, including type information,
    statistics, PII detection, and annotations.

    Attributes:
        id: Field UUID
        version_id: Parent version UUID
        field_path: Full dotted path (e.g., 'user.address.city')
        field_name: Leaf field name (e.g., 'city')
        parent_path: Parent path (e.g., 'user.address')
        nesting_level: Depth in object hierarchy (0 = root level)
        data_type: Primary data type (string, integer, float, boolean, object, array)
        semantic_type: Inferred semantic type (email, phone, url, date, etc.)
        is_nullable: Whether field can be null
        is_array: Whether field is an array
        array_item_type: Type of array items if is_array=True
        sample_values: Up to 10 sample values
        null_count: Number of null occurrences
        null_percentage: Percentage of null values
        total_count: Total occurrences analyzed
        distinct_count: Number of unique values
        cardinality_ratio: distinct_count / total_count
        min_value: Minimum numeric value
        max_value: Maximum numeric value
        mean_value: Mean of numeric values
        median_value: Median of numeric values
        std_dev: Standard deviation
        percentile_25: 25th percentile
        percentile_50: 50th percentile (median)
        percentile_75: 75th percentile
        is_pii: Whether field contains PII
        pii_type: Type of PII (email, phone, ssn, etc.)
        confidence_score: Confidence in type/semantic detection (0-100)
        annotation: Human/AI annotations
    """

    id: UUID = Field(..., description="Field unique identifier")
    version_id: UUID = Field(..., description="Parent version ID")
    field_path: str = Field(..., description="Full dotted field path")
    field_name: str = Field(..., description="Leaf field name")
    parent_path: str | None = Field(None, description="Parent object path")
    nesting_level: int = Field(..., ge=0, description="Nesting depth")

    # Type information
    data_type: str = Field(..., description="Primary data type")
    semantic_type: str | None = Field(None, description="Semantic type")
    is_nullable: bool = Field(..., description="Can be null")
    is_array: bool = Field(..., description="Is an array")
    array_item_type: str | None = Field(None, description="Array item type")

    # Sample data
    sample_values: list[Any] | None = Field(
        None,
        max_length=10,
        description="Sample values (max 10)"
    )

    # Statistics
    null_count: int = Field(..., ge=0, description="Number of nulls")
    null_percentage: float | None = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Null percentage"
    )
    total_count: int = Field(..., ge=0, description="Total occurrences")
    distinct_count: int = Field(..., ge=0, description="Unique values")
    cardinality_ratio: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Distinct/total ratio"
    )

    # Numeric statistics (for numeric fields)
    min_value: float | None = Field(None, description="Minimum value")
    max_value: float | None = Field(None, description="Maximum value")
    mean_value: float | None = Field(None, description="Mean value")
    median_value: float | None = Field(None, description="Median value")
    std_dev: float | None = Field(None, ge=0.0, description="Standard deviation")
    percentile_25: float | None = Field(None, description="25th percentile")
    percentile_50: float | None = Field(None, description="50th percentile")
    percentile_75: float | None = Field(None, description="75th percentile")

    # PII detection
    is_pii: bool = Field(..., description="Contains PII")
    pii_type: str | None = Field(None, description="Type of PII")
    confidence_score: float | None = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Detection confidence (0-100)"
    )

    # Annotation
    annotation: AnnotationResponse | None = Field(
        None,
        description="Field annotations"
    )

    model_config = ConfigDict(from_attributes=True)


class FieldListItem(BaseModel):
    """
    Condensed field information for list endpoints.

    Optimized for listing many fields without full statistics.

    Attributes:
        id: Field UUID
        field_path: Full dotted path
        field_name: Leaf field name
        data_type: Primary data type
        semantic_type: Semantic type if detected
        is_pii: Whether field contains PII
        pii_type: Type of PII
        is_nullable: Can be null
        is_array: Is an array
        annotation_summary: Brief annotation (business_name or description)
    """

    id: UUID = Field(..., description="Field unique identifier")
    field_path: str = Field(..., description="Full dotted field path")
    field_name: str = Field(..., description="Leaf field name")
    data_type: str = Field(..., description="Primary data type")
    semantic_type: str | None = Field(None, description="Semantic type")
    is_pii: bool = Field(..., description="Contains PII")
    pii_type: str | None = Field(None, description="Type of PII")
    is_nullable: bool = Field(..., description="Can be null")
    is_array: bool = Field(..., description="Is an array")
    annotation_summary: str | None = Field(
        None,
        description="Brief annotation (business_name or truncated description)"
    )

    model_config = ConfigDict(from_attributes=True)


class FieldFilterParams(BaseModel):
    """
    Query parameters for filtering fields.

    Attributes:
        filter_pii: Only return PII fields
        filter_nullable: Only return nullable fields
        data_type: Filter by data type
        semantic_type: Filter by semantic type
        search: Search in field_path, field_name, or annotations
        limit: Number of results per page
        offset: Number of results to skip
    """

    filter_pii: bool | None = Field(
        None,
        description="Filter for PII fields only"
    )
    filter_nullable: bool | None = Field(
        None,
        description="Filter for nullable fields only"
    )
    data_type: str | None = Field(
        None,
        description="Filter by data type"
    )
    semantic_type: str | None = Field(
        None,
        description="Filter by semantic type"
    )
    search: str | None = Field(
        None,
        max_length=255,
        description="Search query"
    )
    limit: int = Field(
        100,
        ge=1,
        le=1000,
        description="Results per page"
    )
    offset: int = Field(
        0,
        ge=0,
        description="Results to skip"
    )
