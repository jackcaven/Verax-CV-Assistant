"""Extract template structure from DOCX documents."""

from pathlib import Path
from docx import Document
from docx.shared import Pt

from verax.models.template_schema import SectionTemplate, TemplateSchema
from verax.utils import get_logger

logger = get_logger(__name__)


class DoxcTemplateExtractor:
    """Extract CV template structure from DOCX files."""

    def extract(self, file_path: Path) -> TemplateSchema:
        """Extract template structure from DOCX file.

        Detects section headings by:
        1. Style name (Heading 1, Heading 2, etc.)
        2. Heuristic: Bold + font size > 12pt

        Args:
            file_path: Path to the DOCX template file.

        Returns:
            TemplateSchema with detected sections.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is not a valid DOCX.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            doc = Document(file_path)
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX template: {e}")

        sections: list[SectionTemplate] = []
        order_index = 0

        for para in doc.paragraphs:
            heading_info = self._detect_heading(para)
            if heading_info:
                style_name, font_name, font_size = heading_info
                section = SectionTemplate(
                    title=para.text,
                    heading_style=style_name,
                    font_name=font_name,
                    font_size=font_size,
                    order_index=order_index,
                )
                sections.append(section)
                order_index += 1
                logger.debug(f"Detected section: {para.text} (style: {style_name})")

        logger.info(f"Extracted {len(sections)} sections from {file_path.name}")

        return TemplateSchema(
            sections=sections,
            raw_docx_path=str(file_path),
            source_format="docx",
            contact_block_style="Normal",
        )

    @staticmethod
    def _detect_heading(para) -> tuple[str, str, int] | None:
        """Detect if paragraph is a heading.

        Args:
            para: Paragraph object from python-docx.

        Returns:
            Tuple of (style_name, font_name, font_size) if heading, else None.
        """
        style_name = para.style.name if para.style else ""

        # Check for explicit Heading style
        if style_name.startswith("Heading"):
            font_name = ""
            font_size = 0
            if para.runs:
                run = para.runs[0]
                if run.font.name:
                    font_name = run.font.name
                if run.font.size:
                    font_size = int(run.font.size / Pt(1))
            return (style_name, font_name, font_size)

        # Heuristic: Bold + large font
        if not para.runs:
            return None

        is_bold = any(run.bold for run in para.runs)
        max_size = 0
        font_name = ""

        for run in para.runs:
            if run.font.size:
                font_size_pt = int(run.font.size / Pt(1))
                if font_size_pt > max_size:
                    max_size = font_size_pt
                    if run.font.name:
                        font_name = run.font.name

        if is_bold and max_size > 12:
            heuristic_style = f"Bold+Size{max_size}"
            return (heuristic_style, font_name, max_size)

        return None
