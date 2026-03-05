"""Parser for PDF documents."""

from pathlib import Path

import pdfplumber

from verax.parsers.models import RawDocument
from verax.utils import get_logger

logger = get_logger(__name__)


class PdfParser:
    """Parser for PDF documents using pdfplumber."""

    def parse(self, file_path: Path) -> RawDocument:
        """Parse PDF file and extract plain text.

        Extracts text from all pages in order.

        Args:
            file_path: Path to the PDF file.

        Returns:
            RawDocument with extracted text.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is not a valid PDF.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        text_parts: list[str] = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(page_text)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF file: {e}")

        full_text = "\n".join(text_parts)
        logger.debug(f"Parsed PDF: {file_path.name}, {len(full_text)} chars")

        return RawDocument(
            text=full_text,
            source_filename=file_path.name,
            source_format="pdf",
        )
