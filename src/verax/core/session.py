"""Session management for application state."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from verax.models.config import AppConfig
from verax.models.structured_cv import StructuredCV
from verax.models.template_schema import TemplateSchema
from verax.utils import get_logger

logger = get_logger(__name__)

# Type alias for batch processing results
BatchResults = Dict[str, Tuple[Path, Optional[StructuredCV], Optional[Exception]]]


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
        self.current_cv: Optional[StructuredCV] = None
        # Store batch processing results: {cv_filename: (cv_path, structured_cv, error)}
        self.batch_results: Dict[str, Tuple[Path, Optional[StructuredCV], Optional[Exception]]] = {}
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

    def set_current_cv(self, cv: StructuredCV) -> None:
        """Set current structured CV.

        Args:
            cv: StructuredCV instance
        """
        self.current_cv = cv
        logger.debug(f"Current CV set: {len(cv.sections)} sections")

    def get_current_cv(self) -> Optional[StructuredCV]:
        """Get current structured CV.

        Returns:
            StructuredCV or None if not set
        """
        return self.current_cv

    def set_batch_results(
        self,
        results: List[Tuple[Path, Optional[StructuredCV], Optional[Exception]]],
    ) -> None:
        """Store batch processing results.

        Args:
            results: List of (cv_path, structured_cv, error) tuples
        """
        self.batch_results.clear()
        for cv_path, structured_cv, error in results:
            self.batch_results[cv_path.name] = (cv_path, structured_cv, error)
        logger.debug(f"Batch results stored: {len(self.batch_results)} CVs")

    def get_batch_results(self) -> BatchResults:
        """Get batch processing results.

        Returns:
            Dictionary of {cv_filename: (cv_path, structured_cv, error)}
        """
        return self.batch_results
