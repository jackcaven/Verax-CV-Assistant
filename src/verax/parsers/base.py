"""Abstract base for document parsers."""

from pathlib import Path
from typing import Protocol

from verax.parsers.models import RawDocument


class DocumentParser(Protocol):
    """Contract for document parsing.

    Implementations parse documents in various formats (DOCX, PDF, .doc)
    and return plain text.
    """

    def parse(self, file_path: Path) -> RawDocument:
        """Parse a document file and extract plain text.

        Args:
            file_path: Path to the document file.

        Returns:
            RawDocument with extracted text and metadata.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file format is not supported or parsing fails.
        """
        ...
