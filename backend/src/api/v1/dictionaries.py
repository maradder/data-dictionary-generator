"""Dictionary endpoints for managing data dictionaries."""
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
    DatabaseSession,
    get_current_user,
    get_dictionary_service,
)
from src.core.config import settings
from src.core.exceptions import NotFoundError
from src.core.exceptions import ValidationError as AppValidationError
from src.schemas.common import PaginatedResponse, PaginationMeta
from src.schemas.dictionary import (
    DictionaryDelete,
    DictionaryListItem,
    DictionaryResponse,
    DictionaryUpdate,
)
from src.services.dictionary_service import DictionaryService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[DictionaryListItem],
    summary="List all dictionaries",
    description="Retrieve a paginated list of all data dictionaries.",
)
async def list_dictionaries(
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    db: DatabaseSession = None,
    dictionary_service: DictionaryService = Depends(get_dictionary_service),
) -> PaginatedResponse[DictionaryListItem]:
    """
    List all dictionaries with pagination.

    Args:
        limit: Number of items per page (1-100)
        offset: Number of items to skip
        db: Database session
        dictionary_service: Dictionary service instance

    Returns:
        PaginatedResponse[DictionaryListItem]: Paginated list of dictionaries

    Raises:
        HTTPException: If database error occurs
    """
    try:
        dictionaries, total = dictionary_service.list_dictionaries(
            limit=limit, offset=offset
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
                    len(d.versions[-1].fields) if d.versions and d.versions[-1].fields else 0
                ),
            )
            for d in dictionaries
        ]

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
        logger.error(f"Error listing dictionaries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dictionaries",
        )


@router.post(
    "/",
    response_model=DictionaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new dictionary",
    description="Upload a JSON, XML, SQLite, or GeoPackage file and create a data dictionary from it.",
)
async def create_dictionary(
    file: UploadFile = File(..., description="JSON, XML, SQLite, or GeoPackage file to analyze"),
    name: str = Form(..., description="Dictionary name"),
    description: str | None = Form(None, description="Dictionary description"),
    generate_ai_descriptions: bool = Form(
        True, description="Generate AI descriptions"
    ),
    current_user: str = Depends(get_current_user),
    dictionary_service: DictionaryService = Depends(get_dictionary_service),
) -> DictionaryResponse:
    """
    Create a new dictionary from uploaded JSON, XML, SQLite, or GeoPackage file.

    Args:
        file: JSON, XML, SQLite, or GeoPackage file to analyze
        name: Dictionary name
        description: Optional description
        generate_ai_descriptions: Whether to generate AI descriptions
        current_user: Current authenticated user
        dictionary_service: Dictionary service instance

    Returns:
        DictionaryResponse: Created dictionary details

    Raises:
        HTTPException: If file is invalid, too large, or processing fails
    """
    # Validate file type
    if not file.filename.endswith((".json", ".jsonl", ".ndjson", ".xml", ".db", ".sqlite", ".sqlite3", ".gpkg", ".proto", ".desc")):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JSON, XML, SQLite, GeoPackage, and Protocol Buffer files are supported (.json, .jsonl, .ndjson, .xml, .db, .sqlite, .sqlite3, .gpkg, .proto, .desc). MongoDB Extended JSON format is auto-detected.",
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
        # Use appropriate suffix based on file type
        file_suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=file_suffix, mode="wb"
        ) as temp_file:
            temp_file.write(file_content)
            temp_path = Path(temp_file.name)

        # Create dictionary using service
        try:
            dictionary = dictionary_service.create_dictionary(
                file_path=temp_path,
                name=name,
                description=description,
                created_by=current_user,
                generate_ai_descriptions=generate_ai_descriptions,
                original_filename=file.filename,
            )

            logger.info(f"Created dictionary {dictionary.id} from file {file.filename}")

            # Get latest version for response
            latest_version = (
                dictionary.versions[-1] if dictionary.versions else None
            )

            return DictionaryResponse(
                id=dictionary.id,
                name=dictionary.name,
                description=dictionary.description,
                source_file_name=dictionary.source_file_name,
                source_file_size=dictionary.source_file_size,
                total_records_analyzed=dictionary.total_records_analyzed,
                created_at=dictionary.created_at,
                created_by=dictionary.created_by,
                updated_at=dictionary.updated_at,
                metadata=dictionary.custom_metadata,
                latest_version=(
                    {
                        "id": latest_version.id,
                        "version_number": latest_version.version_number,
                        "field_count": len(latest_version.fields),
                        "created_at": latest_version.created_at,
                        "created_by": latest_version.created_by,
                    }
                    if latest_version
                    else None
                ),
            )

        finally:
            # Clean up temporary file
            temp_path.unlink(missing_ok=True)

    except AppValidationError as e:
        logger.warning(f"Validation error creating dictionary: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating dictionary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dictionary",
        )


