"""
AI Description Generator for creating field descriptions using OpenAI.

This module provides the AIDescriptionGenerator class for generating
human-readable descriptions and business-friendly names for fields
using OpenAI's API with comprehensive error handling, caching, and metrics.
"""

import asyncio
import logging
import os
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

from openai import AsyncOpenAI
from openai import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    RateLimitError as OpenAIRateLimitError,
)

from ..core.config import settings
from ..core.exceptions import ExternalServiceError, RateLimitError

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with TTL and model version tracking."""

    value: tuple[str, str]
    expiry_time: float
    model_version: str


@dataclass
class CostMetrics:
    """Cost and usage metrics for OpenAI API calls."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cached_requests: int = 0
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    rate_limit_errors: int = 0
    timeout_errors: int = 0
    api_errors: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    cache_evictions: int = 0

    def __str__(self) -> str:
        """Format metrics for logging."""
        return (
            f"Requests: {self.total_requests} "
            f"(Success: {self.successful_requests}, Failed: {self.failed_requests}, Cached: {self.cached_requests}) | "
            f"Tokens: {self.total_tokens} (Prompt: {self.prompt_tokens}, Completion: {self.completion_tokens}) | "
            f"Errors: Rate Limit: {self.rate_limit_errors}, Timeout: {self.timeout_errors}, API: {self.api_errors} | "
            f"Cache: Hits: {self.cache_hits}, Misses: {self.cache_misses}, Evictions: {self.cache_evictions}"
        )


