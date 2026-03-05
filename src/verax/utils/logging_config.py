"""Structured logging configuration for Verax."""

import logging
import sys
from pathlib import Path
import platformdirs


def setup_logging(debug: bool = False) -> None:
    """Configure logging for the application.

    Logs are written to:
    - Console (INFO level or DEBUG if debug=True)
    - Log file in platformdirs user_log_path

    Args:
        debug: If True, set console level to DEBUG.
    """
    log_dir = Path(platformdirs.user_log_dir("verax", "verax"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "verax.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    root_logger.info(f"Logging started. Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.

    Args:
        name: Usually __name__ from the calling module.

    Returns:
        A logger instance.
    """
    return logging.getLogger(name)
