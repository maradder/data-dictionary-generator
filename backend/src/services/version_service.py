"""
Version Service - Business logic for version operations.

This module provides the VersionService class for managing dictionary versions,
comparing versions, and tracking schema changes over time.
"""

import hashlib
import logging
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
from src.models.field import Field
from src.models.version import Version
from src.processors.json_parser import JSONParser
from src.processors.pii_detector import PIIDetector
from src.processors.quality_analyzer import QualityAnalyzer
from src.processors.semantic_detector import SemanticTypeDetector
from src.processors.type_inferrer import TypeInferrer

# Get logger
logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("audit")


class VersionService:
    """
    Service for version operations.

    Handles version creation, comparison, and change tracking.
    """

    def __init__(self, db: Session):
        """
        Initialize VersionService.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

        # Initialize processors
        self.json_parser = JSONParser()
        self.type_inferrer = TypeInferrer()
        self.semantic_detector = SemanticTypeDetector()
        self.pii_detector = PIIDetector()
        self.quality_analyzer = QualityAnalyzer()

        logger.info("VersionService initialized")

    def create_new_version(
        self,
        dictionary_id: UUID,
        file_path: Path,
        created_by: str | None = None,
        notes: str | None = None,
    ) -> Version:
        """
        Create a new version from a JSON file.

        Args:
            dictionary_id: Dictionary UUID
            file_path: Path to new JSON file
            created_by: User creating the version
            notes: Optional version notes

        Returns:
            New Version

        Raises:
            NotFoundError: If dictionary not found
            ValidationError: If validation fails
            ProcessingError: If JSON processing fails
            DatabaseError: If database operations fail
        """
        logger.info(
            f"Creating new version for dictionary {dictionary_id}",
            extra={"dictionary_id": str(dictionary_id), "file_path": str(file_path)},
        )

        # Validate file
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        if not file_path.suffix.lower() == ".json":
            raise ValidationError("File must be a JSON file")

        # Get latest version number
        latest_version = (
            self.db.query(Version)
            .filter(Version.dictionary_id == dictionary_id)
            .order_by(Version.version_number.desc())
            .first()
        )

        if not latest_version:
            raise NotFoundError(
                f"No versions found for dictionary {dictionary_id}",
                details={"dictionary_id": str(dictionary_id)},
            )

        new_version_number = latest_version.version_number + 1

        # Parse JSON
        logger.info("Parsing JSON file")
        try:
            parse_result = self.json_parser.parse_file(file_path)
        except Exception as e:
            logger.error(f"JSON parsing failed: {e}")
            raise ProcessingError(
                f"Failed to parse JSON file: {str(e)}",
                details={"file_path": str(file_path)},
            )

        # Calculate schema hash
        schema_hash = self._calculate_schema_hash(parse_result["fields"])

        # Check if schema actually changed
        if schema_hash == latest_version.schema_hash:
            logger.warning("Schema hash unchanged - no schema changes detected")

        # Create version
        version = Version(
            dictionary_id=dictionary_id,
            version_number=new_version_number,
            schema_hash=schema_hash,
            created_by=created_by,
            notes=notes,
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

        # Process fields
        logger.info(f"Processing {len(parse_result['fields'])} fields")
        fields_created = 0

        for position, field_meta in enumerate(parse_result["fields"]):
            try:
                self._process_field(version, field_meta, position)
                fields_created += 1
            except Exception as e:
                logger.error(
                    f"Failed to process field {field_meta['field_path']}: {e}"
                )

        # Commit transaction
        try:
            self.db.commit()
            logger.info(
                f"Version created successfully: {version.id}",
                extra={
                    "version_id": str(version.id),
                    "version_number": new_version_number,
                    "fields_created": fields_created,
                },
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to commit transaction: {e}")
            raise DatabaseError(f"Failed to save version: {str(e)}")

        # Audit log
        audit_logger.info(
            "Version created",
            extra={
                "action": "create_version",
                "dictionary_id": str(dictionary_id),
                "version_id": str(version.id),
                "version_number": new_version_number,
                "created_by": created_by,
            },
        )

        return version

    def _process_field(
        self,
        version: Version,
        field_meta: dict[str, Any],
        position: int,
    ) -> Field:
        """
        Process a single field.

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
        self.db.flush()

        return field

    def _calculate_schema_hash(self, fields: list[dict[str, Any]]) -> str:
        """
        Calculate hash of schema structure.

        Args:
            fields: List of field metadata dictionaries

        Returns:
            SHA256 hash of schema structure
        """
        field_signatures = []
        for field in sorted(fields, key=lambda x: x["field_path"]):
            types = field.get("types_seen", [])
            primary_type = types[0] if types else "unknown"
            sig = f"{field['field_path']}:{primary_type}"
            field_signatures.append(sig)

        schema_str = "|".join(field_signatures)
        return hashlib.sha256(schema_str.encode()).hexdigest()

    def compare_versions(
        self,
        dictionary_id: UUID,
        version1_number: int,
        version2_number: int,
    ) -> dict[str, Any]:
        """
        Compare two versions and identify changes.

        Implements algorithm from Section 7.2:
        1. Fetch all fields for both versions
        2. Create maps: field_path -> field_data
        3. Identify added fields (in v2, not in v1)
        4. Identify removed fields (in v1, not in v2)
        5. Identify modified fields (in both, but different)
        6. Classify breaking changes

        Args:
            dictionary_id: Dictionary UUID
            version1_number: First version number
            version2_number: Second version number

        Returns:
            Dictionary with comparison results

        Raises:
            NotFoundError: If versions not found
        """
        logger.info(
            f"Comparing versions {version1_number} and {version2_number}",
            extra={
                "dictionary_id": str(dictionary_id),
                "v1": version1_number,
                "v2": version2_number,
            },
        )

        # Get versions
        version1 = (
            self.db.query(Version)
            .filter(
                Version.dictionary_id == dictionary_id,
                Version.version_number == version1_number,
            )
            .first()
        )

        version2 = (
            self.db.query(Version)
            .filter(
                Version.dictionary_id == dictionary_id,
                Version.version_number == version2_number,
            )
            .first()
        )

        if not version1:
            raise NotFoundError(f"Version {version1_number} not found")

        if not version2:
            raise NotFoundError(f"Version {version2_number} not found")

        # Get fields for both versions
        v1_fields = self.get_version_fields(version1.id)
        v2_fields = self.get_version_fields(version2.id)

        # Create maps
        v1_map = {f.field_path: f for f in v1_fields}
        v2_map = {f.field_path: f for f in v2_fields}

        changes = []

        # Find added fields
        for path, field in v2_map.items():
            if path not in v1_map:
                changes.append(
                    {
                        "change_type": "added",
                        "field_path": path,
                        "version_2_data": self._field_to_dict(field),
                        "is_breaking": False,  # New fields are not breaking
                    }
                )

        # Find removed fields
        for path, field in v1_map.items():
            if path not in v2_map:
                changes.append(
                    {
                        "change_type": "removed",
                        "field_path": path,
                        "version_1_data": self._field_to_dict(field),
                        "is_breaking": True,  # Removed fields are breaking
                    }
                )

        # Find modified fields
        for path in set(v1_map.keys()) & set(v2_map.keys()):
            v1_field = v1_map[path]
            v2_field = v2_map[path]

            if self._fields_differ(v1_field, v2_field):
                is_breaking = self._is_breaking_change(v1_field, v2_field)
                changes.append(
                    {
                        "change_type": "modified",
                        "field_path": path,
                        "version_1_data": self._field_to_dict(v1_field),
                        "version_2_data": self._field_to_dict(v2_field),
                        "is_breaking": is_breaking,
                        "changes": self._get_field_changes(v1_field, v2_field),
                    }
                )

        # Summary
        summary = {
            "fields_added": sum(1 for c in changes if c["change_type"] == "added"),
            "fields_removed": sum(1 for c in changes if c["change_type"] == "removed"),
            "fields_modified": sum(
                1 for c in changes if c["change_type"] == "modified"
            ),
            "breaking_changes": sum(1 for c in changes if c.get("is_breaking", False)),
            "total_fields_v1": len(v1_fields),
            "total_fields_v2": len(v2_fields),
        }

        return {
            "summary": summary,
            "changes": changes,
            "version_1": {
                "id": str(version1.id),
                "version_number": version1.version_number,
                "created_at": version1.created_at.isoformat(),
                "schema_hash": version1.schema_hash,
            },
            "version_2": {
                "id": str(version2.id),
                "version_number": version2.version_number,
                "created_at": version2.created_at.isoformat(),
                "schema_hash": version2.schema_hash,
            },
        }

    def _is_breaking_change(self, v1_field: Field, v2_field: Field) -> bool:
        """
        Determine if change is breaking.

        Breaking changes:
        - Type changes
        - Nullable to non-nullable
        - Field removal (handled elsewhere)

        Args:
            v1_field: Field from version 1
            v2_field: Field from version 2

        Returns:
            True if breaking change
        """
        # Type changes are breaking
        if v1_field.data_type != v2_field.data_type:
            return True

        # Nullability changes (nullable -> non-nullable is breaking)
        if v1_field.is_nullable and not v2_field.is_nullable:
            return True

        # Array type changes
        if v1_field.is_array != v2_field.is_array:
            return True

        return False

    def _fields_differ(self, v1_field: Field, v2_field: Field) -> bool:
        """
        Check if two fields have meaningful differences.

        Args:
            v1_field: Field from version 1
            v2_field: Field from version 2

        Returns:
            True if fields differ
        """
        # Compare key attributes
        return (
            v1_field.data_type != v2_field.data_type
            or v1_field.semantic_type != v2_field.semantic_type
            or v1_field.is_nullable != v2_field.is_nullable
            or v1_field.is_array != v2_field.is_array
            or v1_field.is_pii != v2_field.is_pii
        )

    def _get_field_changes(self, v1_field: Field, v2_field: Field) -> list[str]:
        """
        Get list of specific changes between fields.

        Args:
            v1_field: Field from version 1
            v2_field: Field from version 2

        Returns:
            List of change descriptions
        """
        changes = []

        if v1_field.data_type != v2_field.data_type:
            changes.append(f"Type changed: {v1_field.data_type} -> {v2_field.data_type}")

        if v1_field.semantic_type != v2_field.semantic_type:
            changes.append(
                f"Semantic type changed: {v1_field.semantic_type} -> {v2_field.semantic_type}"
            )

        if v1_field.is_nullable != v2_field.is_nullable:
            changes.append(
                f"Nullability changed: {v1_field.is_nullable} -> {v2_field.is_nullable}"
            )

        if v1_field.is_array != v2_field.is_array:
            changes.append(f"Array status changed: {v1_field.is_array} -> {v2_field.is_array}")

        if v1_field.is_pii != v2_field.is_pii:
            changes.append(f"PII status changed: {v1_field.is_pii} -> {v2_field.is_pii}")

        return changes

    def _field_to_dict(self, field: Field) -> dict[str, Any]:
        """
        Convert field to dictionary.

        Args:
            field: Field object

        Returns:
            Dictionary representation
        """
        return {
            "field_path": field.field_path,
            "field_name": field.field_name,
            "data_type": field.data_type,
            "semantic_type": field.semantic_type,
            "is_nullable": field.is_nullable,
            "is_array": field.is_array,
            "array_item_type": field.array_item_type,
            "is_pii": field.is_pii,
            "pii_type": field.pii_type,
            "null_percentage": float(field.null_percentage) if field.null_percentage else 0.0,
            "confidence_score": float(field.confidence_score) if field.confidence_score else 0.0,
        }

    def get_version_fields(self, version_id: UUID) -> list[Field]:
        """
        Get all fields for a version.

        Args:
            version_id: Version UUID

        Returns:
            List of fields
        """
        return (
            self.db.query(Field)
            .filter(Field.version_id == version_id)
            .order_by(Field.position)
            .all()
        )

    def get_version(self, version_id: UUID) -> Version:
        """
        Get version by ID.

        Args:
            version_id: Version UUID

        Returns:
            Version

        Raises:
            NotFoundError: If version not found
        """
        version = self.db.query(Version).filter(Version.id == version_id).first()

        if not version:
            raise NotFoundError(
                f"Version not found: {version_id}",
                details={"version_id": str(version_id)},
            )

        return version

    def list_versions(
        self,
        dictionary_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Version]:
        """
        List versions for a dictionary.

        Args:
            dictionary_id: Dictionary UUID
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of versions
        """
        return (
            self.db.query(Version)
            .filter(Version.dictionary_id == dictionary_id)
            .order_by(Version.version_number.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_version_fields_paginated(
        self,
        version_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Field], int]:
        """
        Get fields for a version with pagination.

        Args:
            version_id: Version UUID
            limit: Maximum number of results (default 100)
            offset: Number of results to skip (default 0)

        Returns:
            Tuple of (fields list, total count)

        Raises:
            NotFoundError: If version not found
        """
        # Verify version exists
        version = self.get_version(version_id)
        if not version:
            raise NotFoundError(
                f"Version not found: {version_id}",
                details={"version_id": str(version_id)},
            )

        # Get total count
        total_count = (
            self.db.query(Field)
            .filter(Field.version_id == version_id)
            .count()
        )

        # Get paginated fields with eager loading of annotations
        from sqlalchemy.orm import joinedload

        fields = (
            self.db.query(Field)
            .options(joinedload(Field.annotations))
            .filter(Field.version_id == version_id)
            .order_by(Field.position, Field.field_path)
            .limit(limit)
            .offset(offset)
            .all()
        )

        return fields, total_count
