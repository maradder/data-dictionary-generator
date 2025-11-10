"""
Analysis Service - Business logic for analyzing and regenerating data.

This module provides the AnalysisService class for analyzing JSON files,
regenerating AI descriptions, and recalculating quality metrics.
"""

import logging
from datetime import datetime
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
from src.models.field import Field
from src.models.version import Version
from src.processors.ai_generator import AIDescriptionGenerator
from src.processors.json_parser import JSONParser
from src.processors.pii_detector import PIIDetector
from src.processors.quality_analyzer import QualityAnalyzer
from src.processors.semantic_detector import SemanticTypeDetector
from src.processors.type_inferrer import TypeInferrer

# Get logger
logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("audit")


class AnalysisService:
    """
    Service for analysis and regeneration operations.

    Handles analysis of JSON files without saving, regeneration of AI descriptions,
    and recalculation of quality metrics.
    """

    def __init__(self, db: Session):
        """
        Initialize AnalysisService.

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

        logger.info("AnalysisService initialized")

    def analyze_json_file(
        self,
        file_path: Path,
        analyzed_by: str | None = None,
    ) -> dict[str, Any]:
        """
        Analyze JSON file and return statistics without saving to database.

        This method provides a preview of what would be created if the file
        were imported as a dictionary. Useful for validation and preview.

        Args:
            file_path: Path to JSON file
            analyzed_by: User performing the analysis

        Returns:
            Dictionary with analysis results:
            {
                'file_info': {...},
                'schema_summary': {...},
                'fields': [...],
                'quality_summary': {...},
                'pii_summary': {...}
            }

        Raises:
            ValidationError: If file validation fails
            ProcessingError: If JSON processing fails
        """
        logger.info(
            f"Analyzing JSON file: {file_path}",
            extra={"file_path": str(file_path), "analyzed_by": analyzed_by},
        )

        # Validate file
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        if not file_path.suffix.lower() == ".json":
            raise ValidationError("File must be a JSON file")

        # Parse JSON
        try:
            parse_result = self.json_parser.parse_file(file_path)
        except Exception as e:
            logger.error(f"JSON parsing failed: {e}")
            raise ProcessingError(
                f"Failed to parse JSON file: {str(e)}",
                details={"file_path": str(file_path)},
            )

        # Analyze fields
        analyzed_fields = []
        type_distribution = {}
        semantic_type_distribution = {}
        pii_count = 0
        total_null_percentage = 0.0

        for field_meta in parse_result["fields"]:
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

            # Track statistics
            type_distribution[data_type] = type_distribution.get(data_type, 0) + 1

            if semantic_type:
                semantic_type_distribution[semantic_type] = (
                    semantic_type_distribution.get(semantic_type, 0) + 1
                )

            if is_pii:
                pii_count += 1

            null_pct = field_meta.get("null_percentage", 0)
            total_null_percentage += null_pct

            # Build field analysis
            field_analysis = {
                "field_path": field_meta["field_path"],
                "field_name": field_meta["field_name"],
                "parent_path": field_meta["parent_path"],
                "nesting_level": field_meta["nesting_level"],
                "data_type": data_type,
                "type_confidence": confidence,
                "semantic_type": semantic_type,
                "is_pii": is_pii,
                "pii_type": pii_type,
                "is_array": field_meta.get("is_array", False),
                "null_percentage": null_pct,
                "sample_values": field_meta["sample_values"][:5],  # First 5 samples
                "distinct_count": quality_metrics.get("distinct_count", 0),
                "cardinality_ratio": quality_metrics.get("cardinality_ratio", 0),
            }

            # Add numeric statistics if available
            if data_type in ("integer", "float"):
                field_analysis.update(
                    {
                        "min_value": quality_metrics.get("min_value"),
                        "max_value": quality_metrics.get("max_value"),
                        "mean_value": quality_metrics.get("mean_value"),
                        "median_value": quality_metrics.get("median_value"),
                    }
                )

            analyzed_fields.append(field_analysis)

        # Calculate averages
        num_fields = len(parse_result["fields"])
        avg_null_percentage = total_null_percentage / num_fields if num_fields > 0 else 0

        # Build summary
        result = {
            "file_info": {
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "file_path": str(file_path),
            },
            "schema_summary": {
                "total_fields": num_fields,
                "total_records": parse_result["total_records"],
                "is_array_root": parse_result["is_array"],
                "max_nesting_level": max(
                    (f["nesting_level"] for f in parse_result["fields"]), default=0
                ),
                "type_distribution": type_distribution,
                "semantic_type_distribution": semantic_type_distribution,
            },
            "quality_summary": {
                "average_null_percentage": round(avg_null_percentage, 2),
                "fields_with_nulls": sum(
                    1 for f in parse_result["fields"] if f.get("null_percentage", 0) > 0
                ),
            },
            "pii_summary": {
                "total_pii_fields": pii_count,
                "pii_percentage": round((pii_count / num_fields * 100), 2)
                if num_fields > 0
                else 0,
            },
            "fields": analyzed_fields,
        }

        logger.info(
            f"Analysis completed: {num_fields} fields, {pii_count} PII fields",
            extra={
                "file_path": str(file_path),
                "num_fields": num_fields,
                "pii_fields": pii_count,
            },
        )

        # Audit log
        audit_logger.info(
            "JSON file analyzed",
            extra={
                "action": "analyze_json_file",
                "file_path": str(file_path),
                "analyzed_by": analyzed_by,
                "num_fields": num_fields,
            },
        )

        return result

    def regenerate_ai_descriptions(
        self,
        dictionary_id: UUID,
        version_id: UUID | None = None,
        regenerated_by: str | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """
        Regenerate AI descriptions for all fields in a version.

        Args:
            dictionary_id: Dictionary UUID
            version_id: Optional version ID (defaults to latest)
            regenerated_by: User performing the regeneration
            force: If True, regenerate even if annotations exist

        Returns:
            Dictionary with regeneration results

        Raises:
            NotFoundError: If dictionary or version not found
            ProcessingError: If regeneration fails
        """
        logger.info(
            f"Regenerating AI descriptions for dictionary {dictionary_id}",
            extra={
                "dictionary_id": str(dictionary_id),
                "version_id": str(version_id) if version_id else "latest",
                "force": force,
            },
        )

        # Get version
        if version_id:
            version = (
                self.db.query(Version)
                .filter(Version.id == version_id, Version.dictionary_id == dictionary_id)
                .first()
            )
        else:
            version = (
                self.db.query(Version)
                .filter(Version.dictionary_id == dictionary_id)
                .order_by(Version.version_number.desc())
                .first()
            )

        if not version:
            raise NotFoundError(
                "Version not found",
                details={
                    "dictionary_id": str(dictionary_id),
                    "version_id": str(version_id) if version_id else None,
                },
            )

        # Get fields
        fields = (
            self.db.query(Field)
            .filter(Field.version_id == version.id)
            .order_by(Field.position)
            .all()
        )

        if not fields:
            logger.warning(f"No fields found for version {version.id}")
            return {
                "version_id": str(version.id),
                "total_fields": 0,
                "regenerated": 0,
                "skipped": 0,
                "failed": 0,
            }

        regenerated = 0
        skipped = 0
        failed = 0

        for field in fields:
            # Check if annotation exists
            existing_annotation = (
                self.db.query(Annotation)
                .filter(Annotation.field_id == field.id)
                .order_by(Annotation.created_at.desc())
                .first()
            )

            # Skip if annotation exists and not forcing
            if existing_annotation and not force:
                skipped += 1
                continue

            try:
                # Generate description
                description, business_name = self.ai_generator.generate_description(
                    field.field_path,
                    field.field_name,
                    field.data_type,
                    field.semantic_type,
                    field.sample_values.get("values", []) if field.sample_values else [],
                )

                if existing_annotation:
                    # Update existing
                    existing_annotation.description = description
                    existing_annotation.business_name = business_name
                    existing_annotation.is_ai_generated = True
                    existing_annotation.ai_model_version = self.ai_generator.model
                    existing_annotation.updated_at = datetime.utcnow()
                    existing_annotation.updated_by = regenerated_by
                else:
                    # Create new
                    annotation = Annotation(
                        field_id=field.id,
                        description=description,
                        business_name=business_name,
                        is_ai_generated=True,
                        ai_model_version=self.ai_generator.model,
                        created_by=regenerated_by,
                    )
                    self.db.add(annotation)

                regenerated += 1

            except Exception as e:
                logger.error(
                    f"Failed to generate AI description for field {field.field_path}: {e}",
                    extra={"field_id": str(field.id)},
                )
                failed += 1

        # Commit changes
        try:
            self.db.commit()
            logger.info(
                f"AI descriptions regenerated: {regenerated} fields",
                extra={
                    "version_id": str(version.id),
                    "regenerated": regenerated,
                    "skipped": skipped,
                    "failed": failed,
                },
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save AI descriptions: {e}")
            raise DatabaseError(f"Failed to save AI descriptions: {str(e)}")

        # Audit log
        audit_logger.info(
            "AI descriptions regenerated",
            extra={
                "action": "regenerate_ai_descriptions",
                "dictionary_id": str(dictionary_id),
                "version_id": str(version.id),
                "regenerated_by": regenerated_by,
                "regenerated": regenerated,
                "skipped": skipped,
                "failed": failed,
            },
        )

        return {
            "version_id": str(version.id),
            "version_number": version.version_number,
            "total_fields": len(fields),
            "regenerated": regenerated,
            "skipped": skipped,
            "failed": failed,
        }

    def recalculate_quality_metrics(
        self,
        version_id: UUID,
        recalculated_by: str | None = None,
    ) -> dict[str, Any]:
        """
        Recalculate quality metrics for all fields in a version.

        This is useful when the quality analyzer has been updated or when
        full dataset analysis was not performed initially.

        Args:
            version_id: Version UUID
            recalculated_by: User performing the recalculation

        Returns:
            Dictionary with recalculation results

        Raises:
            NotFoundError: If version not found
            ProcessingError: If recalculation fails
        """
        logger.info(
            f"Recalculating quality metrics for version {version_id}",
            extra={"version_id": str(version_id)},
        )

        # Get version
        version = self.db.query(Version).filter(Version.id == version_id).first()

        if not version:
            raise NotFoundError(
                f"Version not found: {version_id}",
                details={"version_id": str(version_id)},
            )

        # Get fields
        fields = (
            self.db.query(Field)
            .filter(Field.version_id == version.id)
            .order_by(Field.position)
            .all()
        )

        if not fields:
            logger.warning(f"No fields found for version {version.id}")
            return {
                "version_id": str(version.id),
                "total_fields": 0,
                "updated": 0,
                "failed": 0,
            }

        updated = 0
        failed = 0

        for field in fields:
            try:
                # Extract sample values
                sample_values = (
                    field.sample_values.get("values", []) if field.sample_values else []
                )

                # Recalculate metrics
                quality_metrics = self.quality_analyzer.analyze_field(
                    sample_values,
                    field.data_type,
                )

                # Update field
                field.total_count = quality_metrics.get("total_count", field.total_count)
                field.null_count = quality_metrics.get("null_count", field.null_count)
                field.null_percentage = quality_metrics.get(
                    "null_percentage", field.null_percentage
                )
                field.distinct_count = quality_metrics.get(
                    "distinct_count", field.distinct_count
                )
                field.cardinality_ratio = quality_metrics.get(
                    "cardinality_ratio", field.cardinality_ratio
                )

                # Update numeric metrics if available
                if field.data_type in ("integer", "float"):
                    field.min_value = quality_metrics.get("min_value")
                    field.max_value = quality_metrics.get("max_value")
                    field.mean_value = quality_metrics.get("mean_value")
                    field.median_value = quality_metrics.get("median_value")
                    field.std_dev = quality_metrics.get("std_dev")
                    field.percentile_25 = quality_metrics.get("percentile_25")
                    field.percentile_50 = quality_metrics.get("percentile_50")
                    field.percentile_75 = quality_metrics.get("percentile_75")

                updated += 1

            except Exception as e:
                logger.error(
                    f"Failed to recalculate metrics for field {field.field_path}: {e}",
                    extra={"field_id": str(field.id)},
                )
                failed += 1

        # Commit changes
        try:
            self.db.commit()
            logger.info(
                f"Quality metrics recalculated: {updated} fields",
                extra={
                    "version_id": str(version.id),
                    "updated": updated,
                    "failed": failed,
                },
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save quality metrics: {e}")
            raise DatabaseError(f"Failed to save quality metrics: {str(e)}")

        # Audit log
        audit_logger.info(
            "Quality metrics recalculated",
            extra={
                "action": "recalculate_quality_metrics",
                "version_id": str(version.id),
                "recalculated_by": recalculated_by,
                "updated": updated,
                "failed": failed,
            },
        )

        return {
            "version_id": str(version.id),
            "version_number": version.version_number,
            "total_fields": len(fields),
            "updated": updated,
            "failed": failed,
        }

    def get_field_statistics(
        self,
        version_id: UUID,
    ) -> dict[str, Any]:
        """
        Get statistical summary for a version.

        Args:
            version_id: Version UUID

        Returns:
            Dictionary with statistics

        Raises:
            NotFoundError: If version not found
        """
        logger.debug(f"Getting field statistics for version {version_id}")

        # Get version
        version = self.db.query(Version).filter(Version.id == version_id).first()

        if not version:
            raise NotFoundError(
                f"Version not found: {version_id}",
                details={"version_id": str(version_id)},
            )

        # Get fields
        fields = self.db.query(Field).filter(Field.version_id == version.id).all()

        if not fields:
            return {
                "version_id": str(version.id),
                "total_fields": 0,
            }

        # Calculate statistics
        type_distribution = {}
        semantic_type_distribution = {}
        pii_count = 0
        nullable_count = 0
        array_count = 0
        total_null_percentage = 0.0

        for field in fields:
            type_distribution[field.data_type] = (
                type_distribution.get(field.data_type, 0) + 1
            )

            if field.semantic_type:
                semantic_type_distribution[field.semantic_type] = (
                    semantic_type_distribution.get(field.semantic_type, 0) + 1
                )

            if field.is_pii:
                pii_count += 1

            if field.is_nullable:
                nullable_count += 1

            if field.is_array:
                array_count += 1

            if field.null_percentage:
                total_null_percentage += float(field.null_percentage)

        num_fields = len(fields)

        return {
            "version_id": str(version.id),
            "version_number": version.version_number,
            "total_fields": num_fields,
            "type_distribution": type_distribution,
            "semantic_type_distribution": semantic_type_distribution,
            "pii_fields": pii_count,
            "pii_percentage": round((pii_count / num_fields * 100), 2),
            "nullable_fields": nullable_count,
            "array_fields": array_count,
            "average_null_percentage": round(
                total_null_percentage / num_fields, 2
            ) if num_fields > 0 else 0,
        }
