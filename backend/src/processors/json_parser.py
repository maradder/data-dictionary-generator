"""
JSON Parser for streaming analysis of JSON files.

This module provides the JSONParser class for parsing large JSON files
using streaming techniques with ijson, extracting field structure and
sample values.
"""

from pathlib import Path
from typing import Any

import ijson


class JSONParser:
    """
    Streaming JSON parser for large files.
    Extracts field structure and sample values.
    """

    def __init__(self, max_samples: int = 1000, max_depth: int = 10):
        """
        Initialize JSONParser.

        Args:
            max_samples: Maximum number of records to sample
            max_depth: Maximum nesting depth to analyze
        """
        self.max_samples = max_samples
        self.max_depth = max_depth

    def parse_file(self, file_path: Path) -> dict[str, Any]:
        """
        Parse JSON file and extract field metadata.

        Args:
            file_path: Path to JSON file

        Returns:
            {
                'fields': [...],  # List of field metadata
                'total_records': int,
                'is_array': bool  # Root is array or object
            }
        """
        # Check if root is array or object
        with open(file_path, 'rb') as f:
            first_char = self._skip_whitespace(f)
            is_array = first_char == b'['

        if is_array:
            return self._parse_array_root(file_path)
        else:
            return self._parse_object_root(file_path)

    def _skip_whitespace(self, f) -> bytes:
        """Skip whitespace and return first non-whitespace character."""
        while True:
            char = f.read(1)
            if not char:
                return b''
            if char not in b' \t\n\r':
                return char

    def _parse_array_root(self, file_path: Path) -> dict[str, Any]:
        """Parse JSON array of objects"""
        fields_map = {}  # field_path -> FieldMetadata
        records_processed = 0

        with open(file_path, 'rb') as f:
            # Use ijson for streaming parsing
            items = ijson.items(f, 'item')

            for item in items:
                if records_processed >= self.max_samples:
                    break

                # Extract fields from this record
                self._extract_fields(
                    item,
                    parent_path='',
                    fields_map=fields_map,
                    depth=0
                )
                records_processed += 1

        return {
            'fields': [field.to_dict() for field in fields_map.values()],
            'total_records': records_processed,
            'is_array': True
        }

    def _parse_object_root(self, file_path: Path) -> dict[str, Any]:
        """Parse single JSON object"""
        fields_map = {}

        with open(file_path, 'rb') as f:
            obj = ijson.items(f, '')
            for item in obj:
                self._extract_fields(
                    item,
                    parent_path='',
                    fields_map=fields_map,
                    depth=0
                )

        return {
            'fields': [field.to_dict() for field in fields_map.values()],
            'total_records': 1,
            'is_array': False
        }

    def _extract_fields(
        self,
        obj: Any,
        parent_path: str,
        fields_map: dict[str, 'FieldMetadata'],
        depth: int
    ):
        """Recursively extract fields from object"""
        if depth > self.max_depth:
            return

        if isinstance(obj, dict):
            for key, value in obj.items():
                field_path = f"{parent_path}.{key}" if parent_path else key

                # Update or create field metadata
                if field_path not in fields_map:
                    fields_map[field_path] = FieldMetadata(
                        field_path=field_path,
                        field_name=key,
                        parent_path=parent_path,
                        nesting_level=depth
                    )

                field_meta = fields_map[field_path]
                field_meta.observe_value(value)

                # Recurse for nested objects/arrays
                if isinstance(value, (dict, list)):
                    self._extract_fields(value, field_path, fields_map, depth + 1)

        elif isinstance(obj, list):
            # For arrays, analyze sample items
            for _i, item in enumerate(obj[:10]):  # Sample first 10 items
                self._extract_fields(item, parent_path, fields_map, depth)


class FieldMetadata:
    """Accumulates metadata for a single field"""

    def __init__(self, field_path: str, field_name: str, parent_path: str, nesting_level: int):
        """
        Initialize FieldMetadata.

        Args:
            field_path: Full dot-notation path to field
            field_name: Name of the field
            parent_path: Path to parent object
            nesting_level: Depth in JSON hierarchy
        """
        self.field_path = field_path
        self.field_name = field_name
        self.parent_path = parent_path
        self.nesting_level = nesting_level
        self.values = []  # Sample values
        self.types_seen = set()
        self.null_count = 0
        self.total_count = 0
        self.is_array = False
        self.array_item_types = set()

    def observe_value(self, value: Any):
        """Record observation of a value"""
        self.total_count += 1

        if value is None:
            self.null_count += 1
            self.types_seen.add('null')
        elif isinstance(value, bool):
            self.types_seen.add('boolean')
            self._add_sample(value)
        elif isinstance(value, int):
            self.types_seen.add('integer')
            self._add_sample(value)
        elif isinstance(value, float):
            self.types_seen.add('float')
            self._add_sample(value)
        elif isinstance(value, str):
            self.types_seen.add('string')
            self._add_sample(value)
        elif isinstance(value, list):
            self.is_array = True
            self.types_seen.add('array')
            # Analyze array item types
            for item in value[:10]:
                self.array_item_types.add(type(item).__name__)
        elif isinstance(value, dict):
            self.types_seen.add('object')

    def _add_sample(self, value: Any):
        """Add sample value (up to 10 unique)"""
        if len(self.values) < 10 and value not in self.values:
            self.values.append(value)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'field_path': self.field_path,
            'field_name': self.field_name,
            'parent_path': self.parent_path,
            'nesting_level': self.nesting_level,
            'types_seen': list(self.types_seen),
            'is_array': self.is_array,
            'array_item_types': list(self.array_item_types),
            'sample_values': self.values,
            'null_count': self.null_count,
            'total_count': self.total_count,
            'null_percentage': (self.null_count / self.total_count * 100) if self.total_count > 0 else 0
        }
