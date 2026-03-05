"""Factory for creating output builders by format."""

from typing import Literal

from verax.utils import get_logger

logger = get_logger(__name__)


class BuilderFactory:
    """Factory for creating output builders."""

    @staticmethod
    def create(format_name: str) -> "OutputBuilder":  # type: ignore
        """Create an output builder by format name.

        Args:
            format_name: Output format ("docx", "pdf", "html")

        Returns:
            OutputBuilder implementation instance

        Raises:
            ValueError: If format is not supported
        """
        format_lower = format_name.lower().strip()

        if format_lower == "docx":
            from verax.builder.docx_builder import DocxBuilder
            return DocxBuilder()

        elif format_lower == "pdf":
            from verax.builder.pdf_builder import PdfBuilder
            return PdfBuilder()

        elif format_lower == "html":
            from verax.builder.html_builder import HtmlBuilder
            return HtmlBuilder()

        else:
            raise ValueError(f"Unsupported output format: {format_name}")

    @staticmethod
    def get_supported_formats() -> list[str]:
        """Get list of supported output formats.

        Returns:
            List of format names
        """
        return ["docx", "pdf", "html"]

    @staticmethod
    def is_available(format_name: str) -> bool:
        """Check if a format is available (dependencies installed/configured).

        Args:
            format_name: Output format to check

        Returns:
            True if format is available, False otherwise
        """
        format_lower = format_name.lower().strip()

        if format_lower in ["docx", "html"]:
            return True

        elif format_lower == "pdf":
            # PDF requires LibreOffice; check if available
            from verax.builder.pdf_builder import detect_libreoffice
            return detect_libreoffice() is not None

        else:
            return False
