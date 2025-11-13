"""Export endpoints for generating data dictionary exports."""
import logging
from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.api.dependencies import (
    get_current_user,
    get_export_service,
)
from src.core.exceptions import NotFoundError
from src.core.exceptions import ValidationError as AppValidationError
from src.services.export_service import ExportService

logger = logging.getLogger(__name__)
router = APIRouter()


class BatchExportRequest(BaseModel):
    """Request model for batch export."""
    dictionary_ids: list[UUID]
    include_statistics: bool = True
    include_annotations: bool = True
    include_pii_info: bool = True


@router.get(
    "/{dictionary_id}/excel",
    response_class=FileResponse,
    summary="Export to Excel",
    description="Export a dictionary version to Excel format with formatted sheets.",
)
async def export_to_excel(
    dictionary_id: UUID,
    version_id: UUID | None = Query(
        None, description="Specific version (defaults to latest)"
    ),
    include_statistics: bool = Query(True, description="Include statistical data"),
    include_annotations: bool = Query(True, description="Include annotations"),
    include_pii_info: bool = Query(True, description="Include PII detection info"),
    current_user: str = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
) -> FileResponse:
    """
    Export dictionary to Excel format.

    Creates a formatted Excel workbook with:
    - Data Dictionary sheet with all field information
    - Metadata sheet with dictionary and version details
    - Formatted headers, borders, and conditional formatting

    Args:
        dictionary_id: Dictionary UUID
        version_id: Optional specific version UUID (defaults to latest)
        include_statistics: Include statistical metadata
        include_annotations: Include field annotations
        include_pii_info: Include PII detection information
        current_user: Current authenticated user
        export_service: Export service instance

    Returns:
        FileResponse: Excel file download

    Raises:
        HTTPException: If dictionary/version not found or export fails
    """
    try:
        # Export to Excel using service
        file_path = export_service.export_to_excel(
            dictionary_id=dictionary_id,
            version_id=version_id,
            include_statistics=include_statistics,
            include_annotations=include_annotations,
            include_pii_info=include_pii_info,
        )

        # Get filename from service metadata
        dictionary_name = export_service.get_dictionary_name(dictionary_id)
        version_number = export_service.get_version_number(
            dictionary_id, version_id
        )

        filename = f"{dictionary_name}_v{version_number}_{datetime.now().strftime('%Y%m%d')}.xlsx"

        logger.info(
            f"User {current_user} exported dictionary {dictionary_id} to Excel"
        )

        return FileResponse(
            path=str(file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-cache",
            },
        )

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error exporting dictionary {dictionary_id} to Excel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export to Excel",
        )


@router.get(
    "/{dictionary_id}/json",
    summary="Export to JSON",
    description="Export a dictionary version to JSON format.",
)
async def export_to_json(
    dictionary_id: UUID,
    version_id: UUID | None = Query(
        None, description="Specific version (defaults to latest)"
    ),
    include_statistics: bool = Query(True, description="Include statistical data"),
    include_annotations: bool = Query(True, description="Include annotations"),
    include_pii_info: bool = Query(True, description="Include PII detection info"),
    current_user: str = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
) -> dict:
    """
    Export dictionary to JSON format.

    Returns a complete JSON representation of the dictionary including
    all field metadata, statistics, and annotations.

    Args:
        dictionary_id: Dictionary UUID
        version_id: Optional specific version UUID (defaults to latest)
        include_statistics: Include statistical metadata
        include_annotations: Include field annotations
        include_pii_info: Include PII detection information
        current_user: Current authenticated user
        export_service: Export service instance

    Returns:
        dict: Complete dictionary data in JSON format

    Raises:
        HTTPException: If dictionary/version not found or export fails
    """
    try:
        # Get dictionary and version data
        export_data = export_service.export_to_json(
            dictionary_id=dictionary_id,
            version_id=version_id,
            include_statistics=include_statistics,
            include_annotations=include_annotations,
            include_pii_info=include_pii_info,
        )

        logger.info(
            f"User {current_user} exported dictionary {dictionary_id} to JSON"
        )

        return export_data

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error exporting dictionary {dictionary_id} to JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export to JSON",
        )


@router.get(
    "/{dictionary_id}/versions/compare/excel",
    response_class=FileResponse,
    summary="Export version comparison to Excel",
    description="Compare two versions and export the comparison to Excel.",
)
async def export_version_comparison(
    dictionary_id: UUID,
    version_1: int = Query(..., ge=1, description="First version number"),
    version_2: int = Query(..., ge=1, description="Second version number"),
    current_user: str = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
) -> FileResponse:
    """
    Export version comparison to Excel.

    Creates an Excel workbook showing:
    - Summary of changes between versions
    - Detailed field-by-field comparison
    - Fields added, removed, and modified

    Args:
        dictionary_id: Dictionary UUID
        version_1: First version number
        version_2: Second version number
        current_user: Current authenticated user
        export_service: Export service instance

    Returns:
        FileResponse: Excel file download with comparison

    Raises:
        HTTPException: If versions not found or comparison fails
    """
    try:
        # Export comparison to Excel
        file_path = export_service.export_version_comparison(
            dictionary_id=dictionary_id,
            version_1_number=version_1,
            version_2_number=version_2,
        )

        # Get filename
        dictionary_name = export_service.get_dictionary_name(dictionary_id)
        filename = f"{dictionary_name}_comparison_v{version_1}_vs_v{version_2}_{datetime.now().strftime('%Y%m%d')}.xlsx"

        logger.info(
            f"User {current_user} exported version comparison for dictionary {dictionary_id}"
        )

        return FileResponse(
            path=str(file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-cache",
            },
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
            f"Error exporting version comparison for dictionary {dictionary_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export version comparison",
        )


@router.post(
    "/batch/excel",
    response_class=FileResponse,
    summary="Batch export to Excel",
    description="Export multiple dictionaries to a single Excel workbook with each dictionary as a separate sheet.",
)
async def batch_export_to_excel(
    request: BatchExportRequest = Body(...),
    current_user: str = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
) -> FileResponse:
    """
    Batch export multiple dictionaries to Excel.

    Creates a single Excel workbook with:
    - One sheet per dictionary (latest version)
    - Each sheet formatted like individual exports
    - Summary sheet with all dictionaries metadata

    Args:
        request: Batch export request with dictionary IDs and options
        current_user: Current authenticated user
        export_service: Export service instance

    Returns:
        FileResponse: Excel file download with all dictionaries

    Raises:
        HTTPException: If any dictionary not found or export fails
    """
    try:
        # Validate we have at least one dictionary
        if not request.dictionary_ids:
            raise AppValidationError("At least one dictionary ID is required")

        # Export to Excel using service
        file_path = export_service.batch_export_to_excel(
            dictionary_ids=request.dictionary_ids,
            include_statistics=request.include_statistics,
            include_annotations=request.include_annotations,
            include_pii_info=request.include_pii_info,
        )

        # Create filename
        filename = f"data_dictionaries_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        logger.info(
            f"User {current_user} batch exported {len(request.dictionary_ids)} dictionaries to Excel"
        )

        return FileResponse(
            path=str(file_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-cache",
            },
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
        logger.error(f"Error batch exporting dictionaries to Excel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to batch export to Excel",
        )