@router.get(
    "/{dictionary_id}",
    response_model=DictionaryResponse,
    summary="Get dictionary by ID",
    description="Retrieve detailed information for a specific dictionary.",
)
async def get_dictionary(
    dictionary_id: UUID,
    include_versions: bool = Query(
        False, description="Include all version summaries"
    ),
    dictionary_service: DictionaryService = Depends(get_dictionary_service),
) -> DictionaryResponse:
    """
    Get dictionary by ID.

    Args:
        dictionary_id: Dictionary UUID
        include_versions: Whether to include all version summaries
        dictionary_service: Dictionary service instance

    Returns:
        DictionaryResponse: Dictionary details

    Raises:
        HTTPException: If dictionary not found
    """
    try:
        dictionary = dictionary_service.get_dictionary(dictionary_id)

        if not dictionary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dictionary {dictionary_id} not found",
            )

        # Get latest version
        latest_version = dictionary.versions[-1] if dictionary.versions else None

        # Build response
        response_data = {
            "id": dictionary.id,
            "name": dictionary.name,
            "description": dictionary.description,
            "source_file_name": dictionary.source_file_name,
            "source_file_size": dictionary.source_file_size,
            "total_records_analyzed": dictionary.total_records_analyzed,
            "created_at": dictionary.created_at,
            "created_by": dictionary.created_by,
            "updated_at": dictionary.updated_at,
            "metadata": dictionary.custom_metadata,
            "latest_version": (
                {
                    "id": latest_version.id,
                    "version_number": latest_version.version_number,
                    "field_count": len(latest_version.fields),
                    "created_at": latest_version.created_at,
                    "created_by": latest_version.created_by,
                }
                if latest_version
                else None
            ),
        }

        # Include all versions if requested
        if include_versions and dictionary.versions:
            response_data["versions"] = [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "field_count": len(v.fields),
                    "created_at": v.created_at,
                    "created_by": v.created_by,
                }
                for v in dictionary.versions
            ]

        return DictionaryResponse(**response_data)

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary {dictionary_id} not found",
        )
    except Exception as e:
        logger.error(f"Error retrieving dictionary {dictionary_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dictionary",
        )


