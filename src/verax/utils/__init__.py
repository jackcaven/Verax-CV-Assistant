"""Utilities for Verax."""

from verax.utils.config_manager import get_config_path, load_config, save_config
from verax.utils.events import ProgressEvent, clear_queue, emit_progress
from verax.utils.file_utils import (
    ensure_dir,
    get_supported_extensions,
    is_supported_file,
    safe_copy,
)
from verax.utils.logging_config import get_logger, setup_logging
from verax.utils.secrets import delete_api_key, get_api_key, set_api_key

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
    "load_config",
    "save_config",
    "get_config_path",
]
