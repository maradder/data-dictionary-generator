"""
Core processing components for JSON analysis.

This package contains the processors responsible for analyzing JSON files
and extracting metadata for data dictionary generation.
"""

from .ai_generator import AIDescriptionGenerator
from .json_parser import FieldMetadata, JSONParser
from .pii_detector import PIIDetector
from .quality_analyzer import QualityAnalyzer
from .semantic_detector import SemanticTypeDetector
from .type_inferrer import TypeInferrer

__all__ = [
    "JSONParser",
    "FieldMetadata",
    "TypeInferrer",
    "SemanticTypeDetector",
    "PIIDetector",
    "QualityAnalyzer",
    "AIDescriptionGenerator",
]
