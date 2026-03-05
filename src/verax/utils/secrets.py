"""Secrets management using OS keyring and environment variables."""

import os
from typing import Optional

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

from verax.utils.logging_config import get_logger

logger = get_logger(__name__)

SERVICE_NAME = "verax"


def get_api_key(provider: str) -> Optional[str]:
    """Get API key from environment or OS keyring.

    Search order:
    1. Environment variable (PROVIDER_API_KEY in uppercase)
    2. OS keyring (if available)
    3. None if not found

    Args:
        provider: Provider name (e.g., "openai", "anthropic")

    Returns:
        API key if found, None otherwise
    """
    env_var = f"{provider.upper()}_API_KEY"

    # 1. Check environment
    if key := os.getenv(env_var):
        logger.debug(f"Found {provider} API key in environment")
        return key

    # 2. Check keyring (if available)
    if KEYRING_AVAILABLE:
        try:
            if key := keyring.get_password(SERVICE_NAME, provider):
                logger.debug(f"Found {provider} API key in keyring")
                return key
        except Exception as e:
            logger.warning(f"Failed to retrieve key from keyring: {e}")

    logger.debug(f"No API key found for {provider}")
    return None


def set_api_key(provider: str, key: str) -> bool:
    """Store API key in OS keyring.

    Args:
        provider: Provider name (e.g., "openai", "anthropic")
        key: API key to store

    Returns:
        True if successful, False if keyring unavailable

    Raises:
        ValueError: If key is empty
    """
    if not key:
        raise ValueError("API key cannot be empty")

    if not KEYRING_AVAILABLE:
        logger.warning("keyring not available; cannot store API key securely")
        return False

    try:
        keyring.set_password(SERVICE_NAME, provider, key)
        logger.info(f"Stored {provider} API key in keyring")
        return True
    except Exception as e:
        logger.error(f"Failed to store key in keyring: {e}")
        return False


def delete_api_key(provider: str) -> bool:
    """Delete API key from OS keyring.

    Args:
        provider: Provider name (e.g., "openai", "anthropic")

    Returns:
        True if successful, False if keyring unavailable or key not found
    """
    if not KEYRING_AVAILABLE:
        logger.warning("keyring not available; cannot delete API key")
        return False

    try:
        keyring.delete_password(SERVICE_NAME, provider)
        logger.info(f"Deleted {provider} API key from keyring")
        return True
    except Exception as e:
        logger.debug(f"Failed to delete key from keyring: {e}")
        return False
