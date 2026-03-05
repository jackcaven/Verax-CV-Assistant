"""Configuration persistence and loading."""

import json
from pathlib import Path

import platformdirs

from verax.models.config import AppConfig
from verax.utils import get_logger

logger = get_logger(__name__)


def get_config_path() -> Path:
    """Get the configuration file path.

    Returns platform-appropriate config directory.

    Returns:
        Path to config.json file
    """
    config_dir = Path(platformdirs.user_config_dir("verax"))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def load_config() -> AppConfig:
    """Load AppConfig from disk, or return defaults if missing.

    Returns:
        AppConfig instance loaded from disk or defaults
    """
    config_path = get_config_path()

    if not config_path.exists():
        logger.debug(f"Config file not found at {config_path}, using defaults")
        return AppConfig()

    try:
        with config_path.open("r") as f:
            data = json.load(f)
        config = AppConfig.from_dict(data)
        logger.info(f"Loaded config from {config_path}")
        return config
    except Exception as e:
        logger.warning(f"Failed to load config from {config_path}: {e}, using defaults")
        return AppConfig()


def save_config(config: AppConfig) -> None:
    """Save AppConfig to disk.

    Args:
        config: AppConfig instance to save

    Raises:
        Exception: If save fails
    """
    config_path = get_config_path()

    try:
        with config_path.open("w") as f:
            json.dump(config.to_dict(), f, indent=2)
        logger.info(f"Saved config to {config_path}")
    except Exception as e:
        logger.error(f"Failed to save config to {config_path}: {e}")
        raise
