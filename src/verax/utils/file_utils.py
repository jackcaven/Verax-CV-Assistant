"""File utility functions for Verax."""

import shutil
from pathlib import Path
from typing import Set

from verax.utils import get_logger

logger = get_logger(__name__)

# Supported file extensions
SUPPORTED_EXTENSIONS: Set[str] = {".docx", ".pdf", ".doc"}


def get_supported_extensions() -> Set[str]:
    """Get set of supported file extensions.

    Returns:
        Set of supported extensions (lowercase, with dots)
    """
    return SUPPORTED_EXTENSIONS.copy()


def is_supported_file(path: Path) -> bool:
    """Check if a file has a supported extension.

    Args:
        path: Path to file

    Returns:
        True if file extension is supported, False otherwise
    """
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def safe_copy(src: Path, dst: Path) -> Path:
    """Safely copy a file with error logging.

    Args:
        src: Source file path
        dst: Destination file path

    Returns:
        Destination path

    Raises:
        OSError: If copy fails
    """
    try:
        logger.debug(f"Copying {src} to {dst}")
        shutil.copy2(src, dst)
        logger.debug(f"Successfully copied {src.name} to {dst.name}")
        return dst
    except OSError as e:
        logger.error(f"Failed to copy {src} to {dst}: {e}")
        raise


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        The directory path

    Raises:
        OSError: If directory creation fails
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {path}")
        return path
    except OSError as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise
