"""
Semantic Type Detector for identifying semantic types from field values.

This module provides the SemanticTypeDetector class for detecting semantic
types like email, phone, URL, UUID, dates, etc. from field names and values.
"""

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .ai_generator import AIDescriptionGenerator


class SemanticTypeDetector:
    """Detects semantic types from field values"""

    # Regex patterns - ordered by specificity to prevent false positives
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    # SSN patterns (US: XXX-XX-XXXX or XXXXXXXXX)
    SSN_PATTERN = re.compile(r'^(?:\d{3}-\d{2}-\d{4}|\d{9})$')

    # Credit card patterns (last 4 digits or full with spaces/dashes)
    CREDIT_CARD_PATTERN = re.compile(r'^(?:\*{12}\d{4}|\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}|\d{4})$')

    # Phone patterns - more restrictive (requires area code structure)
    PHONE_PATTERN = re.compile(r'^[\+]?[1]?[\s.-]?[(]?[0-9]{3}[)]?[\s.-]?[0-9]{3}[\s.-]?[0-9]{4}$')

    # URL patterns
    URL_PATTERN = re.compile(r'^https?://[^\s]+$')

    # UUID patterns
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)

    # ZIP code patterns (US: 5 digits or 5+4)
    ZIP_CODE_PATTERN = re.compile(r'^\d{5}(-\d{4})?$')

    # Identifier patterns (ends with _id or id, alphanumeric)
    ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

    # Date formats to try
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%m/%d/%Y',
        '%d/%m/%Y',
    ]

    def __init__(self, ai_generator: Optional['AIDescriptionGenerator'] = None, use_ai: bool = False):
        """
        Initialize SemanticTypeDetector.

        Args:
            ai_generator: Optional AI generator for enhanced detection
            use_ai: Whether to use AI for ambiguous cases
        """
        self.ai_generator = ai_generator
        self.use_ai = use_ai

    def detect(self, field_name: str, sample_values: list[Any], data_type: str) -> str | None:
        """
        Detect semantic type.

        Args:
            field_name: Field name (may contain hints)
            sample_values: Sample values
            data_type: Basic data type

        Returns:
            Semantic type or None
        """
        if not sample_values:
            return self._detect_from_field_name(field_name, data_type)

        # String-based semantic detection
        if data_type == 'string':
            semantic_type = self._detect_string_semantic_type(field_name, sample_values)
            if semantic_type:
                return semantic_type

        # Number-based semantic detection
        elif data_type in ('integer', 'number', 'float'):
            semantic_type = self._detect_number_semantic_type(field_name, sample_values)
            if semantic_type:
                return semantic_type

        # If no match found and AI is enabled, try AI detection
        if self.use_ai and self.ai_generator:
            return self._detect_with_ai(field_name, sample_values, data_type)

        # Fall back to field name hints
        return self._detect_from_field_name(field_name, data_type)

    def _detect_string_semantic_type(self, field_name: str, sample_values: list[Any]) -> str | None:
        """Detect semantic type for string fields using pattern matching."""
        matches = {
            'email': 0,
            'ssn': 0,
            'credit_card': 0,
            'phone': 0,
            'url': 0,
            'uuid': 0,
            'date': 0,
            'zip_code': 0,
            'currency': 0,
            'identifier': 0
        }

        for value in sample_values[:10]:
            if not isinstance(value, str):
                continue

            # Check patterns in order of specificity (most specific first)
            if self.EMAIL_PATTERN.match(value):
                matches['email'] += 1
            elif self.SSN_PATTERN.match(value):
                matches['ssn'] += 1
            elif self.CREDIT_CARD_PATTERN.match(value):
                matches['credit_card'] += 1
            elif self.UUID_PATTERN.match(value):
                matches['uuid'] += 1
            elif self.ZIP_CODE_PATTERN.match(value):
                matches['zip_code'] += 1
            elif self.PHONE_PATTERN.match(value):
                matches['phone'] += 1
            elif self.URL_PATTERN.match(value):
                matches['url'] += 1
            elif self._is_date(value):
                matches['date'] += 1
            elif self._is_currency(value):
                matches['currency'] += 1
            elif self._is_identifier(field_name, value):
                matches['identifier'] += 1

        # Find best match (>70% of samples)
        total_samples = len([v for v in sample_values[:10] if isinstance(v, str)])
        if total_samples == 0:
            return None

        for semantic_type, count in matches.items():
            if count / total_samples >= 0.7:
                return semantic_type

        return None

    def _detect_number_semantic_type(self, field_name: str, sample_values: list[Any]) -> str | None:
        """Detect semantic type for numeric fields."""
        field_lower = field_name.lower()

        # Check for currency/money fields
        if any(keyword in field_lower for keyword in ['price', 'cost', 'amount', 'balance', 'revenue', 'total', 'payment']):
            return 'currency'

        # Check for identifier fields
        if field_name.endswith('_id') or field_name.endswith('Id') or field_name == 'id':
            return 'identifier'

        # Check for count fields
        if any(keyword in field_lower for keyword in ['count', 'quantity', 'qty', 'number_of']):
            return 'count'

        return None

    def _detect_from_field_name(self, field_name: str, data_type: str) -> str | None:
        """Detect semantic type from field name hints."""
        field_lower = field_name.lower()

        # String-based hints
        if 'email' in field_lower:
            return 'email'
        elif 'ssn' in field_lower or 'social_security' in field_lower:
            return 'ssn'
        elif 'credit_card' in field_lower or 'card' in field_lower and 'last' in field_lower:
            return 'credit_card'
        elif 'phone' in field_lower or 'mobile' in field_lower or 'tel' in field_lower:
            return 'phone'
        elif 'url' in field_lower or 'link' in field_lower or 'website' in field_lower:
            return 'url'
        elif 'date' in field_lower or 'time' in field_lower or field_lower.endswith('_at'):
            return 'date'
        elif 'zip' in field_lower or 'postal' in field_lower:
            return 'zip_code'
        elif field_name.endswith('_id') or field_name.endswith('Id') or field_name == 'id':
            return 'identifier'
        elif any(keyword in field_lower for keyword in ['name', 'title', 'label']):
            return 'name'
        elif any(keyword in field_lower for keyword in ['status', 'type', 'category', 'tier', 'level']):
            return 'category'

        # Number-based hints
        if data_type in ('integer', 'number', 'float'):
            if any(keyword in field_lower for keyword in ['price', 'cost', 'amount', 'balance', 'revenue', 'total']):
                return 'currency'
            elif any(keyword in field_lower for keyword in ['count', 'quantity', 'qty']):
                return 'count'

        return None

    def _is_identifier(self, field_name: str, value: str) -> bool:
        """Check if value looks like an identifier."""
        # Must be alphanumeric with possible dashes/underscores
        if not self.ID_PATTERN.match(value):
            return False

        # Field name should suggest it's an ID
        field_lower = field_name.lower()
        return (field_name.endswith('_id') or field_name.endswith('Id') or
                field_name == 'id' or 'identifier' in field_lower)

    def _is_date(self, value: str) -> bool:
        """Check if value is a date"""
        for fmt in self.DATE_FORMATS:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        return False

    def _is_currency(self, value: str) -> bool:
        """Check if value looks like currency"""
        # Simple check for currency symbols
        return value.startswith(('$', '€', '£', '¥')) and any(c.isdigit() for c in value)

    def _detect_with_ai(self, field_name: str, sample_values: list[Any], data_type: str) -> str | None:
        """
        Use AI to detect semantic type for ambiguous cases.

        Args:
            field_name: Field name
            sample_values: Sample values
            data_type: Basic data type

        Returns:
            Semantic type detected by AI or None
        """
        if not self.ai_generator or not self.ai_generator.client:
            return None

        # Build prompt for AI
        samples_str = ", ".join(str(v) for v in sample_values[:5])
        prompt = f"""Analyze this data field and identify its semantic type.

Field Name: {field_name}
Data Type: {data_type}
Sample Values: {samples_str}

What is the most likely semantic type? Choose from:
- email
- phone
- ssn (social security number)
- credit_card
- url
- uuid
- date (or datetime/timestamp)
- zip_code (or postal_code)
- currency (monetary amount)
- identifier (ID field)
- name (person name, organization name, etc.)
- category (status, type, tier, etc.)
- count (quantity, number of items)
- address (street address, location)
- country (country name or code)
- state (state/province)
- city
- other (if none of the above fit)

Respond with ONLY the semantic type name, nothing else."""

        try:
            response = self.ai_generator.client.chat.completions.create(
                model=self.ai_generator.model,
                messages=[
                    {"role": "system", "content": "You are a data classification expert. Respond with only the semantic type name."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=20
            )

            semantic_type = response.choices[0].message.content.strip().lower()

            # Validate the response
            valid_types = {
                'email', 'phone', 'ssn', 'credit_card', 'url', 'uuid',
                'date', 'datetime', 'timestamp', 'zip_code', 'postal_code',
                'currency', 'identifier', 'name', 'category', 'count',
                'address', 'country', 'state', 'city'
            }

            # Normalize some variations
            if semantic_type in ('datetime', 'timestamp'):
                semantic_type = 'date'
            elif semantic_type == 'postal_code':
                semantic_type = 'zip_code'

            if semantic_type in valid_types:
                return semantic_type

        except Exception:
            # If AI fails, return None to fall back to other methods
            pass

        return None
