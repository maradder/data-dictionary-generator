"""Search endpoints for querying dictionary fields."""
import logging
from uuid import UUID

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    status,
)

from src.api.dependencies import DatabaseSession
from src.models.field import Field
from src.repositories.field_repo import FieldRepository
from src.schemas.common import PaginatedResponse, PaginationMeta
from src.schemas.field import AnnotationResponse, FieldResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/fields",
    response_model=PaginatedResponse[FieldResponse],
    summary="Search fields",
    description="Search for fields across dictionaries by name, type, or other criteria.",
)
async def search_fields(
    query: str | None = Query(
        None,
        min_length=1,
        description="Search query for field name/path",
    ),
    data_type: str | None = Query(
        None,
        description="Filter by data type (string, integer, float, etc.)",
    ),
    semantic_type: str | None = Query(
        None,
        description="Filter by semantic type (email, phone, url, etc.)",
    ),
    is_pii: bool | None = Query(
        None,
        description="Filter by PII status",
    ),
    dictionary_id: UUID | None = Query(
        None,
        description="Filter by specific dictionary",
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    db: DatabaseSession = None,
) -> PaginatedResponse[FieldResponse]:
    """
    Search for fields across dictionaries.

    Allows filtering by:
    - Field name/path (text search)
    - Data type
    - Semantic type
    - PII status
    - Specific dictionary

    Args:
        query: Text search for field name or path
        data_type: Filter by data type
        semantic_type: Filter by semantic type
        is_pii: Filter by PII status
        dictionary_id: Filter by specific dictionary
        limit: Number of results per page
        offset: Number of results to skip
        db: Database session

    Returns:
        PaginatedResponse[FieldResponse]: Paginated search results

    Raises:
        HTTPException: If search fails
    """
    try:
        field_repo = FieldRepository(db=db)

        # Build filter conditions
        filters = []

        if data_type:
            filters.append(Field.data_type == data_type)

        if semantic_type:
            filters.append(Field.semantic_type == semantic_type)

        if is_pii is not None:
            filters.append(Field.is_pii == is_pii)

        # Perform global search across all versions
        fields, total = field_repo.global_search(
            query=query,
            limit=limit,
            offset=offset,
            additional_filters=filters if filters else None,
            dictionary_id=dictionary_id,
        )

        # Convert to response models
        items = []
        for field in fields:
            # Get annotation if exists (use first annotation)
            annotation = None
            if field.annotations:
                ann = field.annotations[0]
                annotation = AnnotationResponse(
                    description=ann.description,
                    business_name=ann.business_name,
                    is_ai_generated=ann.is_ai_generated,
                    ai_model_version=ann.ai_model_version,
                    tags=ann.tags,
                    business_owner=ann.business_owner,
                    updated_at=ann.updated_at,
                    updated_by=ann.updated_by,
                )

            # Extract sample values from JSON field
            sample_values = None
            if field.sample_values and isinstance(field.sample_values, dict):
                sample_values = field.sample_values.get("values", [])

            items.append(
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
                    null_percentage=float(field.null_percentage)
                    if field.null_percentage
                    else None,
                    total_count=field.total_count,
                    distinct_count=field.distinct_count,
                    cardinality_ratio=float(field.cardinality_ratio)
                    if field.cardinality_ratio
                    else None,
                    min_value=float(field.min_value) if field.min_value else None,
                    max_value=float(field.max_value) if field.max_value else None,
                    mean_value=float(field.mean_value) if field.mean_value else None,
                    median_value=float(field.median_value)
                    if field.median_value
                    else None,
                    std_dev=float(field.std_dev) if field.std_dev else None,
                    percentile_25=float(field.percentile_25)
                    if field.percentile_25
                    else None,
                    percentile_50=float(field.percentile_50)
                    if field.percentile_50
                    else None,
                    percentile_75=float(field.percentile_75)
                    if field.percentile_75
                    else None,
                    is_pii=field.is_pii,
                    pii_type=field.pii_type,
                    confidence_score=float(field.confidence_score)
                    if field.confidence_score
                    else None,
                    annotation=annotation,
                )
            )

        return PaginatedResponse(
            data=items,
            meta=PaginationMeta(
                total=total,
                limit=limit,
                offset=offset,
                has_more=(offset + len(items) < total),
            ),
        )

    except Exception as e:
        logger.error(f"Error searching fields: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search fields",
        )


@router.get(
    "/dictionaries",
    summary="Search dictionaries",
    description="Search for dictionaries by name.",
)
async def search_dictionaries(
    query: str = Query(..., min_length=1, description="Search query for dictionary name"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    db: DatabaseSession = None,
) -> dict:
    """
    Search for dictionaries by name.

    Args:
        query: Text search for dictionary name
        limit: Number of results per page
        offset: Number of results to skip
        db: Database session

    Returns:
        dict: Search results with dictionaries

    Raises:
        HTTPException: If search fails
    """
    try:
        from repositories.dictionary_repo import DictionaryRepository
        from schemas.dictionary import DictionaryListItem

        dict_repo = DictionaryRepository(db=db)

        # Search dictionaries
        dictionaries, total = dict_repo.search_by_name(
            query=query,
            limit=limit,
            offset=offset,
        )

        # Convert to list items
        items = [
            DictionaryListItem(
                id=d.id,
                name=d.name,
                description=d.description,
                created_at=d.created_at,
                created_by=d.created_by,
                version_count=len(d.versions),
                latest_version_number=(
                    max(v.version_number for v in d.versions) if d.versions else 1
                ),
                field_count=(
                    len(d.versions[-1].fields)
                    if d.versions and d.versions[-1].fields
                    else 0
                ),
            )
            for d in dictionaries
        ]

        return {
            "data": [item.model_dump() for item in items],
            "meta": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + len(items) < total),
            },
        }

    except Exception as e:
        logger.error(f"Error searching dictionaries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search dictionaries",
        )
