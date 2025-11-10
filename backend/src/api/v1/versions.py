"""Version endpoints for managing dictionary versions."""
import logging
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from src.api.dependencies import (
    get_current_user,
    get_dictionary_service,
    get_version_service,
)
from src.core.config import settings
from src.core.exceptions import NotFoundError
from src.core.exceptions import ValidationError as AppValidationError
from src.schemas.common import PaginatedResponse, PaginationMeta
from src.schemas.field import FieldResponse
from src.schemas.version import (
    ChangeDetail,
    ChangeSummary,
    FieldChangeData,
    VersionComparisonResponse,
    VersionInfo,
    VersionListItem,
    VersionResponse,
)
from src.services.dictionary_service import DictionaryService
from src.services.version_service import VersionService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/{dictionary_id}/versions",
    response_model=list[VersionListItem],
    summary="List all versions",
    description="List all versions for a specific dictionary.",
)
async def list_versions(
    dictionary_id: UUID,
    version_service: VersionService = Depends(get_version_service),
) -> list[VersionListItem]:
    """
    List all versions for a dictionary.

    Args:
        dictionary_id: Dictionary UUID
        version_service: Version service instance

    Returns:
        List[VersionListItem]: List of version summaries

    Raises:
        HTTPException: If dictionary not found or error occurs
    """
    try:
        versions = version_service.list_versions(dictionary_id)

        return [
            VersionListItem(
                id=v.id,
                version_number=v.version_number,
                field_count=len(v.fields) if v.fields else 0,
                created_at=v.created_at,
                created_by=v.created_by,
                notes_preview=(
                    v.notes[:200] if v.notes and len(v.notes) > 200 else v.notes
                ),
            )
            for v in versions
        ]

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary {dictionary_id} not found",
        )
    except Exception as e:
        logger.error(f"Error listing versions for dictionary {dictionary_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve versions",
        )


@router.post(
    "/{dictionary_id}/versions",
    response_model=VersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new version",
    description="Upload a new JSON file to create a new version of the dictionary.",
)
async def create_version(
    dictionary_id: UUID,
    file: UploadFile = File(..., description="JSON file to analyze"),
    notes: str | None = Form(None, description="Release notes"),
    generate_ai_descriptions: bool = Form(
        True, description="Generate AI descriptions"
    ),
    current_user: str = Depends(get_current_user),
    dictionary_service: DictionaryService = Depends(get_dictionary_service),
) -> VersionResponse:
    """
    Create a new version from uploaded JSON file.

    Args:
        dictionary_id: Dictionary UUID
        file: JSON file to analyze
        notes: Optional release notes
        generate_ai_descriptions: Whether to generate AI descriptions
        current_user: Current authenticated user
        dictionary_service: Dictionary service instance

    Returns:
        VersionResponse: Created version details

    Raises:
        HTTPException: If file is invalid, too large, or processing fails
    """
    # Validate file type
    if not file.filename.endswith((".json", ".jsonl", ".ndjson")):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JSON files are supported (.json, .jsonl, .ndjson)",
        )

    # Validate file size
    try:
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB",
            )

        # Save to temporary file for processing
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".json", mode="wb"
        ) as temp_file:
            temp_file.write(file_content)
            temp_path = Path(temp_file.name)

        # Create new version using service
        try:
            version = dictionary_service.create_new_version(
                dictionary_id=dictionary_id,
                file_path=temp_path,
                created_by=current_user,
                generate_ai_descriptions=generate_ai_descriptions,
                notes=notes,
            )

            logger.info(
                f"Created version {version.version_number} for dictionary {dictionary_id}"
            )

            return VersionResponse(
                id=version.id,
                dictionary_id=version.dictionary_id,
                version_number=version.version_number,
                field_count=len(version.fields) if version.fields else 0,
                created_at=version.created_at,
                created_by=version.created_by,
                notes=version.notes,
                source_file_name=file.filename,
                source_file_size=file_size,
                total_records_analyzed=version.processing_stats.get("total_records")
                if version.processing_stats
                else None,
                metadata=version.metadata,
            )

        finally:
            # Clean up temporary file
            temp_path.unlink(missing_ok=True)

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary {dictionary_id} not found",
        )
    except AppValidationError as e:
        logger.warning(f"Validation error creating version: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating version: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create version",
        )


