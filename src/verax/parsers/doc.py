"""Parser for legacy .doc documents."""

from pathlib import Path

import mammoth

from verax.parsers.models import RawDocument
from verax.utils import get_logger

logger = get_logger(__name__)


class DocParser:
    """Parser for legacy .doc documents using mammoth."""

    def parse(self, file_path: Path) -> RawDocument:
        """Parse .doc file and extract plain text.

        Legacy .doc files (OLE2 format) are converted to plain text using mammoth.
        This is a graceful fallback; users should prefer .docx.

        Args:
            file_path: Path to the .doc file.

        Returns:
            RawDocument with extracted text.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is not a valid .doc.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "rb") as f:
                result = mammoth.extract_text(f)
                text = result.value
        except Exception as e:
            raise ValueError(f"Failed to parse .doc file: {e}")

        logger.debug(f"Parsed .doc: {file_path.name}, {len(text)} chars")
        logger.warning(
            "Legacy .doc format detected. Consider using .docx for better compatibility."
        )

        return RawDocument(
            text=text,
            source_filename=file_path.name,
            source_format="doc",
        )
