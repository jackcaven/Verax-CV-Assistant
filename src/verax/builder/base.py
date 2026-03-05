"""Base abstraction for output builders."""

from pathlib import Path
from typing import Protocol

from verax.models.structured_cv import StructuredCV
from verax.models.template_schema import TemplateSchema


class OutputBuilder(Protocol):
    """Contract for building CV output in various formats."""

    name: str  # "docx", "pdf", "html"

    def build(
        self,
        cv: StructuredCV,
        template_schema: TemplateSchema,
        output_path: Path,
    ) -> None:
        """Build and write CV to output file.

        Args:
            cv: Structured CV data
            template_schema: Template structure with section mapping
            output_path: Path where output file should be written

        Raises:
            ValueError: If build fails (missing data, invalid template, etc.)
            IOError: If file write fails
        """
        ...
