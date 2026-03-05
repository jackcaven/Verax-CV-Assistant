"""PDF builder via LibreOffice conversion."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from verax.models.structured_cv import StructuredCV
from verax.models.template_schema import TemplateSchema
from verax.builder.docx_builder import DocxBuilder
from verax.utils import get_logger

logger = get_logger(__name__)


def detect_libreoffice() -> Optional[Path]:
    """Detect LibreOffice soffice binary in system PATH.

    Tries common installation paths on different OSes.

    Returns:
        Path to soffice executable if found, None otherwise
    """
    # Candidates in order of preference
    candidates = [
        "soffice",  # Unix/Linux PATH
        "/usr/bin/soffice",  # Linux
        "/usr/local/bin/soffice",  # macOS Homebrew
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
        "C:\\Program Files\\LibreOffice\\program\\soffice.exe",  # Windows
        "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe",  # Windows 32-bit
    ]

    for candidate in candidates:
        if shutil.which(candidate):
            logger.debug(f"Found LibreOffice: {candidate}")
            return Path(candidate)

    logger.warning("LibreOffice soffice binary not found")
    return None


class PdfBuilder:
    """Build PDF output by converting DOCX via LibreOffice.

    Process:
    1. Use DocxBuilder to create intermediate DOCX
    2. Convert DOCX to PDF via LibreOffice headless
    3. Clean up intermediate DOCX
    """

    name = "pdf"

    def build(
        self,
        cv: StructuredCV,
        template_schema: TemplateSchema,
        output_path: Path,
    ) -> None:
        """Build PDF by DOCX conversion.

        Args:
            cv: Structured CV to write
            template_schema: Template structure
            output_path: Where to save the PDF file

        Raises:
            ValueError: If LibreOffice not available or conversion fails
            IOError: If file operations fail
        """
        logger.info(f"Building PDF for {cv.source_filename} -> {output_path}")

        # Check LibreOffice availability
        soffice_path = detect_libreoffice()
        if not soffice_path:
            raise ValueError(
                "LibreOffice not found. PDF export requires LibreOffice to be installed. "
                "Install from https://www.libreoffice.org/ or disable PDF format in settings."
            )

        # Create intermediate DOCX
        docx_path = output_path.with_suffix(".docx")
        try:
            docx_builder = DocxBuilder()
            docx_builder.build(cv, template_schema, docx_path)
            logger.debug(f"Created intermediate DOCX: {docx_path}")
        except Exception as e:
            raise ValueError(f"Failed to create intermediate DOCX: {e}")

        # Convert DOCX to PDF via LibreOffice
        try:
            self._convert_to_pdf(soffice_path, docx_path, output_path)
            logger.info(f"PDF saved: {output_path}")
        except Exception as e:
            logger.error(f"PDF conversion failed: {e}")
            raise
        finally:
            # Clean up intermediate DOCX
            if docx_path.exists():
                try:
                    docx_path.unlink()
                    logger.debug(f"Cleaned up intermediate DOCX")
                except Exception as e:
                    logger.warning(f"Failed to clean up {docx_path}: {e}")

    @staticmethod
    def _convert_to_pdf(soffice_path: Path, docx_path: Path, output_path: Path) -> None:
        """Convert DOCX to PDF using LibreOffice.

        Args:
            soffice_path: Path to soffice executable
            docx_path: Path to input DOCX file
            output_path: Path where PDF should be saved

        Raises:
            subprocess.CalledProcessError: If conversion fails
        """
        output_dir = output_path.parent

        try:
            # LibreOffice headless conversion
            # Note: --outdir must be an existing directory
            cmd = [
                str(soffice_path),
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(output_dir),
                str(docx_path),
            ]

            logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )

            logger.debug(f"LibreOffice output: {result.stdout}")

            # LibreOffice creates PDF with same name as input (minus extension)
            temp_pdf_path = docx_path.with_suffix(".pdf")
            if temp_pdf_path.exists() and temp_pdf_path != output_path:
                shutil.move(str(temp_pdf_path), str(output_path))
                logger.debug(f"Moved PDF from {temp_pdf_path} to {output_path}")

        except subprocess.TimeoutExpired:
            raise ValueError("PDF conversion timed out (> 30 seconds)")
        except subprocess.CalledProcessError as e:
            raise ValueError(f"LibreOffice conversion failed: {e.stderr}")
        except FileNotFoundError:
            raise ValueError(f"LibreOffice binary not found: {soffice_path}")
