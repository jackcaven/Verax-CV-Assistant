"""Batch processing panel for managing multiple CVs and progress."""

import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Optional

import customtkinter as ctk

from verax.core.batch_processor import BatchProcessor
from verax.core.session import Session
from verax.ui.styles import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH_STANDARD,
    COLORS,
    FONT_HEADING,
    FONT_STANDARD,
    PADDING_LARGE,
    PADDING_STANDARD,
    SUPPORTED_CV_FORMATS,
)
from verax.utils import get_logger

logger = get_logger(__name__)


class BatchPanel(ctk.CTkFrame):
    """Panel for batch processing multiple CVs."""

    def __init__(self, master: object, session: Session, **kwargs):  # type: ignore
        """Initialize batch panel.

        Args:
            master: Parent widget
            session: Session instance
            **kwargs: Additional frame arguments
        """
        super().__init__(master, **kwargs)
        self.session = session
        self.cv_files: List[Path] = []
        self.progress_dict: Dict[str, int] = {}  # filename -> percent
        self.is_processing = False
        self.processing_thread: Optional[threading.Thread] = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and layout batch panel widgets."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Batch Process CVs",
            font=FONT_HEADING,
            text_color=COLORS["text_primary"],
        )
        title.pack(pady=PADDING_LARGE, padx=PADDING_STANDARD)

        # File list section
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=PADDING_STANDARD)

        list_label = ctk.CTkLabel(
            list_frame,
            text="CV Files to Process:",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        list_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        # Scrollable text widget for file list
        self.file_list = ctk.CTkTextbox(
            list_frame,
            height=150,
            fg_color=COLORS["bg_secondary"],
            text_color=COLORS["text_primary"],
        )
        self.file_list.pack(fill="both", expand=True, padx=PADDING_STANDARD, pady=PADDING_STANDARD)
        self.file_list.configure(state="disabled")

        # Button frame for file management
        button_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=PADDING_STANDARD, pady=PADDING_STANDARD)

        add_button = ctk.CTkButton(
            button_frame,
            text="Add CV",
            command=self._add_cv,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        )
        add_button.pack(side="left", padx=5)

        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear All",
            command=self._clear_list,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["warning"],
            hover_color="#FF7700",
        )
        clear_button.pack(side="left", padx=5)

        # Progress section
        progress_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        progress_frame.pack(fill="x", padx=PADDING_LARGE, pady=PADDING_STANDARD)

        progress_label = ctk.CTkLabel(
            progress_frame,
            text="Processing Progress:",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        progress_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        # Scrollable progress display
        self.progress_text = ctk.CTkTextbox(
            progress_frame,
            height=120,
            fg_color=COLORS["bg_primary"],
            text_color=COLORS["text_primary"],
        )
        self.progress_text.pack(
            fill="both",
            expand=True,
            padx=PADDING_STANDARD,
            pady=PADDING_STANDARD,
        )
        self.progress_text.configure(state="disabled")

        # Action buttons
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=PADDING_LARGE)

        process_button = ctk.CTkButton(
            action_frame,
            text="Start Processing",
            command=self._start_processing,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["success"],
            hover_color="#00CC00",
        )
        process_button.pack(side="left", padx=PADDING_STANDARD)

        self.cancel_button = ctk.CTkButton(
            action_frame,
            text="Cancel",
            command=self._cancel_processing,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["error"],
            hover_color="#BB0000",
            state="disabled",
        )
        self.cancel_button.pack(side="left", padx=PADDING_STANDARD)

        logger.debug("Batch panel widgets created")

    def _add_cv(self) -> None:
        """Add CV file to batch list."""
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
                    self.progress_dict[p.name] = 0
                    self.session.set_last_cv_dir(p.parent)

            self._update_file_list()
            logger.info(f"Added {len(paths)} CV(s)")

    def _clear_list(self) -> None:
        """Clear all files from batch list."""
        self.cv_files.clear()
        self.progress_dict.clear()
        self._update_file_list()
        self._update_progress_display()
        logger.info("Cleared file list")

    def _update_file_list(self) -> None:
        """Update the file list display."""
        self.file_list.configure(state="normal")
        self.file_list.delete("1.0", "end")

        if not self.cv_files:
            self.file_list.insert("1.0", "No files selected")
        else:
            for path in self.cv_files:
                self.file_list.insert("end", f"• {path.name}\n")

        self.file_list.configure(state="disabled")

    def _update_progress_display(self) -> None:
        """Update the progress display."""
        self.progress_text.configure(state="normal")
        self.progress_text.delete("1.0", "end")

        if not self.progress_dict:
            self.progress_text.insert("1.0", "No processing yet")
        else:
            for filename, percent in self.progress_dict.items():
                bar = self._make_progress_bar(percent)
                self.progress_text.insert("end", f"{filename}\n{bar} {percent}%\n\n")

        self.progress_text.configure(state="disabled")

    def _make_progress_bar(self, percent: int) -> str:
        """Create a text-based progress bar.

        Args:
            percent: Progress percentage (0-100)

        Returns:
            Text representation of progress bar.
        """
        filled = int(percent / 5)
        empty = 20 - filled
        return f"[{'=' * filled}{'-' * empty}]"

    def _start_processing(self) -> None:
        """Start processing batch of CVs."""
        if not self.cv_files:
            messagebox.showerror("Error", "Please add at least one CV file.")
            return

        if not self.session.get_template_schema():
            messagebox.showerror("Error", "Please upload a template first.")
            return

        self.is_processing = True
        self.cancel_button.configure(state="normal")

        # Clear previous progress
        self.progress_dict.clear()
        for cv_path in self.cv_files:
            self.progress_dict[cv_path.name] = 0
        self._update_progress_display()

        # Start processing in background thread
        self.processing_thread = threading.Thread(
            target=self._process_batch_worker,
            daemon=False,
        )
        self.processing_thread.start()
        logger.info(f"Starting batch processing for {len(self.cv_files)} files")

    def _process_batch_worker(self) -> None:
        """Background worker for batch processing."""
        try:
            batch_processor = BatchProcessor(self.session.config)
            template_schema = self.session.get_template_schema()

            if not template_schema:
                logger.error("Template schema not set in session")
                return

            results = batch_processor.process_batch(
                self.cv_files,
                template_schema,
                progress_callback=None,  # Progress via event queue
            )

            # Store results in session
            self.session.set_batch_results(results)

            # Log summary
            success_count = sum(1 for _, cv, err in results if cv is not None)
            logger.info(f"Batch processing complete: {success_count}/{len(results)} successful")

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
        finally:
            self.is_processing = False

    def _cancel_processing(self) -> None:
        """Cancel ongoing batch processing."""
        if self.is_processing:
            self.is_processing = False
            logger.info("Batch processing cancellation requested")
            self.cancel_button.configure(state="disabled")
            msg = (
                "Processing cancellation requested. "
                "Waiting for current tasks to complete..."
            )
            messagebox.showinfo("Info", msg)

    def update_progress(self, event: Any) -> None:  # type: ignore
        """Update progress for a single CV.

        Args:
            event: ProgressEvent from the queue.
        """
        self.progress_dict[event.cv_filename] = event.percent
        self._update_progress_display()
