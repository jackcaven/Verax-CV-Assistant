"""Data models for document parsing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RawDocument:
    """Plain text extracted from a document.

    Represents the output of a document parser before LLM processing.

    Attributes:
        text: Plain text content extracted from the document
        source_filename: Original file name for audit trail
        source_format: File format (docx, pdf, doc)
    """

    text: str
    source_filename: str
    source_format: str
