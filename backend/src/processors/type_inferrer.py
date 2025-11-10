"""
Type Inferrer for determining data types from observed values.

This module provides the TypeInferrer class for inferring data types
with confidence scores based on observed values in JSON fields.
"""

from collections import Counter


class TypeInferrer:
    """Infers data types from observed values"""

    def infer_type(self, types_seen: list[str]) -> tuple[str, float]:
        """
        Infer primary type and confidence score.

        Args:
            types_seen: List of observed types

        Returns:
            (data_type, confidence_score)
        """
        if not types_seen:
            return ('unknown', 0.0)

        # Count type occurrences
        type_counts = Counter(types_seen)
        total = sum(type_counts.values())

        # Remove null from consideration if other types exist
        if len(type_counts) > 1 and 'null' in type_counts:
            non_null_counts = {k: v for k, v in type_counts.items() if k != 'null'}
            if non_null_counts:
                type_counts = Counter(non_null_counts)
                total = sum(type_counts.values())

        # Get most common type
        most_common_type, count = type_counts.most_common(1)[0]
        confidence = (count / total) * 100

        # Type hierarchy: if integer and float both present, use float
        if 'integer' in type_counts and 'float' in type_counts:
            return ('float', (type_counts['integer'] + type_counts['float']) / total * 100)

        return (most_common_type, confidence)

    def infer_array_item_type(self, item_types: list[str]) -> str:
        """
        Infer array item type.

        Args:
            item_types: List of observed item types

        Returns:
            Inferred array item type or 'mixed'
        """
        if not item_types:
            return 'unknown'

        unique_types = set(item_types)
        if len(unique_types) == 1:
            return list(unique_types)[0]
        else:
            return 'mixed'
