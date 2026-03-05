"""Extract template structure from PDF documents."""

from pathlib import Path
from statistics import median

import pdfplumber

from verax.models.template_schema import SectionTemplate, TemplateSchema
from verax.utils import get_logger

logger = get_logger(__name__)


class PdfTemplateExtractor:
    """Extract CV template structure from PDF files.

    PDF templates are used for structural reference only.
    The actual output is always DOCX-based (clone-and-fill).
    """

    def extract(self, file_path: Path) -> TemplateSchema:
        """Extract template structure from PDF file.

        Detects headings by font size (>1.15x median page font size).

        Args:
            file_path: Path to the PDF template file.

        Returns:
            TemplateSchema with detected sections.
                     source_format='pdf' indicates structural reference only.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is not a valid PDF.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with pdfplumber.open(file_path) as pdf:
                sections: list[SectionTemplate] = []
                order_index = 0

                # Analyze all pages to find font sizes
                all_font_sizes = []
                for page in pdf.pages:
                    for obj in page.chars:
                        if "size" in obj:
                            all_font_sizes.append(obj["size"])

                median_size = median(all_font_sizes) if all_font_sizes else 10

                # Extract headings (font size > 1.15x median)
                heading_threshold = median_size * 1.15
                found_headings = set()

                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue

                    # Group consecutive large-font characters into potential headings
                    for obj in page.chars:
                        if obj.get("size", 0) > heading_threshold:
                            char_text = obj.get("text", "").strip()
                            if char_text and char_text not in found_headings:
                                found_headings.add(char_text)

                # Create sections from found headings
                for heading_text in sorted(found_headings):
                    if heading_text and len(heading_text) > 2:  # Filter noise
                        section = SectionTemplate(
                            title=heading_text,
                            heading_style="PDF-Heading",
                            font_name="",
                            font_size=int(heading_threshold),
                            order_index=order_index,
                        )
                        sections.append(section)
                        order_index += 1
                        logger.debug(f"Detected PDF section: {heading_text}")

        except Exception as e:
            raise ValueError(f"Failed to parse PDF template: {e}")

        logger.info(f"Extracted {len(sections)} sections from {file_path.name}")
        logger.warning("PDF templates provide structural info only. Use DOCX for best fidelity.")

        return TemplateSchema(
            sections=sections,
            raw_docx_path=None,  # PDF is structural reference only
            source_format="pdf",
            contact_block_style="PDF-Contact",
        )
