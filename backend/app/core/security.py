"""
Security utilities for API key handling.
"""
from fastapi import Header, HTTPException, status


async def get_api_key(x_api_key: str = Header(None)) -> str:
    """
    Extract OpenRouter API key from request header.
    The key is never stored - only passed per-request.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Please provide X-API-Key header.",
        )
    return x_api_key


async def get_optional_api_key(x_api_key: str = Header(None)) -> str | None:
    """Extract optional API key from request header."""
    return x_api_key
