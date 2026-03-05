"""Utilities for Verax."""

from verax.utils.logging_config import get_logger, setup_logging
from verax.utils.events import emit_progress, ProgressEvent, clear_queue
from verax.utils.file_utils import (
    get_supported_extensions,
    is_supported_file,
    safe_copy,
    ensure_dir,
)
from verax.utils.secrets import get_api_key, set_api_key, delete_api_key

__all__ = [
    "get_logger",
    "setup_logging",
    "emit_progress",
    "ProgressEvent",
    "clear_queue",
    "get_supported_extensions",
    "is_supported_file",
    "safe_copy",
    "ensure_dir",
    "get_api_key",
    "set_api_key",
    "delete_api_key",
]