@router.put(
    "/{dictionary_id}",
    response_model=DictionaryResponse,
    summary="Update dictionary",
    description="Update dictionary metadata (name, description, metadata).",
)
async def update_dictionary(
    dictionary_id: UUID,
    update_data: DictionaryUpdate,
    dictionary_service: DictionaryService = Depends(get_dictionary_service),
) -> DictionaryResponse:
    """
    Update dictionary metadata.

    Args:
        dictionary_id: Dictionary UUID
        update_data: Update data
        dictionary_service: Dictionary service instance

    Returns:
        DictionaryResponse: Updated dictionary details

    Raises:
        HTTPException: If dictionary not found or update fails
    """
    try:
        dictionary = dictionary_service.update_dictionary(
            dictionary_id=dictionary_id,
            name=update_data.name,
            description=update_data.description,
            metadata=update_data.metadata,
        )

        # Get latest version
        latest_version = dictionary.versions[-1] if dictionary.versions else None

        return DictionaryResponse(
            id=dictionary.id,
            name=dictionary.name,
            description=dictionary.description,
            source_file_name=dictionary.source_file_name,
            source_file_size=dictionary.source_file_size,
            total_records_analyzed=dictionary.total_records_analyzed,
            created_at=dictionary.created_at,
            created_by=dictionary.created_by,
            updated_at=dictionary.updated_at,
            metadata=dictionary.custom_metadata,
            latest_version=(
                {
                    "id": latest_version.id,
                    "version_number": latest_version.version_number,
                    "field_count": len(latest_version.fields),
                    "created_at": latest_version.created_at,
                    "created_by": latest_version.created_by,
                }
                if latest_version
                else None
            ),
        )

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary {dictionary_id} not found",
        )
    except AppValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating dictionary {dictionary_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dictionary",
        )


@router.delete(
    "/{dictionary_id}",
    response_model=DictionaryDelete,
    summary="Delete dictionary",
    description="Delete a dictionary and all its versions and fields.",
)
async def delete_dictionary(
    dictionary_id: UUID,
    dictionary_service: DictionaryService = Depends(get_dictionary_service),
) -> DictionaryDelete:
    """
    Delete dictionary.

    Args:
        dictionary_id: Dictionary UUID
        dictionary_service: Dictionary service instance

    Returns:
        DictionaryDelete: Deletion confirmation

    Raises:
        HTTPException: If dictionary not found or deletion fails
    """
    try:
        dictionary_service.delete_dictionary(dictionary_id)

        logger.info(f"Deleted dictionary {dictionary_id}")

        return DictionaryDelete(
            success=True,
            message=f"Dictionary {dictionary_id} deleted successfully",
            deleted_id=dictionary_id,
        )

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary {dictionary_id} not found",
        )
    except Exception as e:
        logger.error(f"Error deleting dictionary {dictionary_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete dictionary",
        )


@router.post(
    "/import",
    summary="Import dictionaries from XLSX",
    description="Import dictionaries from an exported XLSX file to rehydrate the database.",
)
async def import_from_excel(
    file: UploadFile = File(..., description="XLSX file to import"),
    conflict_mode: str = Query(
        default="skip",
        description="How to handle conflicts: 'skip', 'overwrite', or 'fail'",
        regex="^(skip|overwrite|fail)$",
    ),
    imported_by: str | None = Form(None, description="User performing the import"),
    db: DatabaseSession = None,
) -> dict:
    """
    Import dictionaries from an XLSX export file.

    Supports both single dictionary and batch export formats.
    The file will be validated before import.

    Args:
        file: XLSX file to import
        conflict_mode: How to handle existing dictionaries
            - skip: Skip dictionaries that already exist
            - overwrite: Replace existing dictionaries
            - fail: Return error if any dictionary exists
        imported_by: Email of user performing import

    Returns:
        Import results including counts and any errors

    Raises:
        HTTPException: If file is invalid or import fails
    """
    from src.services.import_service import ImportService

    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)",
        )

    logger.info(f"Starting import from file: {file.filename}")

    # Save uploaded file to temp location
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    try:
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        # Perform import
        import_service = ImportService(db)
        results = import_service.import_from_excel(
            file_path=temp_file.name,
            conflict_mode=conflict_mode,
            imported_by=imported_by,
        )

        logger.info(
            f"Import completed: {results.get('dictionaries_imported', 0)} dictionaries imported"
        )

        return results

    except AppValidationError as e:
        logger.error(f"Validation error during import: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except FileNotFoundError as e:
        logger.error(f"File not found during import: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error during import: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}",
        )
    finally:
        # Clean up temp file
        import os
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
