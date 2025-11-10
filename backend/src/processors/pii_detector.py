"""
PII Detector for identifying personally identifiable information.

This module provides the PIIDetector class for detecting potential PII
in fields based on field names, semantic types, and value patterns.
"""

import re
from typing import Any


class PIIDetector:
    """Detects potential PII in fields"""

    # SSN pattern: XXX-XX-XXXX
    SSN_PATTERN = re.compile(r'^\d{3}-\d{2}-\d{4}$')

    # Credit card pattern (basic Luhn check)
    CC_PATTERN = re.compile(r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$')

    def detect_pii(
        self,
        field_path: str,
        field_name: str,
        semantic_type: str | None,
        sample_values: list[Any]
    ) -> tuple[bool, str | None]:
        """
        Detect if field contains PII.

        Args:
            field_path: Full path to field
            field_name: Name of field
            semantic_type: Detected semantic type
            sample_values: Sample values from field

        Returns:
            (is_pii, pii_type)
        """
        # Semantic type-based detection
        if semantic_type in ('email', 'phone'):
            return (True, semantic_type)

        # Field name-based detection
        field_lower = field_name.lower()
        pii_indicators = {
            'email': 'email',
            'phone': 'phone',
            'mobile': 'phone',
            'ssn': 'ssn',
            'social_security': 'ssn',
            'credit_card': 'credit_card',
            'passport': 'passport',
            'driver_license': 'drivers_license',
            'address': 'address',
            'ip_address': 'ip_address'
        }

        for indicator, pii_type in pii_indicators.items():
            if indicator in field_lower:
                return (True, pii_type)

        # Value-based detection
        if sample_values:
            ssn_count = sum(1 for v in sample_values if isinstance(v, str) and self.SSN_PATTERN.match(v))
            if ssn_count / len(sample_values) > 0.5:
                return (True, 'ssn')

            cc_count = sum(1 for v in sample_values if isinstance(v, str) and self._is_credit_card(v))
            if cc_count / len(sample_values) > 0.5:
                return (True, 'credit_card')

        return (False, None)

    def _is_credit_card(self, value: str) -> bool:
        """Check if value is credit card using Luhn algorithm"""
        if not self.CC_PATTERN.match(value):
            return False

        # Remove spaces/dashes
        digits = re.sub(r'[\s-]', '', value)

        # Luhn algorithm
        def luhn_check(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10 == 0

        return luhn_check(digits)