class AIDescriptionGenerator:
    """
    Generates field descriptions using OpenAI with comprehensive error handling.

    Features:
    - Async API calls with timeout protection
    - TTL-aware cache with LRU eviction
    - Smart retry logic with error classification
    - Cost and usage metrics tracking
    - Rate limiting via semaphore
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """
        Initialize AIDescriptionGenerator.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (defaults to config or "gpt-3.5-turbo")
        """
        # Only initialize OpenAI client if API key is available
        api_key_value = api_key or os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        base_url = os.getenv("OPENAI_BASE_URL")

        if api_key_value and api_key_value != "sk-your-openai-api-key-here":
            # Initialize AsyncOpenAI client with timeout
            timeout_config = {
                "timeout": settings.OPENAI_REQUEST_TIMEOUT,
                "connect": settings.OPENAI_CONNECTION_TIMEOUT,
            }

            if base_url:
                self.client = AsyncOpenAI(
                    api_key=api_key_value, base_url=base_url, timeout=timeout_config
                )
            else:
                self.client = AsyncOpenAI(api_key=api_key_value, timeout=timeout_config)
        else:
            self.client = None

        # Use provided model, or config, or default
        self.model = (
            model or os.getenv("OPENAI_MODEL") or settings.OPENAI_MODEL or "gpt-3.5-turbo"
        )

        # TTL-aware cache with LRU eviction
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._cache_enabled = settings.OPENAI_CACHE_ENABLED
        self._cache_ttl = settings.OPENAI_CACHE_TTL
        self._cache_max_size = settings.OPENAI_CACHE_MAX_SIZE

        # Cost metrics tracking
        self.metrics = CostMetrics()
        self._metrics_enabled = settings.OPENAI_METRICS_ENABLED

        # Rate limiting semaphore
        self._semaphore = asyncio.Semaphore(settings.OPENAI_MAX_CONCURRENT_REQUESTS)

        # Circuit breaker state
        self._consecutive_failures = 0
        self._circuit_open = False
        self._circuit_open_until = 0.0

    def _get_from_cache(self, cache_key: str) -> tuple[str, str] | None:
        """
        Get value from cache if valid.

        Args:
            cache_key: Cache key to lookup

        Returns:
            Cached value or None if not found/expired
        """
        if not self._cache_enabled:
            return None

        if cache_key not in self._cache:
            if self._metrics_enabled:
                self.metrics.cache_misses += 1
            return None

        entry = self._cache[cache_key]

        # Check expiry
        if time.time() > entry.expiry_time:
            del self._cache[cache_key]
            if self._metrics_enabled:
                self.metrics.cache_misses += 1
            return None

        # Check model version
        if entry.model_version != self.model:
            del self._cache[cache_key]
            if self._metrics_enabled:
                self.metrics.cache_misses += 1
            return None

        # Move to end (LRU)
        self._cache.move_to_end(cache_key)

        if self._metrics_enabled:
            self.metrics.cache_hits += 1

        return entry.value

    def _put_in_cache(self, cache_key: str, value: tuple[str, str]) -> None:
        """
        Put value in cache with TTL.

        Args:
            cache_key: Cache key
            value: Value to cache
        """
        if not self._cache_enabled:
            return

        # Evict if at max size
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entry (LRU)
            self._cache.popitem(last=False)
            if self._metrics_enabled:
                self.metrics.cache_evictions += 1

        # Add new entry
        entry = CacheEntry(
            value=value,
            expiry_time=time.time() + self._cache_ttl,
            model_version=self.model,
        )
        self._cache[cache_key] = entry

    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open."""
        if not self._circuit_open:
            return False

        # Check if circuit should close
        if time.time() >= self._circuit_open_until:
            self._circuit_open = False
            self._consecutive_failures = 0
            logger.info("Circuit breaker closed, resuming OpenAI API calls")
            return False

        return True

    def _open_circuit(self) -> None:
        """Open circuit breaker after consecutive failures."""
        self._circuit_open = True
        self._circuit_open_until = time.time() + 60  # Open for 60 seconds
        logger.warning(
            f"Circuit breaker opened after {self._consecutive_failures} consecutive failures"
        )

    async def _call_openai_with_retry(
        self, prompt: str, max_tokens: int = 150
    ) -> tuple[str, int, int, int]:
        """
        Call OpenAI API with smart retry logic.

        Args:
            prompt: Prompt to send
            max_tokens: Maximum tokens in response

        Returns:
            (response_content, total_tokens, prompt_tokens, completion_tokens)

        Raises:
            RateLimitError: If rate limited after retries
            ExternalServiceError: If API fails after retries
        """
        attempt = 0
        wait_time = settings.OPENAI_RETRY_MIN_WAIT

        while attempt < settings.OPENAI_MAX_RETRY_ATTEMPTS:
            try:
                # Use semaphore for rate limiting
                async with self._semaphore:
                    # Add timeout protection
                    response = await asyncio.wait_for(
                        self.client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a data documentation expert. Generate concise, clear descriptions for data fields.",
                                },
                                {"role": "user", "content": prompt},
                            ],
                            temperature=settings.OPENAI_TEMPERATURE,
                            max_tokens=max_tokens,
                        ),
                        timeout=settings.OPENAI_REQUEST_TIMEOUT,
                    )

                # Extract token usage
                usage = response.usage
                total_tokens = usage.total_tokens if usage else 0
                prompt_tokens = usage.prompt_tokens if usage else 0
                completion_tokens = usage.completion_tokens if usage else 0

                # Get response content
                content = response.choices[0].message.content.strip()

                return (content, total_tokens, prompt_tokens, completion_tokens)

            except asyncio.TimeoutError:
                attempt += 1
                if self._metrics_enabled:
                    self.metrics.timeout_errors += 1

                logger.warning(
                    f"OpenAI API timeout (attempt {attempt}/{settings.OPENAI_MAX_RETRY_ATTEMPTS})"
                )

                if attempt >= settings.OPENAI_MAX_RETRY_ATTEMPTS:
                    raise ExternalServiceError(
                        "OpenAI API request timed out",
                        details={"attempts": attempt, "timeout": settings.OPENAI_REQUEST_TIMEOUT},
                    )

                # Retry with exponential backoff
                await asyncio.sleep(wait_time)
                wait_time = min(
                    wait_time * settings.OPENAI_RETRY_MULTIPLIER, settings.OPENAI_RETRY_MAX_WAIT
                )

            except OpenAIRateLimitError as e:
                attempt += 1
                if self._metrics_enabled:
                    self.metrics.rate_limit_errors += 1

                # Parse Retry-After header if available
                retry_after = getattr(e, "retry_after", None) or wait_time

                logger.warning(
                    f"OpenAI rate limit hit (attempt {attempt}/{settings.OPENAI_MAX_RETRY_ATTEMPTS}), "
                    f"waiting {retry_after}s"
                )

                if attempt >= settings.OPENAI_MAX_RETRY_ATTEMPTS:
                    raise RateLimitError(
                        "OpenAI API rate limit exceeded",
                        details={"attempts": attempt, "retry_after": retry_after},
                    )

                # Wait for retry-after period
                await asyncio.sleep(retry_after)
                wait_time = min(
                    wait_time * settings.OPENAI_RETRY_MULTIPLIER, settings.OPENAI_RETRY_MAX_WAIT
                )

            except AuthenticationError as e:
                # Don't retry auth errors
                if self._metrics_enabled:
                    self.metrics.api_errors += 1

                logger.error(f"OpenAI authentication failed: {e}")
                raise ExternalServiceError(
                    "OpenAI authentication failed",
                    details={"error": str(e)},
                )

            except APIConnectionError as e:
                attempt += 1
                if self._metrics_enabled:
                    self.metrics.api_errors += 1

                logger.warning(
                    f"OpenAI connection error (attempt {attempt}/{settings.OPENAI_MAX_RETRY_ATTEMPTS}): {e}"
                )

                if attempt >= settings.OPENAI_MAX_RETRY_ATTEMPTS:
                    raise ExternalServiceError(
                        "OpenAI API connection failed",
                        details={"attempts": attempt, "error": str(e)},
                    )

                # Retry with exponential backoff
                await asyncio.sleep(wait_time)
                wait_time = min(
                    wait_time * settings.OPENAI_RETRY_MULTIPLIER, settings.OPENAI_RETRY_MAX_WAIT
                )

            except APIError as e:
                attempt += 1
                if self._metrics_enabled:
                    self.metrics.api_errors += 1

                # Check if it's a server error (5xx) - retry
                # Otherwise, fail immediately
                status_code = getattr(e, "status_code", None)
                if status_code and 500 <= status_code < 600:
                    logger.warning(
                        f"OpenAI server error {status_code} (attempt {attempt}/{settings.OPENAI_MAX_RETRY_ATTEMPTS})"
                    )

                    if attempt >= settings.OPENAI_MAX_RETRY_ATTEMPTS:
                        raise ExternalServiceError(
                            f"OpenAI API server error: {status_code}",
                            details={"attempts": attempt, "error": str(e)},
                        )

                    # Retry with exponential backoff
                    await asyncio.sleep(wait_time)
                    wait_time = min(
                        wait_time * settings.OPENAI_RETRY_MULTIPLIER,
                        settings.OPENAI_RETRY_MAX_WAIT,
                    )
                else:
                    # Client error, don't retry
                    logger.error(f"OpenAI API error: {e}")
                    raise ExternalServiceError(
                        "OpenAI API error",
                        details={"status_code": status_code, "error": str(e)},
                    )

            except Exception as e:
                # Unexpected error, don't retry
                if self._metrics_enabled:
                    self.metrics.api_errors += 1

                logger.error(f"Unexpected OpenAI API error: {e}", exc_info=True)
                raise ExternalServiceError(
                    "Unexpected OpenAI API error",
                    details={"error": str(e)},
                )

        # Should never reach here
        raise ExternalServiceError("Max retry attempts exceeded")

    async def generate_description(
        self,
        field_path: str,
        field_name: str,
        data_type: str,
        semantic_type: str | None,
        sample_values: list[Any],
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
        # Track total requests
        if self._metrics_enabled:
            self.metrics.total_requests += 1

        # Check cache
        cache_key = f"{field_path}:{data_type}:{semantic_type}"
        cached_value = self._get_from_cache(cache_key)
        if cached_value is not None:
            if self._metrics_enabled:
                self.metrics.cached_requests += 1
            return cached_value

        # If no OpenAI client, return fallback immediately
        if self.client is None:
            logger.debug("No OpenAI client configured, using fallback")
            return self._fallback_description(field_name, data_type, semantic_type)

        # Check circuit breaker
        if self._is_circuit_open():
            logger.warning("Circuit breaker is open, using fallback")
            if self._metrics_enabled:
                self.metrics.failed_requests += 1
            return self._fallback_description(field_name, data_type, semantic_type)

        # Build prompt
        prompt = self._build_prompt(field_path, field_name, data_type, semantic_type, sample_values)

        try:
            # Call OpenAI with retry logic
            content, total_tokens, prompt_tokens, completion_tokens = (
                await self._call_openai_with_retry(prompt, max_tokens=150)
            )

            # Update metrics
            if self._metrics_enabled:
                self.metrics.successful_requests += 1
                self.metrics.total_tokens += total_tokens
                self.metrics.prompt_tokens += prompt_tokens
                self.metrics.completion_tokens += completion_tokens

            # Reset circuit breaker on success
            self._consecutive_failures = 0

            # Parse response
            description, business_name = self._parse_response(content)

            # Cache result
            result = (description, business_name)
            self._put_in_cache(cache_key, result)

            return result

        except (RateLimitError, ExternalServiceError) as e:
            # Track failure for circuit breaker
            self._consecutive_failures += 1
            if self._consecutive_failures >= 3:
                self._open_circuit()

            if self._metrics_enabled:
                self.metrics.failed_requests += 1

            logger.warning(f"OpenAI API call failed: {e}, using fallback")

            # Fallback to simple description
            return self._fallback_description(field_name, data_type, semantic_type)

    def _build_prompt(
        self,
        field_path: str,
        field_name: str,
        data_type: str,
        semantic_type: str | None,
        sample_values: list[Any],
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
        lines = content.split("\n")
        description = ""
        business_name = ""

        for line in lines:
            if line.startswith("DESCRIPTION:"):
                description = line.replace("DESCRIPTION:", "").strip()
            elif line.startswith("BUSINESS_NAME:"):
                business_name = line.replace("BUSINESS_NAME:", "").strip()

        return (description, business_name)

    def _fallback_description(
        self, field_name: str, data_type: str, semantic_type: str | None
    ) -> tuple[str, str]:
        """Generate fallback description"""
        # Simple rule-based description
        business_name = field_name.replace("_", " ").title()
        description = f"{business_name} field of type {semantic_type or data_type}"

        return (description, business_name)

    async def generate_batch(
        self, fields: list[dict[str, Any]], batch_size: int = 10
    ) -> list[tuple[str, str]]:
        """
        Generate descriptions for multiple fields concurrently.

        Args:
            fields: List of field dictionaries
            batch_size: Number of fields to process concurrently (ignored, uses semaphore)

        Returns:
            List of (description, business_name) tuples
        """
        # Create tasks for all fields
        tasks = [
            self.generate_description(
                field["field_path"],
                field["field_name"],
                field["data_type"],
                field.get("semantic_type"),
                field.get("sample_values", []),
            )
            for field in fields
        ]

        # Execute all tasks concurrently (rate-limited by semaphore)
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing field {fields[i]['field_path']}: {result}")
                # Use fallback
                processed_results.append(
                    self._fallback_description(
                        fields[i]["field_name"],
                        fields[i]["data_type"],
                        fields[i].get("semantic_type"),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    def get_metrics(self) -> dict[str, Any]:
        """
        Get cost and usage metrics.

        Returns:
            Dictionary of metrics
        """
        return {
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "cached_requests": self.metrics.cached_requests,
            "total_tokens": self.metrics.total_tokens,
            "prompt_tokens": self.metrics.prompt_tokens,
            "completion_tokens": self.metrics.completion_tokens,
            "rate_limit_errors": self.metrics.rate_limit_errors,
            "timeout_errors": self.metrics.timeout_errors,
            "api_errors": self.metrics.api_errors,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "cache_evictions": self.metrics.cache_evictions,
            "cache_size": len(self._cache),
            "circuit_breaker_open": self._circuit_open,
        }

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics = CostMetrics()

    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        logger.info("OpenAI cache cleared")
