"""
Quality Analyzer for calculating data quality metrics.

This module provides the QualityAnalyzer class for analyzing data quality
metrics such as null percentage, cardinality, and statistical measures
for numeric fields.
"""

from typing import Any

import pandas as pd


class QualityAnalyzer:
    """Analyzes data quality metrics for fields"""

    def analyze_field(self, values: list[Any], data_type: str) -> dict[str, Any]:
        """
        Analyze field quality metrics.

        Args:
            values: List of field values
            data_type: Data type of field

        Returns:
            Dictionary of quality metrics
        """
        if not values:
            return {}

        # Convert to pandas Series for analysis
        series = pd.Series(values)

        metrics = {
            'total_count': len(values),
            'null_count': int(series.isna().sum()),
            'null_percentage': float((series.isna().sum() / len(values)) * 100),
            'distinct_count': int(series.nunique()),
            'cardinality_ratio': float(series.nunique() / len(values))
        }

        # Numeric-specific metrics
        if data_type in ('integer', 'float'):
            numeric_values = pd.to_numeric(series, errors='coerce').dropna()
            if len(numeric_values) > 0:
                metrics.update({
                    'min_value': float(numeric_values.min()),
                    'max_value': float(numeric_values.max()),
                    'mean_value': float(numeric_values.mean()),
                    'median_value': float(numeric_values.median()),
                    'std_dev': float(numeric_values.std()),
                    'percentile_25': float(numeric_values.quantile(0.25)),
                    'percentile_50': float(numeric_values.quantile(0.50)),
                    'percentile_75': float(numeric_values.quantile(0.75))
                })

        return metrics

    def get_sample_values(self, values: list[Any], max_samples: int = 10) -> list[Any]:
        """
        Get up to max_samples unique values.

        Args:
            values: List of values
            max_samples: Maximum number of samples to return

        Returns:
            List of unique sample values
        """
        unique_values = []
        seen = set()

        for value in values:
            if value not in seen and len(unique_values) < max_samples:
                unique_values.append(value)
                seen.add(value)

        return unique_values
