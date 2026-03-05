"""Session management for application state."""

from pathlib import Path
from typing import Optional

from verax.models.template_schema import TemplateSchema
from verax.models.config import AppConfig
from verax.utils import get_logger

logger = get_logger(__name__)


class Session:
    """Maintains application state across operations."""

    def __init__(self, config: AppConfig):
        """Initialize session.

        Args:
            config: AppConfig instance
        """
        self.config = config
        self.current_template_path: Optional[Path] = None
        self.current_template_schema: Optional[TemplateSchema] = None
        self.last_cv_dir: Optional[Path] = None
        logger.info("Session initialized")

    def set_template(self, template_path: Path, schema: TemplateSchema) -> None:
        """Set current template.

        Args:
            template_path: Path to template file
            schema: Extracted TemplateSchema
        """
        self.current_template_path = template_path
        self.current_template_schema = schema
        logger.info(f"Template set: {template_path.name}, {len(schema.sections)} sections")

    def get_template_schema(self) -> Optional[TemplateSchema]:
        """Get current template schema.

        Returns:
            TemplateSchema or None if not set
        """
        return self.current_template_schema

    def set_last_cv_dir(self, path: Path) -> None:
        """Remember last CV directory for UI.

        Args:
            path: Directory path
        """
        self.last_cv_dir = path
        logger.debug(f"Last CV dir: {path}")

    def get_last_cv_dir(self) -> Optional[Path]:
        """Get last CV directory.

        Returns:
            Path or None
        """
        return self.last_cv_dir
