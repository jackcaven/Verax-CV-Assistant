"""Process panel for unified CV template selection, batch processing, and export."""

import os
import platform
import subprocess
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, List, Optional

import customtkinter as ctk

from verax.builder.factory import BuilderFactory
from verax.core.batch_processor import BatchProcessor
from verax.core.session import Session
from verax.template.docx_extractor import DoxcTemplateExtractor
from verax.template.pdf_extractor import PdfTemplateExtractor
from verax.ui.styles import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH_STANDARD,
    COLORS,
    FONT_HEADING,
    FONT_STANDARD,
    PADDING_LARGE,
    PADDING_STANDARD,
    SUPPORTED_CV_FORMATS,
    SUPPORTED_TEMPLATE_FORMATS,
)
from verax.utils import get_logger

logger = get_logger(__name__)


class ProcessPanel(ctk.CTkFrame):
    """Unified panel for template selection, CV batch processing, and export."""

    def __init__(self, master: object, session: Session, **kwargs):  # type: ignore
        """Initialize process panel.

        Args:
            master: Parent widget
            session: Session instance
            **kwargs: Additional frame arguments
        """
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True)
        self.session = session

        self.template_path: Optional[Path] = None
        self.cv_files: List[Path] = []
        self.output_dir: Path = Path.home() / "Documents"
        self.is_processing = False
        self.processing_thread: Optional[threading.Thread] = None
        self.progress_lines: List[str] = []

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and layout process panel widgets."""
        # Scrollable container
        scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_container.pack(
            fill="both", expand=True, padx=PADDING_STANDARD, pady=PADDING_STANDARD
        )

        # Title
        title = ctk.CTkLabel(
            scroll_container,
            text="Process CVs",
            font=FONT_HEADING,
            text_color=COLORS["text_primary"],
        )
        title.pack(pady=PADDING_LARGE, padx=PADDING_STANDARD)

        # Template section
        template_frame = ctk.CTkFrame(scroll_container, fg_color=COLORS["bg_secondary"])
        template_frame.pack(fill="x", padx=PADDING_LARGE, pady=PADDING_STANDARD)

        template_label = ctk.CTkLabel(
            template_frame,
            text="Template CV (required)",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        template_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.template_display = ctk.CTkLabel(
            template_frame,
            text="No template selected",
            font=("Arial", 9),
            text_color=COLORS["text_secondary"],
        )
        self.template_display.pack(pady=5, padx=PADDING_STANDARD)

        template_button = ctk.CTkButton(
            template_frame,
            text="Browse",
            command=self._select_template,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        )
        template_button.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        # CVs section
        cvs_frame = ctk.CTkFrame(scroll_container, fg_color=COLORS["bg_secondary"])
        cvs_frame.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=PADDING_STANDARD)

        cvs_label = ctk.CTkLabel(
            cvs_frame,
            text="CVs to Process",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        cvs_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        # Scrollable frame for CV list with remove buttons
        self.cv_list_container = ctk.CTkScrollableFrame(
            cvs_frame, fg_color=COLORS["bg_primary"], height=150
        )
        self.cv_list_container.pack(
            fill="both",
            expand=True,
            padx=PADDING_STANDARD,
            pady=PADDING_STANDARD,
        )

        # Empty state label
        self.cv_empty_label = ctk.CTkLabel(
            self.cv_list_container,
            text="No CVs selected",
            font=("Arial", 9),
            text_color=COLORS["text_secondary"],
        )
        self.cv_empty_label.pack(pady=PADDING_STANDARD)

        # CV list buttons
        cv_button_frame = ctk.CTkFrame(cvs_frame, fg_color="transparent")
        cv_button_frame.pack(fill="x", padx=PADDING_STANDARD, pady=PADDING_STANDARD)

        add_cv_button = ctk.CTkButton(
            cv_button_frame,
            text="+ Add CVs",
            command=self._add_cvs,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        )
        add_cv_button.pack(side="left", padx=5)

        clear_cv_button = ctk.CTkButton(
            cv_button_frame,
            text="Clear All",
            command=self._clear_all_cvs,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["warning"],
            hover_color="#FF7700",
        )
        clear_cv_button.pack(side="left", padx=5)

        # Output folder section
        output_frame = ctk.CTkFrame(scroll_container, fg_color=COLORS["bg_secondary"])
        output_frame.pack(fill="x", padx=PADDING_LARGE, pady=PADDING_STANDARD)

        output_label = ctk.CTkLabel(
            output_frame,
            text="Output Folder",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        output_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.output_display = ctk.CTkLabel(
            output_frame,
            text=str(self.output_dir),
            font=("Arial", 8),
            text_color=COLORS["text_secondary"],
        )
        self.output_display.pack(pady=5, padx=PADDING_STANDARD)

        output_button = ctk.CTkButton(
            output_frame,
            text="Browse",
            command=self._select_output_dir,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        )
        output_button.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        # Progress log section
        log_frame = ctk.CTkFrame(scroll_container, fg_color=COLORS["bg_secondary"])
        log_frame.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=PADDING_STANDARD)

        log_label = ctk.CTkLabel(
            log_frame,
            text="Progress Log",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        log_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.progress_log = ctk.CTkTextbox(
            log_frame,
            height=150,
            fg_color=COLORS["bg_primary"],
            text_color=COLORS["text_primary"],
        )
        self.progress_log.pack(
            fill="both",
            expand=True,
            padx=PADDING_STANDARD,
            pady=PADDING_STANDARD,
        )
        self.progress_log.configure(state="disabled")

        # Action buttons
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=PADDING_LARGE)

        self.run_button = ctk.CTkButton(
            action_frame,
            text="Run Process",
            command=self._run_process,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["success"],
            hover_color="#00CC00",
            state="disabled",
        )
        self.run_button.pack(side="left", padx=PADDING_STANDARD)

        self.cancel_button = ctk.CTkButton(
            action_frame,
            text="Cancel",
            command=self._cancel_process,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["error"],
            hover_color="#BB0000",
            state="disabled",
        )
        self.cancel_button.pack(side="left", padx=PADDING_STANDARD)

        logger.debug("Process panel widgets created")

    def _select_template(self) -> None:
        """Open file dialog to select template file."""
        path = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=SUPPORTED_TEMPLATE_FORMATS,
            initialdir=self.session.get_last_cv_dir(),
        )
        if path:
            self.template_path = Path(path)
            self.template_display.configure(text=self.template_path.name)
            self.session.set_last_cv_dir(self.template_path.parent)
            logger.info(f"Template selected: {self.template_path}")
            self._update_run_button_state()

    def _add_cvs(self) -> None:
        """Add CV files to the batch list."""
        paths = filedialog.askopenfilenames(
            title="Select CV Files",
            filetypes=SUPPORTED_CV_FORMATS,
            initialdir=self.session.get_last_cv_dir(),
        )
        if paths:
            for path in paths:
                p = Path(path)
                if p not in self.cv_files:
                    self.cv_files.append(p)
                    self.session.set_last_cv_dir(p.parent)
            self._refresh_cv_list()
            logger.info(f"Added {len(paths)} CV(s)")
            self._update_run_button_state()

    def _clear_all_cvs(self) -> None:
        """Clear all CVs from the list."""
        self.cv_files.clear()
        self._refresh_cv_list()
        logger.info("Cleared CV list")
        self._update_run_button_state()

    def _refresh_cv_list(self) -> None:
        """Refresh the CV list display."""
        # Clear container
        for widget in self.cv_list_container.winfo_children():
            widget.destroy()

        if not self.cv_files:
            self.cv_empty_label.pack(pady=PADDING_STANDARD)
        else:
            for i, cv_path in enumerate(self.cv_files):
                row_frame = ctk.CTkFrame(self.cv_list_container, fg_color="transparent")
                row_frame.pack(fill="x", padx=PADDING_STANDARD, pady=3)

                # Filename label
                filename_label = ctk.CTkLabel(
                    row_frame,
                    text=cv_path.name,
                    font=("Arial", 9),
                    text_color=COLORS["text_primary"],
                    anchor="w",
                )
                filename_label.pack(side="left", fill="x", expand=True)

                # Remove button
                remove_button = ctk.CTkButton(
                    row_frame,
                    text="×",
                    command=lambda idx=i: self._remove_cv(idx),
                    height=25,
                    width=30,
                    fg_color=COLORS["error"],
                    hover_color="#BB0000",
                    font=("Arial", 12),
                )
                remove_button.pack(side="right", padx=5)

    def _remove_cv(self, index: int) -> None:
        """Remove a CV from the list by index."""
        if 0 <= index < len(self.cv_files):
            removed = self.cv_files.pop(index)
            logger.info(f"Removed CV: {removed.name}")
            self._refresh_cv_list()
            self._update_run_button_state()

    def _select_output_dir(self) -> None:
        """Open directory dialog to select output folder."""
        path = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=self.output_dir,
        )
        if path:
            self.output_dir = Path(path)
            self.output_display.configure(text=str(self.output_dir))
            logger.info(f"Output directory set to: {self.output_dir}")

    def _update_run_button_state(self) -> None:
        """Update Run button state based on template and CV selection."""
        enabled = self.template_path is not None and len(self.cv_files) > 0
        state = "normal" if enabled else "disabled"
        self.run_button.configure(state=state)

    def _run_process(self) -> None:
        """Start the CV processing pipeline."""
        if not self.template_path or not self.cv_files:
            messagebox.showerror("Error", "Please select a template and at least one CV.")
            return

        self.is_processing = True
        self.run_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")

        # Clear progress log
        self.progress_lines = []
        self._append_progress("Starting processing...\n")

        # Start processing in background thread
        self.processing_thread = threading.Thread(
            target=self._process_worker,
            daemon=False,
        )
        self.processing_thread.start()
        logger.info(f"Starting processing for {len(self.cv_files)} CV(s)")

    def _process_worker(self) -> None:
        """Background worker for CV processing."""
        try:
            # Step 1: Extract template schema
            self._append_progress(f"Extracting template from {self.template_path.name}...\n")
            template_schema = self._extract_template(self.template_path)
            self._append_progress(
                f"Template extracted: {len(template_schema.sections)} sections\n\n"
            )
            self.session.set_template(self.template_path, template_schema)

            # Step 2: Process batch
            self._append_progress(f"Processing {len(self.cv_files)} CV file(s)...\n")
            batch_processor = BatchProcessor(self.session.config)
            results = batch_processor.process_batch(
                self.cv_files,
                template_schema,
                progress_callback=None,  # Progress via event queue
            )

            # Step 3: Build outputs
            self._append_progress("Building outputs...\n")
            success_count = 0
            error_count = 0

            for cv_path, structured_cv, error in results:
                if error:
                    self._append_progress(f"✗ {cv_path.name}: {str(error)[:60]}\n")
                    error_count += 1
                else:
                    try:
                        # Get selected output formats from config
                        for output_format in self.session.config.output_formats:
                            builder = BuilderFactory.create(output_format.value)
                            if builder and BuilderFactory.is_available(output_format.value):
                                output_path = self.output_dir / cv_path.stem
                                builder.build(structured_cv, template_schema, output_path)
                        self._append_progress(f"✓ {cv_path.name}\n")
                        success_count += 1
                    except Exception as build_err:
                        self._append_progress(f"✗ {cv_path.name}: {str(build_err)[:60]}\n")
                        error_count += 1

            # Step 4: Show summary
            self._append_progress("\n--- Complete ---\n")
            self._append_progress(f"Success: {success_count}/{len(self.cv_files)}\n")
            self.session.set_batch_results(results)
            logger.info(f"Processing complete: {success_count}/{len(self.cv_files)} successful")

            # Show completion popup
            summary_msg = (
                f"Processing complete!\n\n"
                f"Success: {success_count}/{len(self.cv_files)}\n"
                f"Errors: {error_count}/{len(self.cv_files)}\n\n"
                f"Output saved to:\n{self.output_dir}"
            )
            messagebox.showinfo("Processing Complete", summary_msg)

            # Open output folder
            self._open_output_folder()

        except Exception as e:
            self._append_progress(f"\nError: {str(e)}\n")
            logger.error(f"Processing failed: {e}")
            messagebox.showerror("Processing Error", f"Failed to process CVs:\n\n{str(e)}")

        finally:
            self.is_processing = False
            self.run_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")

    def _extract_template(self, template_path: Path) -> Any:
        """Extract template schema from file.

        Args:
            template_path: Path to template file

        Returns:
            TemplateSchema instance

        Raises:
            ValueError: If extraction fails
        """
        suffix = template_path.suffix.lower()
        if suffix == ".docx":
            extractor = DoxcTemplateExtractor()
            return extractor.extract(template_path)
        elif suffix == ".pdf":
            extractor = PdfTemplateExtractor()  # type: ignore
            return extractor.extract(template_path)
        else:
            raise ValueError(f"Unsupported template format: {suffix}")

    def _append_progress(self, text: str) -> None:
        """Append text to progress log.

        Args:
            text: Text to append
        """
        self.progress_lines.append(text)
        self.progress_log.configure(state="normal")
        self.progress_log.insert("end", text)
        self.progress_log.see("end")
        self.progress_log.configure(state="disabled")

    def _cancel_process(self) -> None:
        """Cancel ongoing processing."""
        if self.is_processing:
            self.is_processing = False
            self.cancel_button.configure(state="disabled")
            logger.info("Processing cancellation requested")
            messagebox.showinfo("Info", "Cancellation requested. Waiting for current tasks...")

    def _open_output_folder(self) -> None:
        """Open the output folder in file explorer."""
        try:
            if not self.output_dir.exists():
                self.output_dir.mkdir(parents=True, exist_ok=True)

            if platform.system() == "Windows":
                os.startfile(self.output_dir)  # type: ignore
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(self.output_dir)], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(self.output_dir)], check=True)
        except Exception as e:
            logger.error(f"Failed to open output folder: {e}")

    def update_progress(self, event: Any) -> None:  # type: ignore
        """Update progress display from event queue.

        Args:
            event: ProgressEvent from the queue
        """
        # Optionally update progress log with detailed events
        if hasattr(event, "stage"):
            text = f"{event.cv_filename}: {event.stage} ({event.percent}%)\n"
            self._append_progress(text)
