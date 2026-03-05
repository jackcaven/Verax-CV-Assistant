"""Template extraction and handling for Verax."""

from verax.template.docx_extractor import DoxcTemplateExtractor
from verax.template.fallback import get_fallback_template
from verax.template.pdf_extractor import PdfTemplateExtractor

__all__ = ["DoxcTemplateExtractor", "PdfTemplateExtractor", "get_fallback_template"]
