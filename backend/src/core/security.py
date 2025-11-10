"""Security utilities for authentication and authorization."""
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from src.core.config import settings
from src.core.exceptions import AuthenticationError

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Returns:
        str: A cryptographically secure random API key
    """
    return secrets.token_urlsafe(32)


def verify_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    """
    Verify API key authentication.

    This is a basic implementation. In production, you should:
    - Store API keys securely in the database (hashed)
    - Associate keys with users/organizations
    - Implement key expiration and rotation
    - Add rate limiting per key

    Args:
        api_key: API key from request header

    Returns:
        str: Validated API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not settings.API_KEY_ENABLED:
        # API key authentication is disabled
        return "disabled"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # In production, validate against database
    # For now, we'll just check if it's not empty
    # TODO: Implement proper API key validation
    if not api_key or len(api_key) < 10:
        raise AuthenticationError("Invalid API key")

    return api_key


def get_current_user(api_key: str = Depends(verify_api_key)) -> str:
    """
    Get current authenticated user.

    In a full implementation, this would:
    - Look up the user associated with the API key
    - Return a User object
    - Handle user permissions and roles

    Args:
        api_key: Validated API key

    Returns:
        str: User identifier (placeholder)
    """
    # Placeholder implementation
    # TODO: Implement proper user management
    if api_key == "disabled":
        return "anonymous"
    return "authenticated_user"


# Dependency for optional authentication
def get_optional_user(api_key: str | None = Depends(api_key_header)) -> str | None:
    """
    Get current user if authenticated, None otherwise.

    Useful for endpoints that work with or without authentication.

    Args:
        api_key: Optional API key from request header

    Returns:
        Optional[str]: User identifier or None
    """
    if not settings.API_KEY_ENABLED or not api_key:
        return None

    try:
        return get_current_user(api_key)
    except (AuthenticationError, HTTPException):
        return None
