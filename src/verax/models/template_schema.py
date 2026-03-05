"""Template structure detection and representation."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SectionTemplate:
    """Template structure for a single CV section.

    Represents a section as detected or configured from a template document.

    Attributes:
        title: Section heading text as it appears in the template
        heading_style: Style name (e.g., "Heading 1") or heuristic name (e.g., "Bold+Size>12")
        font_name: Font name from the template (e.g., "Calibri")
        font_size: Font size in points (e.g., 14)
        order_index: Position of this section in the template (0-based)
    """

    title: str
    heading_style: str = ""
    font_name: str = ""
    font_size: int = 0
    order_index: int = 0


@dataclass(frozen=True)
class TemplateSchema:
    """Detected or configured structure of a CV template.

    Represents the sections, headings, and style information extracted from
    a template document (DOCX or PDF).

    Attributes:
        sections: List of detected or configured section templates in order
        raw_docx_path: Path to original DOCX file (used for clone-and-fill rebuilding)
                       None if template is PDF or synthetic
        source_format: "docx" or "pdf" — indicates template source type
                       PDF templates are structural references only; output is DOCX
        contact_block_style: Style hint for contact info section (heading style or font)
    """

    sections: List[SectionTemplate] = field(default_factory=list)
    raw_docx_path: Optional[str] = None
    source_format: str = "docx"
    contact_block_style: str = ""
