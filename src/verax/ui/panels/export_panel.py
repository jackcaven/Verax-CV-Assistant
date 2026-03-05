"""Export panel for output format selection and preview."""

import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Optional

import customtkinter as ctk

from verax.builder.factory import BuilderFactory
from verax.core.session import Session
from verax.ui.styles import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH_STANDARD,
    COLORS,
    FONT_HEADING,
    FONT_STANDARD,
    PADDING_LARGE,
    PADDING_STANDARD,
)
from verax.utils import get_logger

logger = get_logger(__name__)


class ExportPanel(ctk.CTkFrame):
    """Panel for exporting processed CVs."""

    def __init__(self, master: object, session: Session, **kwargs):  # type: ignore
        """Initialize export panel.

        Args:
            master: Parent widget
            session: Session instance
            **kwargs: Additional frame arguments
        """
        super().__init__(master, **kwargs)
        self.session = session
        self.export_dir: Path = Path.home() / "Documents"
        self.is_exporting = False
        self.export_thread: Optional[threading.Thread] = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and layout export panel widgets."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Export",
            font=FONT_HEADING,
            text_color=COLORS["text_primary"],
        )
        title.pack(pady=PADDING_LARGE, padx=PADDING_STANDARD)

        # Output directory section
        dir_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        dir_frame.pack(fill="x", padx=PADDING_LARGE, pady=PADDING_STANDARD)

        dir_label = ctk.CTkLabel(
            dir_frame,
            text="Output Directory:",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        dir_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.dir_path_label = ctk.CTkLabel(
            dir_frame,
            text=str(self.export_dir),
            font=("Arial", 9),
            text_color=COLORS["text_secondary"],
        )
        self.dir_path_label.pack(pady=5, padx=PADDING_STANDARD)

        browse_button = ctk.CTkButton(
            dir_frame,
            text="Browse",
            command=self._select_export_dir,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        )
        browse_button.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        # Format selection
        format_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        format_frame.pack(fill="x", padx=PADDING_LARGE, pady=PADDING_STANDARD)

        format_label = ctk.CTkLabel(
            format_frame,
            text="Output Formats:",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        format_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        formats_config = self.session.config.output_formats
        self.docx_var = ctk.BooleanVar(value=bool(formats_config))
        self.pdf_var = ctk.BooleanVar(value=False)
        self.html_var = ctk.BooleanVar(value=False)

        docx_check = ctk.CTkCheckBox(
            format_frame,
            text="DOCX",
            variable=self.docx_var,
        )
        docx_check.pack(anchor="w", padx=PADDING_STANDARD, pady=5)

        pdf_check = ctk.CTkCheckBox(
            format_frame,
            text="PDF",
            variable=self.pdf_var,
        )
        pdf_check.pack(anchor="w", padx=PADDING_STANDARD, pady=5)

        html_check = ctk.CTkCheckBox(
            format_frame,
            text="HTML (Preview)",
            variable=self.html_var,
        )
        html_check.pack(anchor="w", padx=PADDING_STANDARD, pady=5)

        # Info label
        info_label = ctk.CTkLabel(
            self,
            text="Ready to export processed CVs",
            font=("Arial", 9),
            text_color=COLORS["text_secondary"],
        )
        info_label.pack(pady=PADDING_LARGE)

        # Action buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=PADDING_LARGE)

        export_button = ctk.CTkButton(
            button_frame,
            text="Export",
            command=self._export,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["success"],
            hover_color="#00CC00",
        )
        export_button.pack(side="left", padx=PADDING_STANDARD)

        logger.debug("Export panel widgets created")

    def _select_export_dir(self) -> None:
        """Select output directory."""
        path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=str(self.export_dir),
        )
        if path:
            self.export_dir = Path(path)
            self.dir_path_label.configure(text=str(self.export_dir))
            logger.info(f"Export directory set to {self.export_dir}")

    def _export(self) -> None:
        """Export processed CVs."""
        if not any([self.docx_var.get(), self.pdf_var.get(), self.html_var.get()]):
            messagebox.showerror("Error", "Please select at least one output format.")
            return

        batch_results = self.session.get_batch_results()
        if not batch_results:
            msg = "No processed CVs to export. Please run batch processing first."
            messagebox.showerror("Error", msg)
            return

        self.is_exporting = True

        # Get selected formats
        formats = []
        if self.docx_var.get():
            formats.append("docx")
        if self.pdf_var.get():
            formats.append("pdf")
        if self.html_var.get():
            formats.append("html")

        # Start export in background thread
        self.export_thread = threading.Thread(
            target=self._export_worker,
            args=(batch_results, formats),
            daemon=False,
        )
        self.export_thread.start()
        logger.info(f"Starting export to {self.export_dir}")

    def _export_worker(self, batch_results: Dict, formats: List[str]) -> None:  # type: ignore
        """Background worker for exporting CVs."""
        try:
            success_count = 0
            error_count = 0
            template_schema = self.session.get_template_schema()

            if not template_schema:
                logger.error("Template schema not available for export")
                return

            # Ensure export directory exists
            self.export_dir.mkdir(parents=True, exist_ok=True)

            # Export each successfully processed CV
            for cv_filename, (cv_path, structured_cv, error) in batch_results.items():
                if error or not structured_cv:
                    logger.warning(f"Skipping {cv_filename} (processing failed)")
                    error_count += 1
                    continue

                try:
                    # Build each requested format
                    for format_name in formats:
                        # Check if format is available
                        if not BuilderFactory.is_available(format_name):
                            logger.warning(
                                f"Format {format_name} not available, skipping {cv_filename}"
                            )
                            continue

                        builder = BuilderFactory.create(format_name)

                        # Generate output filename
                        stem = cv_path.stem
                        output_path = self.export_dir / f"{stem}.{format_name}"

                        # Build output file
                        logger.debug(f"Building {format_name}: {output_path}")
                        builder.build(structured_cv, template_schema, output_path)
                        logger.info(f"Exported {cv_filename} as {format_name}")

                    success_count += 1

                except Exception as e:
                    logger.error(f"Export failed for {cv_filename}: {e}")
                    error_count += 1

            # Show summary
            summary = (
                f"Export complete!\n\n✓ {success_count} successful\n"
                f"✗ {error_count} failed\n\nFiles saved to:\n{self.export_dir}"
            )
            messagebox.showinfo("Export Complete", summary)
            logger.info(f"Export finished: {success_count} successful, {error_count} failed")

        except Exception as e:
            logger.error(f"Export process failed: {e}")
            messagebox.showerror("Error", f"Export failed:\n\n{str(e)}")
        finally:
            self.is_exporting = False

    def get_export_dir(self) -> Path:
        """Get selected export directory.

        Returns:
            Path to export directory.
        """
        return self.export_dir
