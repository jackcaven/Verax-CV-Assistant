"""Abstract base for LLM providers."""

from typing import Optional, Protocol

from verax.models.structured_cv import StructuredCV
from verax.models.template_schema import TemplateSchema


class LLMProvider(Protocol):
    """Contract for LLM-based CV processing.

    All LLM interactions go through this abstraction.
    Implementations: OpenAI, Anthropic, Local (heuristic).
    """

    name: str  # "openai", "anthropic", or "local"
    supports_local: bool  # Can run without API keys

    def extract_structured_cv(self, raw_text: str, original_filename: str = "") -> StructuredCV:
        """Parse raw CV text into StructuredCV with automatic section detection.

        Args:
            raw_text: Plain text content from parsed document
            original_filename: Original file name for audit trail

        Returns:
            StructuredCV with contact info and sections detected by LLM

        Raises:
            ValueError: If parsing fails or LLM response is invalid
        """
        ...

    def map_sections(
        self,
        cv: StructuredCV,
        template_schema: TemplateSchema,
    ) -> StructuredCV:
        """Reassign CV sections to match template structure.

        Takes extracted CV and reorders/remaps sections to match
        the template's section list.

        Args:
            cv: StructuredCV to remap
            template_schema: Target template structure

        Returns:
            StructuredCV with sections reordered to match template

        Raises:
            ValueError: If mapping fails
        """
        ...

    def enhance_text(
        self,
        cv: StructuredCV,
        style_guide: Optional[str] = None,
    ) -> StructuredCV:
        """Polish CV text: improve clarity, expand bullets, enhance impact.

        Optional step for text improvement. Local provider returns cv unchanged.

        Args:
            cv: StructuredCV to enhance
            style_guide: Optional style/tone guide for enhancement

        Returns:
            StructuredCV with improved text

        Raises:
            ValueError: If enhancement fails
        """
        ...
