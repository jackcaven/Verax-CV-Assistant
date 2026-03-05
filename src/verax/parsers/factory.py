"""Factory for selecting document parsers by file type."""

from pathlib import Path

from verax.parsers.base import DocumentParser
from verax.utils import get_logger

logger = get_logger(__name__)


class ParserFactory:
    """Factory for creating document parsers based on file extension."""

    @staticmethod
    def create(file_path: Path) -> DocumentParser:
        """Create appropriate parser for file type.

        Args:
            file_path: Path to the document file.

        Returns:
            DocumentParser instance.

        Raises:
            ValueError: If file format is not supported.
        """
        suffix = file_path.suffix.lower()

        if suffix == ".docx":
            from verax.parsers.docx import DoxcParser
            logger.debug(f"Created DoxcParser for {file_path.name}")
            return DoxcParser()

        elif suffix == ".pdf":
            from verax.parsers.pdf import PdfParser
            logger.debug(f"Created PdfParser for {file_path.name}")
            return PdfParser()

        elif suffix == ".doc":
            from verax.parsers.doc import DocParser
            logger.debug(f"Created DocParser for {file_path.name}")
            return DocParser()

        else:
            raise ValueError(
                f"Unsupported file format: {suffix}. "
                f"Supported formats: .docx, .pdf, .doc"
            )
