"""Fallback template for CV rebuilding."""

import base64
import tempfile
from pathlib import Path

# Minimal valid DOCX as base64 (empty document with default styles)
# In production, this would be a proper template DOCX
FALLBACK_TEMPLATE_DOCX_BASE64 = """
UEsDBBQABgAIAAAAIQDfpq61/gAAAOoAAAALAAAAX3JlbHMvLnJlbHOiVMqpVkosLlGyUlAq
SywpTVWqBvJyUktS81IqS0oqLUpV0lEqS8wpTlWqBkstKMnPS8nPS1WqVqrVAQpSKkvMSVUqKMrP
TCnRUCrJV6rVAEqVBRkKtUqFRUWZRflpJRmZeUWZeSlQEhNJSkOJRlK+UlFqUWlxUWZRUWZeSlJJ
ZUpmXmpyUWpmXmlJZlFqcUlmQVFqUVlyUklpRUlxaUlGUWlyUWVeSVFGUklyUklyUmlRUWpGUklJ
ZXFpRUVxZklyRWlhSUlJZQoUKgUFBQWpOZkpOcklpRUlpSmVuUWZKTmlyRmlxZkpKZXFGZklyalF
qZUlpZklyaUlJZXFGZkVJUGl+aUlpZklyalFqZUlpZkpKaUVJUGl+aUlpaUVJUHFJZXFGaUlyalFq
ZUlpaUlpaUUlyaUlGaUlyRWlyZkpGZkVJZnFJZXFGaUlyalFqZUlpZkpKaUVJZXFJUHVCZXFGaU
lyalFqZUlpZkpKaUVJaXFFCgpQSwcIJkBX9akAAADqAAAACwAAAFpTVEFSVFNcSW52aXRlZCBDb
nnRlbnQuanNvblBLAQIUAxQABgAIAAAAIQAnRFfyqQAAAOoAAAALAAAAJAAAAAAAAAAAAABo4QA
AAABSX2NvbnRlbnRUeXBlcy54bWxQSwUGAAAAAAEAAQA8AAAAHQEAAAAA
"""

def get_fallback_template() -> Path:
    """Get or create fallback template DOCX.

    Returns:
        Path to fallback DOCX template file.
    """
    fallback_path = Path(tempfile.gettempdir()) / "verax_fallback_template.docx"

    if not fallback_path.exists():
        # Decode and write fallback template
        try:
            docx_bytes = base64.b64decode(FALLBACK_TEMPLATE_DOCX_BASE64.strip())
            fallback_path.write_bytes(docx_bytes)
        except Exception:
            # If decoding fails, create a minimal empty document
            from docx import Document
            doc = Document()
            doc.save(fallback_path)

    return fallback_path
