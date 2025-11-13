"""
Core processing components for JSON analysis.

This package contains the processors responsible for analyzing JSON files
and extracting metadata for data dictionary generation.
"""

from .ai_generator import AIDescriptionGenerator
from .geopackage_parser import GeoPackageFieldMetadata, GeoPackageParser
from .json_parser import FieldMetadata, JSONParser
from .mongodb_parser import MongoDBFieldMetadata, MongoDBParser
from .pii_detector import PIIDetector
from .protobuf_parser import ProtobufParser
from .quality_analyzer import QualityAnalyzer
from .semantic_detector import SemanticTypeDetector
from .sqlite_parser import SQLiteFieldMetadata, SQLiteParser
from .type_inferrer import TypeInferrer

__all__ = [
    "JSONParser",
    "FieldMetadata",
    "MongoDBParser",
    "MongoDBFieldMetadata",
    "SQLiteParser",
    "SQLiteFieldMetadata",
    "GeoPackageParser",
    "GeoPackageFieldMetadata",
    "ProtobufParser",
    "TypeInferrer",
    "SemanticTypeDetector",
    "PIIDetector",
    "QualityAnalyzer",
    "AIDescriptionGenerator",
]
