"""
MongoDB Extended JSON Parser for handling MongoDB export format.

This module extends the JSONParser to support MongoDB Extended JSON format,
which includes special type markers like $oid, $date, $numberLong, etc.
"""

import re
from pathlib import Path
from typing import Any

from .json_parser import FieldMetadata, JSONParser


class MongoDBFieldMetadata(FieldMetadata):
    """
    Extended FieldMetadata that detects MongoDB Extended JSON types.

    Handles MongoDB type wrappers:
    - {"$oid": "..."} → mongodb_objectid
    - {"$date": "..."} or {"$date": {"$numberLong": "..."}} → mongodb_date
    - {"$numberLong": "..."} → mongodb_long
    - {"$numberDecimal": "..."} → mongodb_decimal
    - {"$binary": {...}} → mongodb_binary
    """

    # Regex patterns for MongoDB type detection
    OBJECTID_PATTERN = re.compile(r'^[a-f0-9]{24}$', re.IGNORECASE)
    ISO_DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$')

    def observe_value(self, value: Any):
        """
        Record observation of a value, detecting MongoDB Extended JSON types.

        Args:
            value: Value to observe (may be MongoDB type wrapper)
        """
        # Check for MongoDB Extended JSON type wrappers first
        if isinstance(value, dict):
            # Check for ObjectId: {"$oid": "..."}
            if "$oid" in value and isinstance(value.get("$oid"), str):
                oid_value = value["$oid"]
                if self.OBJECTID_PATTERN.match(oid_value):
                    self.total_count += 1
                    self.types_seen.add('mongodb_objectid')
                    self._add_sample(oid_value)
                    return

            # Check for Date: {"$date": "..."} or {"$date": {"$numberLong": "..."}}
            if "$date" in value:
                date_value = value["$date"]
                if isinstance(date_value, str) and self.ISO_DATE_PATTERN.match(date_value):
                    self.total_count += 1
                    self.types_seen.add('mongodb_date')
                    self._add_sample(date_value)
                    return
                elif isinstance(date_value, dict) and "$numberLong" in date_value:
                    self.total_count += 1
                    self.types_seen.add('mongodb_date')
                    self._add_sample(date_value["$numberLong"])
                    return

            # Check for NumberLong: {"$numberLong": "..."}
            if "$numberLong" in value and isinstance(value.get("$numberLong"), str):
                self.total_count += 1
                self.types_seen.add('mongodb_long')
                self._add_sample(value["$numberLong"])
                return

            # Check for NumberDecimal: {"$numberDecimal": "..."}
            if "$numberDecimal" in value and isinstance(value.get("$numberDecimal"), str):
                self.total_count += 1
                self.types_seen.add('mongodb_decimal')
                self._add_sample(value["$numberDecimal"])
                return

            # Check for Binary: {"$binary": {...}}
            if "$binary" in value and isinstance(value.get("$binary"), dict):
                self.total_count += 1
                self.types_seen.add('mongodb_binary')
                self._add_sample("<binary>")
                return

        # Fall back to parent implementation for standard JSON types
        super().observe_value(value)


class MongoDBParser(JSONParser):
    """
    Parser for MongoDB Extended JSON format.

    Extends JSONParser to handle MongoDB-specific type markers while
    maintaining compatibility with standard JSON parsing.
    """

    def __init__(self, max_samples: int = 1000, max_depth: int = 10):
        """
        Initialize MongoDBParser.

        Args:
            max_samples: Maximum number of records to sample
            max_depth: Maximum nesting depth to analyze
        """
        super().__init__(max_samples=max_samples, max_depth=max_depth)

    def _extract_fields(
        self,
        obj: Any,
        parent_path: str,
        fields_map: dict[str, FieldMetadata],
        depth: int
    ):
        """
        Recursively extract fields from object, handling MongoDB type wrappers.

        Args:
            obj: Object to extract fields from
            parent_path: Path to parent object
            fields_map: Dictionary mapping field paths to metadata
            depth: Current nesting depth
        """
        if depth > self.max_depth:
            return

        if isinstance(obj, dict):
            # Check if this is a MongoDB type wrapper - don't recurse into it
            is_mongodb_type = self._is_mongodb_type_wrapper(obj)

            if is_mongodb_type:
                # Don't treat MongoDB type wrappers as nested objects
                return

            # Process regular object
            for key, value in obj.items():
                field_path = f"{parent_path}.{key}" if parent_path else key

                # Update or create field metadata using MongoDBFieldMetadata
                if field_path not in fields_map:
                    fields_map[field_path] = MongoDBFieldMetadata(
                        field_path=field_path,
                        field_name=key,
                        parent_path=parent_path,
                        nesting_level=depth
                    )

                field_meta = fields_map[field_path]
                field_meta.observe_value(value)

                # Recurse for nested objects/arrays (but not MongoDB type wrappers)
                if isinstance(value, (dict, list)) and not self._is_mongodb_type_wrapper(value):
                    self._extract_fields(value, field_path, fields_map, depth + 1)

        elif isinstance(obj, list):
            # For arrays, analyze sample items
            for _i, item in enumerate(obj[:10]):  # Sample first 10 items
                self._extract_fields(item, parent_path, fields_map, depth)

    def _is_mongodb_type_wrapper(self, obj: Any) -> bool:
        """
        Check if object is a MongoDB Extended JSON type wrapper.

        Args:
            obj: Object to check

        Returns:
            True if object is a MongoDB type wrapper, False otherwise
        """
        if not isinstance(obj, dict):
            return False

        # Check for MongoDB type markers
        mongodb_markers = {"$oid", "$date", "$numberLong", "$numberDecimal", "$binary"}
        return any(marker in obj for marker in mongodb_markers)