@router.get(
    "/{dictionary_id}/versions/{version_id}",
    response_model=VersionResponse,
    summary="Get version by ID",
    description="Retrieve detailed information for a specific version.",
)
async def get_version(
    dictionary_id: UUID,
    version_id: UUID,
    version_service: VersionService = Depends(get_version_service),
) -> VersionResponse:
    """
    Get specific version details.

    Args:
        dictionary_id: Dictionary UUID
        version_id: Version UUID
        version_service: Version service instance

    Returns:
        VersionResponse: Version details

    Raises:
        HTTPException: If version not found
    """
    try:
        version = version_service.get_version(version_id)

        if not version or version.dictionary_id != dictionary_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_id} not found for dictionary {dictionary_id}",
            )

        return VersionResponse(
            id=version.id,
            dictionary_id=version.dictionary_id,
            version_number=version.version_number,
            field_count=len(version.fields) if version.fields else 0,
            created_at=version.created_at,
            created_by=version.created_by,
            notes=version.notes,
            source_file_name=version.source_file_name,
            source_file_size=version.source_file_size,
            total_records_analyzed=version.processing_stats.get("total_records")
            if version.processing_stats
            else None,
            metadata=version.metadata,
        )

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_id} not found",
        )
    except Exception as e:
        logger.error(f"Error retrieving version {version_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve version",
        )


@router.get(
    "/{dictionary_id}/versions/{version_id}/fields",
    response_model=PaginatedResponse[FieldResponse],
    summary="Get fields for version",
    description="Retrieve all fields for a specific version with pagination support.",
)
async def get_version_fields(
    dictionary_id: UUID,
    version_id: UUID,
    limit: int = Query(100, ge=1, le=1000, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    version_service: VersionService = Depends(get_version_service),
) -> PaginatedResponse[FieldResponse]:
    """
    Get all fields for a specific version with pagination.

    This endpoint retrieves complete field metadata including:
    - Type information (data type, semantic type)
    - Statistics (null counts, distinct values, numeric stats)
    - PII detection results
    - Field annotations (descriptions, business names, tags)

    Args:
        dictionary_id: Dictionary UUID
        version_id: Version UUID
        limit: Maximum number of fields to return (default 100, max 1000)
        offset: Number of fields to skip (default 0)
        version_service: Version service instance

    Returns:
        PaginatedResponse[FieldResponse]: Paginated list of fields with metadata

    Raises:
        HTTPException: If version not found or access error occurs
    """
    try:
        # First verify the version exists and belongs to the dictionary
        version = version_service.get_version(version_id)

        if not version or version.dictionary_id != dictionary_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_id} not found for dictionary {dictionary_id}",
            )

        # Get paginated fields
        fields, total_count = version_service.get_version_fields_paginated(
            version_id=version_id,
            limit=limit,
            offset=offset,
        )

        # Convert fields to response schema
        field_responses = []
        for field in fields:
            # Get the first annotation if it exists
            annotation = field.annotations[0] if field.annotations else None

            # Extract sample values from JSON field
            sample_values = None
            if field.sample_values and isinstance(field.sample_values, dict):
                sample_values = field.sample_values.get("values", [])

            field_responses.append(
                FieldResponse(
                    id=field.id,
                    version_id=field.version_id,
                    field_path=field.field_path,
                    field_name=field.field_name,
                    parent_path=field.parent_path,
                    nesting_level=field.nesting_level,
                    data_type=field.data_type,
                    semantic_type=field.semantic_type,
                    is_nullable=field.is_nullable,
                    is_array=field.is_array,
                    array_item_type=field.array_item_type,
                    sample_values=sample_values,
                    null_count=field.null_count,
                    null_percentage=float(field.null_percentage) if field.null_percentage else None,
                    total_count=field.total_count,
                    distinct_count=field.distinct_count,
                    cardinality_ratio=float(field.cardinality_ratio) if field.cardinality_ratio else None,
                    min_value=float(field.min_value) if field.min_value is not None else None,
                    max_value=float(field.max_value) if field.max_value is not None else None,
                    mean_value=float(field.mean_value) if field.mean_value is not None else None,
                    median_value=float(field.median_value) if field.median_value is not None else None,
                    std_dev=float(field.std_dev) if field.std_dev is not None else None,
                    percentile_25=float(field.percentile_25) if field.percentile_25 is not None else None,
                    percentile_50=float(field.percentile_50) if field.percentile_50 is not None else None,
                    percentile_75=float(field.percentile_75) if field.percentile_75 is not None else None,
                    is_pii=field.is_pii,
                    pii_type=field.pii_type,
                    confidence_score=float(field.confidence_score) if field.confidence_score else None,
                    annotation={
                        "description": annotation.description,
                        "business_name": annotation.business_name,
                        "is_ai_generated": annotation.is_ai_generated,
                        "ai_model_version": annotation.ai_model_version,
                        "tags": annotation.tags.get("tags", []) if annotation.tags else None,
                        "business_owner": annotation.business_owner,
                        "updated_at": annotation.updated_at,
                        "updated_by": annotation.updated_by,
                    } if annotation else None,
                )
            )

        # Build pagination metadata
        has_more = (offset + limit) < total_count
        pagination_meta = PaginationMeta(
            total=total_count,
            limit=limit,
            offset=offset,
            has_more=has_more,
        )

        logger.info(
            f"Retrieved {len(field_responses)} fields for version {version_id}",
            extra={
                "version_id": str(version_id),
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
            },
        )

        return PaginatedResponse(
            data=field_responses,
            meta=pagination_meta,
        )

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_id} not found",
        )
    except Exception as e:
        logger.error(f"Error retrieving fields for version {version_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve version fields",
        )


