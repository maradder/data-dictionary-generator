"""
AI Description Generator for creating field descriptions using OpenAI.

This module provides the AIDescriptionGenerator class for generating
human-readable descriptions and business-friendly names for fields
using OpenAI's API.
"""

import os
from typing import Any

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


class AIDescriptionGenerator:
    """Generates field descriptions using OpenAI"""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """
        Initialize AIDescriptionGenerator.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (defaults to OPENAI_MODEL env var or "gpt-3.5-turbo")
        """
        # Only initialize OpenAI client if API key is available
        api_key_value = api_key or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")

        if api_key_value and api_key_value != "sk-your-openai-api-key-here":
            # Initialize with base_url if provided (for OpenAI-compatible servers like LMStudio)
            if base_url:
                self.client = OpenAI(api_key=api_key_value, base_url=base_url)
            else:
                self.client = OpenAI(api_key=api_key_value)
        else:
            self.client = None

        # Use provided model, or OPENAI_MODEL env var, or default to gpt-3.5-turbo
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.cache = {}  # Simple in-memory cache

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_description(
        self,
        field_path: str,
        field_name: str,
        data_type: str,
        semantic_type: str | None,
        sample_values: list[Any]
    ) -> tuple[str, str]:
        """
        Generate description and business-friendly name.

        Args:
            field_path: Full path to field
            field_name: Name of field
            data_type: Data type
            semantic_type: Semantic type (if detected)
            sample_values: Sample values

        Returns:
            (description, business_name)
        """
        # Check cache
        cache_key = f"{field_path}:{data_type}:{semantic_type}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # If no OpenAI client, return fallback immediately
        if self.client is None:
            return self._fallback_description(field_name, data_type, semantic_type)

        # Build prompt
        prompt = self._build_prompt(field_path, field_name, data_type, semantic_type, sample_values)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data documentation expert. Generate concise, clear descriptions for data fields."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )

            content = response.choices[0].message.content.strip()
            description, business_name = self._parse_response(content)

            # Cache result
            self.cache[cache_key] = (description, business_name)

            return (description, business_name)

        except Exception:
            # Fallback to simple description
            return self._fallback_description(field_name, data_type, semantic_type)

    def _build_prompt(
        self,
        field_path: str,
        field_name: str,
        data_type: str,
        semantic_type: str | None,
        sample_values: list[Any]
    ) -> str:
        """Build prompt for AI"""
        samples_str = ", ".join(str(v) for v in sample_values[:5])

        prompt = f"""Generate a description and business-friendly name for this data field:

Field Path: {field_path}
Field Name: {field_name}
Data Type: {data_type}
Semantic Type: {semantic_type or 'N/A'}
Sample Values: {samples_str}

Please respond in this format:
DESCRIPTION: <1-2 sentence description>
BUSINESS_NAME: <Business-friendly name>"""

        return prompt

    def _parse_response(self, content: str) -> tuple[str, str]:
        """Parse AI response"""
        lines = content.split('\n')
        description = ""
        business_name = ""

        for line in lines:
            if line.startswith("DESCRIPTION:"):
                description = line.replace("DESCRIPTION:", "").strip()
            elif line.startswith("BUSINESS_NAME:"):
                business_name = line.replace("BUSINESS_NAME:", "").strip()

        return (description, business_name)

    def _fallback_description(
        self,
        field_name: str,
        data_type: str,
        semantic_type: str | None
    ) -> tuple[str, str]:
        """Generate fallback description"""
        # Simple rule-based description
        business_name = field_name.replace('_', ' ').title()
        description = f"{business_name} field of type {semantic_type or data_type}"

        return (description, business_name)

    async def generate_batch(
        self,
        fields: list[dict[str, Any]],
        batch_size: int = 10
    ) -> list[tuple[str, str]]:
        """
        Generate descriptions for multiple fields.

        Args:
            fields: List of field dictionaries
            batch_size: Number of fields to process at once

        Returns:
            List of (description, business_name) tuples
        """
        # TODO: Implement batch processing with rate limiting
        results = []
        for field in fields:
            result = self.generate_description(
                field['field_path'],
                field['field_name'],
                field['data_type'],
                field.get('semantic_type'),
                field.get('sample_values', [])
            )
            results.append(result)
        return results
