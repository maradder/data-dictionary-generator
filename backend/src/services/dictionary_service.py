"""
Dictionary Service - Business logic for dictionary operations.

This module provides the DictionaryService class that orchestrates the complete
workflow for creating, managing, and analyzing data dictionaries.
"""

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from src.core.exceptions import (
    DatabaseError,
    NotFoundError,
    ProcessingError,
    ValidationError,
)
from src.models.annotation import Annotation
from src.models.dictionary import Dictionary
from src.models.field import Field
from src.models.version import Version
from src.processors.ai_generator import AIDescriptionGenerator
from src.processors.geopackage_parser import GeoPackageParser
from src.processors.json_parser import JSONParser
from src.processors.mongodb_parser import MongoDBParser
from src.processors.pii_detector import PIIDetector
from src.processors.protobuf_parser import ProtobufParser
from src.processors.quality_analyzer import QualityAnalyzer
from src.processors.semantic_detector import SemanticTypeDetector
from src.processors.sqlite_parser import SQLiteParser
from src.processors.type_inferrer import TypeInferrer
from src.processors.xml_parser import XMLParser

# Get logger
logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("audit")


class DictionaryService:
    """
    Service for dictionary operations.

    Orchestrates the complete workflow for dictionary creation including:
    - JSON parsing
    - Type inference
    - Semantic detection
    - PII detection
    - Quality analysis
    - AI description generation
    - Database persistence
    """

    def __init__(
        self,
        db: Session,
    ):
        """
        Initialize DictionaryService.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

        # Initialize processors
        self.json_parser = JSONParser()
        self.type_inferrer = TypeInferrer()
        self.ai_generator = AIDescriptionGenerator()
        # Pass AI generator to semantic detector for enhanced detection
        self.semantic_detector = SemanticTypeDetector(ai_generator=self.ai_generator, use_ai=False)
        self.pii_detector = PIIDetector()
        self.quality_analyzer = QualityAnalyzer()

        logger.info("DictionaryService initialized")

    def create_dictionary(
        self,
        file_path: Path,
        name: str,
        description: str | None = None,
        created_by: str | None = None,
        generate_ai_descriptions: bool = False,
        metadata: dict[str, Any] | None = None,
        original_filename: str | None = None,
    ) -> Dictionary:
        """
        Create dictionary from JSON, XML, SQLite, or GeoPackage file.

        Implements the complete workflow from Section 7.1:
        1. Parse JSON/XML/SQLite/GeoPackage file
        2. Create dictionary record
        3. Create version (v1)
        4. Process each field (type inference, semantic detection, PII detection, quality analysis)
        5. Generate AI descriptions (if enabled)
        6. Save to database with transaction

        Args:
            file_path: Path to JSON, XML, SQLite, or GeoPackage file
            name: Dictionary name
            description: Optional description
            created_by: User who created the dictionary
            generate_ai_descriptions: Whether to generate AI descriptions
            metadata: Additional metadata
            original_filename: Original uploaded filename (if different from file_path.name)

        Returns:
            Dictionary: Created dictionary with version and fields

        Raises:
            ValidationError: If input validation fails
            ProcessingError: If JSON/XML/SQLite/GeoPackage processing fails
            DatabaseError: If database operations fail
        """
        logger.info(
            f"Creating dictionary from file: {file_path}",
            extra={"file_path": str(file_path), "dictionary_name": name},
        )

        try:
            # Validate file
            if not file_path.exists():
                raise ValidationError(f"File not found: {file_path}")

            file_suffix = file_path.suffix.lower()
            if file_suffix not in [".json", ".xml", ".db", ".sqlite", ".sqlite3", ".gpkg", ".proto", ".desc"]:
                raise ValidationError("File must be a JSON, XML, SQLite, GeoPackage, or Protocol Buffer file")

            # Step 1: Parse file based on format
            try:
                if file_suffix == ".xml":
                    logger.info("Parsing XML file")
                    xml_parser = XMLParser()
                    parse_result = xml_parser.parse_file(file_path)
                elif file_suffix == ".gpkg":
                    logger.info("Parsing GeoPackage file")
                    geopackage_parser = GeoPackageParser()
                    parse_result = geopackage_parser.parse_file(file_path)
                elif file_suffix in [".db", ".sqlite", ".sqlite3"]:
                    logger.info("Parsing SQLite database file")
                    sqlite_parser = SQLiteParser()
                    parse_result = sqlite_parser.parse_file(file_path)
                elif file_suffix in [".proto", ".desc"]:
                    logger.info(f"Parsing Protocol Buffer {file_suffix} file")
                    protobuf_parser = ProtobufParser(str(file_path))
                    parse_result = protobuf_parser.parse_file(file_path)
                else:
                    # JSON file - detect MongoDB Extended JSON format
                    logger.info("Parsing JSON file")
                    is_mongodb_format = self._detect_mongodb_format(file_path)

                    # Use appropriate parser
                    if is_mongodb_format:
                        logger.info("Using MongoDB Extended JSON parser")
                        mongodb_parser = MongoDBParser()
                        parse_result = mongodb_parser.parse_file(file_path)
                    else:
                        parse_result = self.json_parser.parse_file(file_path)
            except Exception as e:
                logger.error(f"File parsing failed: {e}")
                raise ProcessingError(
                    f"Failed to parse file: {str(e)}",
                    details={"file_path": str(file_path)},
                )

            # Step 2: Create dictionary record
            logger.info("Creating dictionary record")
            dictionary = Dictionary(
                name=name,
                description=description,
                source_file_name=original_filename or file_path.name,
                source_file_size=file_path.stat().st_size,
                total_records_analyzed=parse_result["total_records"],
                created_by=created_by,
                metadata=metadata,
            )

            try:
                self.db.add(dictionary)
                self.db.flush()  # Get ID without committing
            except Exception as e:
                logger.error(f"Failed to create dictionary record: {e}")
                raise DatabaseError(f"Failed to create dictionary: {str(e)}")

            # Step 3: Create version
            logger.info("Creating version record")
            schema_hash = self._calculate_schema_hash(parse_result["fields"])
            version = Version(
                dictionary_id=dictionary.id,
                version_number=1,
                schema_hash=schema_hash,
                created_by=created_by,
                processing_stats={
                    "total_fields": len(parse_result["fields"]),
                    "total_records": parse_result["total_records"],
                    "is_array_root": parse_result["is_array"],
                },
            )

            try:
                self.db.add(version)
                self.db.flush()
            except Exception as e:
                logger.error(f"Failed to create version record: {e}")
                raise DatabaseError(f"Failed to create version: {str(e)}")

            # Step 4: Process fields
            logger.info(f"Processing {len(parse_result['fields'])} fields")
            fields_created = 0

            # Enable AI-enhanced semantic detection if AI descriptions are enabled
            self.semantic_detector.use_ai = generate_ai_descriptions

            for position, field_meta in enumerate(parse_result["fields"]):
                try:
                    field = self._process_field(
                        version=version,
                        field_meta=field_meta,
                        position=position,
                    )

                    # Step 5: Generate AI description (if enabled)
                    if generate_ai_descriptions:
                        self._generate_ai_annotation(field, field_meta)

                    fields_created += 1

                except Exception as e:
                    logger.error(
                        f"Failed to process field {field_meta['field_path']}: {e}",
                        extra={"field_path": field_meta["field_path"]},
                    )
                    # Continue processing other fields

            # Commit transaction
            try:
                self.db.commit()
                logger.info(
                    f"Dictionary created successfully: {dictionary.id}",
                    extra={
                        "dictionary_id": str(dictionary.id),
                        "fields_created": fields_created,
                    },
                )
            except Exception as e:
                self.db.rollback()
                logger.error(f"Failed to commit transaction: {e}")
                raise DatabaseError(f"Failed to save dictionary: {str(e)}")

            # Audit log
            audit_logger.info(
                "Dictionary created",
                extra={
                    "action": "create_dictionary",
                    "dictionary_id": str(dictionary.id),
                    "dictionary_name": name,
                    "created_by": created_by,
                    "total_fields": fields_created,
                },
            )

            return dictionary

        except (ValidationError, ProcessingError, DatabaseError):
            # Re-raise known exceptions
            self.db.rollback()
            raise
        except Exception as e:
            # Catch unexpected errors
            self.db.rollback()
            logger.error(f"Unexpected error creating dictionary: {e}", exc_info=True)
            raise ProcessingError(f"Unexpected error: {str(e)}")

    def _process_field(
        self,
        version: Version,
        field_meta: dict[str, Any],
        position: int,
    ) -> Field:
        """
        Process a single field through all analysis steps.

        Args:
            version: Version to attach field to
            field_meta: Field metadata from parser
            position: Position in field list

        Returns:
            Field: Created field record
        """
        # Infer type
        data_type, confidence = self.type_inferrer.infer_type(
            field_meta["types_seen"]
        )

        # Detect semantic type
        semantic_type = self.semantic_detector.detect(
            field_meta["field_name"],
            field_meta["sample_values"],
            data_type,
        )

        # Detect PII
        is_pii, pii_type = self.pii_detector.detect_pii(
            field_meta["field_path"],
            field_meta["field_name"],
            semantic_type,
            field_meta["sample_values"],
        )

        # Calculate quality metrics
        quality_metrics = self.quality_analyzer.analyze_field(
            field_meta["sample_values"],
            data_type,
        )

        # Determine nullability
        null_percentage = field_meta.get("null_percentage", 0)
        is_nullable = null_percentage > 0

        # Handle array types
        is_array = field_meta.get("is_array", False)
        array_item_type = None
        if is_array and field_meta.get("array_item_types"):
            array_item_type = self.type_inferrer.infer_array_item_type(
                list(field_meta["array_item_types"])
            )

        # Create field record
        field = Field(
            version_id=version.id,
            field_path=field_meta["field_path"],
            field_name=field_meta["field_name"],
            parent_path=field_meta["parent_path"] or None,
            nesting_level=field_meta["nesting_level"],
            data_type=data_type,
            semantic_type=semantic_type,
            is_nullable=is_nullable,
            is_array=is_array,
            array_item_type=array_item_type,
            sample_values={"values": field_meta["sample_values"]},
            null_count=field_meta.get("null_count", 0),
            null_percentage=null_percentage,
            total_count=quality_metrics.get("total_count", field_meta.get("total_count", 0)),
            distinct_count=quality_metrics.get("distinct_count", 0),
            cardinality_ratio=quality_metrics.get("cardinality_ratio"),
            min_value=quality_metrics.get("min_value"),
            max_value=quality_metrics.get("max_value"),
            mean_value=quality_metrics.get("mean_value"),
            median_value=quality_metrics.get("median_value"),
            std_dev=quality_metrics.get("std_dev"),
            percentile_25=quality_metrics.get("percentile_25"),
            percentile_50=quality_metrics.get("percentile_50"),
            percentile_75=quality_metrics.get("percentile_75"),
            is_pii=is_pii,
            pii_type=pii_type,
            confidence_score=confidence,
            position=position,
        )

        self.db.add(field)
        self.db.flush()  # Get field ID

        return field

    def _generate_ai_annotation(
        self,
        field: Field,
        field_meta: dict[str, Any],
    ) -> Annotation | None:
        """
        Generate AI annotation for a field.

        Args:
            field: Field to annotate
            field_meta: Field metadata

        Returns:
            Annotation if successful, None otherwise
        """
        try:
            description, business_name = self.ai_generator.generate_description(
                field_meta["field_path"],
                field_meta["field_name"],
                field.data_type,
                field.semantic_type,
                field_meta["sample_values"],
            )

            annotation = Annotation(
                field_id=field.id,
                description=description,
                business_name=business_name,
                is_ai_generated=True,
                ai_model_version=self.ai_generator.model,
                created_at=datetime.now(timezone.utc),
            )

            self.db.add(annotation)
            self.db.flush()

            logger.debug(
                f"AI annotation created for field: {field.field_path}",
                extra={"field_id": str(field.id)},
            )

            return annotation

        except Exception as e:
            logger.warning(
                f"Failed to generate AI annotation for {field.field_path}: {e}",
                extra={"field_id": str(field.id)},
            )
            return None

    def _calculate_schema_hash(self, fields: list[dict[str, Any]]) -> str:
        """
        Calculate hash of schema structure for version detection.

        Args:
            fields: List of field metadata dictionaries

        Returns:
            SHA256 hash of schema structure
        """
        # Create deterministic representation
        field_signatures = []
        for field in sorted(fields, key=lambda x: x["field_path"]):
            # Include path and primary type in signature
            types = field.get("types_seen", [])
            primary_type = types[0] if types else "unknown"
            sig = f"{field['field_path']}:{primary_type}"
            field_signatures.append(sig)

        schema_str = "|".join(field_signatures)
        return hashlib.sha256(schema_str.encode()).hexdigest()

    def _detect_mongodb_format(self, file_path: Path) -> bool:
        """
        Detect if file contains MongoDB Extended JSON format.

        Checks first 8KB of file for MongoDB type markers like $oid, $date, etc.

        Args:
            file_path: Path to JSON file

        Returns:
            True if MongoDB markers are detected, False otherwise
        """
        mongodb_markers = {b'"$oid"', b'"$date"', b'"$numberLong"', b'"$numberDecimal"', b'"$binary"'}

        try:
            with open(file_path, 'rb') as f:
                # Read first 8KB
                sample = f.read(8192)

                # Check for any MongoDB markers
                for marker in mongodb_markers:
                    if marker in sample:
                        logger.info(f"MongoDB Extended JSON format detected in {file_path.name}")
                        return True

                return False

        except Exception as e:
            logger.warning(f"Error detecting MongoDB format: {e}")
            return False

    def get_dictionary(self, dictionary_id: UUID) -> Dictionary:
        """
        Get dictionary by ID.

        Args:
            dictionary_id: Dictionary UUID

        Returns:
            Dictionary

        Raises:
            NotFoundError: If dictionary not found
        """
        logger.debug(f"Getting dictionary: {dictionary_id}")

        dictionary = (
            self.db.query(Dictionary)
            .filter(Dictionary.id == str(dictionary_id))
            .first()
        )

        if not dictionary:
            raise NotFoundError(
                f"Dictionary not found: {dictionary_id}",
                details={"dictionary_id": str(dictionary_id)},
            )

        return dictionary

    def list_dictionaries(
        self,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "created_at",
        order: str = "desc",
    ) -> tuple[list[Dictionary], int]:
        """
        List dictionaries with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            sort_by: Field to sort by
            order: Sort order ('asc' or 'desc')

        Returns:
            Tuple of (list of dictionaries, total count)
        """
        logger.debug(
            f"Listing dictionaries: limit={limit}, offset={offset}, sort_by={sort_by}"
        )

        from sqlalchemy.orm import selectinload

        # Build query with eager loading to prevent N+1 queries
        query = self.db.query(Dictionary).options(
            selectinload(Dictionary.versions).selectinload(Version.fields)
        )

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        if hasattr(Dictionary, sort_by):
            sort_column = getattr(Dictionary, sort_by)
            if order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        else:
            # Default sort
            query = query.order_by(Dictionary.created_at.desc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        return query.all(), total

    def update_dictionary(
        self,
        dictionary_id: UUID,
        name: str | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
        updated_by: str | None = None,
    ) -> Dictionary:
        """
        Update dictionary metadata.

        Args:
            dictionary_id: Dictionary UUID
            name: New name (optional)
            description: New description (optional)
            metadata: New metadata (optional)
            updated_by: User updating the dictionary

        Returns:
            Updated dictionary

        Raises:
            NotFoundError: If dictionary not found
            DatabaseError: If update fails
        """
        logger.info(f"Updating dictionary: {dictionary_id}")

        dictionary = self.get_dictionary(dictionary_id)

        # Update fields
        if name is not None:
            dictionary.name = name
        if description is not None:
            dictionary.description = description
        if metadata is not None:
            dictionary.custom_metadata = metadata

        dictionary.updated_at = datetime.now(timezone.utc)

        try:
            self.db.commit()
            logger.info(f"Dictionary updated: {dictionary_id}")

            # Audit log
            audit_logger.info(
                "Dictionary updated",
                extra={
                    "action": "update_dictionary",
                    "dictionary_id": str(dictionary_id),
                    "updated_by": updated_by,
                },
            )

            return dictionary

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update dictionary: {e}")
            raise DatabaseError(f"Failed to update dictionary: {str(e)}")

    def delete_dictionary(
        self,
        dictionary_id: UUID,
        deleted_by: str | None = None,
    ) -> None:
        """
        Delete dictionary and all related data.

        Args:
            dictionary_id: Dictionary UUID
            deleted_by: User deleting the dictionary

        Raises:
            NotFoundError: If dictionary not found
            DatabaseError: If deletion fails
        """
        logger.info(f"Deleting dictionary: {dictionary_id}")

        dictionary = self.get_dictionary(dictionary_id)

        try:
            # Cascade delete will handle versions, fields, and annotations
            self.db.delete(dictionary)
            self.db.commit()

            logger.info(f"Dictionary deleted: {dictionary_id}")

            # Audit log
            audit_logger.info(
                "Dictionary deleted",
                extra={
                    "action": "delete_dictionary",
                    "dictionary_id": str(dictionary_id),
                    "dictionary_name": dictionary.name,
                    "deleted_by": deleted_by,
                },
            )

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete dictionary: {e}")
            raise DatabaseError(f"Failed to delete dictionary: {str(e)}")

    def get_dictionary_stats(self, dictionary_id: UUID) -> dict[str, Any]:
        """
        Get statistics for a dictionary.

        Args:
            dictionary_id: Dictionary UUID

        Returns:
            Dictionary with statistics

        Raises:
            NotFoundError: If dictionary not found
        """
        logger.debug(f"Getting stats for dictionary: {dictionary_id}")

        dictionary = self.get_dictionary(dictionary_id)

        # Get version count
        version_count = (
            self.db.query(Version)
            .filter(Version.dictionary_id == str(dictionary_id))
            .count()
        )

        # Get latest version
        latest_version = (
            self.db.query(Version)
            .filter(Version.dictionary_id == str(dictionary_id))
            .order_by(Version.version_number.desc())
            .first()
        )

        # Get field count for latest version
        field_count = 0
        pii_field_count = 0
        if latest_version:
            field_count = (
                self.db.query(Field)
                .filter(Field.version_id == str(latest_version.id))
                .count()
            )
            pii_field_count = (
                self.db.query(Field)
                .filter(Field.version_id == str(latest_version.id), Field.is_pii)
                .count()
            )

        return {
            "dictionary_id": str(dictionary_id),
            "name": dictionary.name,
            "total_versions": version_count,
            "latest_version_number": latest_version.version_number if latest_version else 0,
            "total_fields": field_count,
            "pii_fields": pii_field_count,
            "total_records_analyzed": dictionary.total_records_analyzed,
            "source_file_size": dictionary.source_file_size,
            "created_at": dictionary.created_at.isoformat(),
            "updated_at": dictionary.updated_at.isoformat(),
        }