@router.get(
    "/{dictionary_id}/versions/compare",
    response_model=VersionComparisonResponse,
    summary="Compare two versions",
    description="Compare two versions of a dictionary to see field changes.",
)
async def compare_versions(
    dictionary_id: UUID,
    version_1: int = Query(..., ge=1, description="First version number"),
    version_2: int = Query(..., ge=1, description="Second version number"),
    version_service: VersionService = Depends(get_version_service),
) -> VersionComparisonResponse:
    """
    Compare two versions of a dictionary.

    Args:
        dictionary_id: Dictionary UUID
        version_1: First version number
        version_2: Second version number
        version_service: Version service instance

    Returns:
        VersionComparisonResponse: Comparison results with changes

    Raises:
        HTTPException: If versions not found or comparison fails
    """
    try:
        comparison = version_service.compare_versions(
            dictionary_id=dictionary_id,
            version_1_number=version_1,
            version_2_number=version_2,
        )

        # Build change details
        changes = []
        for change in comparison.get("changes", []):
            changes.append(
                ChangeDetail(
                    change_type=change["change_type"],
                    field_path=change["field_path"],
                    version_1_data=(
                        FieldChangeData(**change["version_1_data"])
                        if change.get("version_1_data")
                        else None
                    ),
                    version_2_data=(
                        FieldChangeData(**change["version_2_data"])
                        if change.get("version_2_data")
                        else None
                    ),
                    is_breaking=change.get("is_breaking", False),
                    description=change.get("description"),
                )
            )

        return VersionComparisonResponse(
            dictionary_id=dictionary_id,
            version_1=VersionInfo(**comparison["version_1"]),
            version_2=VersionInfo(**comparison["version_2"]),
            summary=ChangeSummary(**comparison["summary"]),
            changes=changes,
        )

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AppValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(
            f"Error comparing versions {version_1} and {version_2} for dictionary {dictionary_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare versions",
        )
