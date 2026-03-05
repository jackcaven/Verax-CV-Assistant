"""Upload panel for selecting CV and template files."""

import customtkinter as ctk
from pathlib import Path
from typing import Optional
from tkinter import filedialog, messagebox

from verax.core.session import Session
from verax.template.docx_extractor import DoxcTemplateExtractor
from verax.template.pdf_extractor import PdfTemplateExtractor
from verax.template.fallback import get_fallback_template
from verax.utils import get_logger
from verax.ui.styles import (
    COLORS,
    PADDING_STANDARD,
    PADDING_LARGE,
    FONT_HEADING,
    FONT_STANDARD,
    BUTTON_HEIGHT,
    BUTTON_WIDTH_STANDARD,
    SUPPORTED_CV_FORMATS,
    SUPPORTED_TEMPLATE_FORMATS,
)

logger = get_logger(__name__)


class UploadPanel(ctk.CTkFrame):
    """Panel for uploading CV and template files."""

    def __init__(self, master, session: Session, app=None, **kwargs):
        """Initialize upload panel.

        Args:
            master: Parent widget
            session: Session instance for storing state
            app: VeraxApp instance for tab switching
            **kwargs: Additional frame arguments
        """
        super().__init__(master, **kwargs)
        self.session = session
        self.app = app
        self.cv_path: Optional[Path] = None
        self.template_path: Optional[Path] = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and layout upload panel widgets."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Upload CV and Template",
            font=FONT_HEADING,
            text_color=COLORS["text_primary"],
        )
        title.pack(pady=PADDING_LARGE, padx=PADDING_STANDARD)

        # CV section
        cv_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        cv_frame.pack(fill="x", padx=PADDING_LARGE, pady=PADDING_STANDARD)

        cv_label = ctk.CTkLabel(
            cv_frame,
            text="Select CV File:",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        cv_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.cv_path_label = ctk.CTkLabel(
            cv_frame,
            text="No file selected",
            font=("Arial", 9),
            text_color=COLORS["text_secondary"],
        )
        self.cv_path_label.pack(pady=5, padx=PADDING_STANDARD)

        cv_button = ctk.CTkButton(
            cv_frame,
            text="Browse CV",
            command=self._select_cv,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        )
        cv_button.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        # Template section
        template_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"])
        template_frame.pack(fill="x", padx=PADDING_LARGE, pady=PADDING_STANDARD)

        template_label = ctk.CTkLabel(
            template_frame,
            text="Select Template File (Optional):",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        template_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.template_path_label = ctk.CTkLabel(
            template_frame,
            text="No file selected (will use default)",
            font=("Arial", 9),
            text_color=COLORS["text_secondary"],
        )
        self.template_path_label.pack(pady=5, padx=PADDING_STANDARD)

        template_button = ctk.CTkButton(
            template_frame,
            text="Browse Template",
            command=self._select_template,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        )
        template_button.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        # Action buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=PADDING_LARGE)

        next_button = ctk.CTkButton(
            button_frame,
            text="Next: Batch Process",
            command=self._go_to_batch,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["success"],
            hover_color="#00CC00",
        )
        next_button.pack(side="left", padx=PADDING_STANDARD)

        logger.debug("Upload panel widgets created")

    def _select_cv(self) -> None:
        """Open file dialog to select CV file."""
        path = filedialog.askopenfilename(
            title="Select CV File",
            filetypes=SUPPORTED_CV_FORMATS,
            initialdir=self.session.get_last_cv_dir(),
        )
        if path:
            self.cv_path = Path(path)
            self.cv_path_label.configure(text=self.cv_path.name)
            self.session.set_last_cv_dir(self.cv_path.parent)
            logger.info(f"CV selected: {self.cv_path}")

    def _select_template(self) -> None:
        """Open file dialog to select template file."""
        path = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=SUPPORTED_TEMPLATE_FORMATS,
            initialdir=self.session.get_last_cv_dir(),
        )
        if path:
            self.template_path = Path(path)
            self.template_path_label.configure(text=self.template_path.name)
            logger.info(f"Template selected: {self.template_path}")

    def _go_to_batch(self) -> None:
        """Navigate to batch processing tab."""
        if not self.cv_path:
            messagebox.showerror("Error", "Please select a CV file first.")
            return

        try:
            # Extract template schema
            if self.template_path:
                template_schema = self._extract_template(self.template_path)
                logger.info(f"Extracted template from {self.template_path.name}: {len(template_schema.sections)} sections")
            else:
                # Use fallback template
                fallback_path = get_fallback_template()
                template_schema = self._extract_template(fallback_path)
                logger.info(f"Using fallback template: {len(template_schema.sections)} sections")

            # Store in session
            template_path = self.template_path or get_fallback_template()
            self.session.set_template(template_path, template_schema)

            # Switch to batch tab
            if self.app:
                self.app.tabview.set("Batch Process")
            else:
                logger.warning("App reference not available; cannot switch tabs")

            messagebox.showinfo(
                "Success",
                f"Template extracted: {len(template_schema.sections)} sections detected.\n\n"
                "You can now add CV files for batch processing.",
            )

        except Exception as e:
            logger.error(f"Error extracting template: {e}")
            messagebox.showerror("Error", f"Failed to extract template:\n\n{str(e)}")

    def _extract_template(self, template_path: Path):
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
            extractor = PdfTemplateExtractor()
            return extractor.extract(template_path)
        else:
            raise ValueError(f"Unsupported template format: {suffix}")

    def get_cv_path(self) -> Optional[Path]:
        """Get selected CV path.

        Returns:
            Path to selected CV or None.
        """
        return self.cv_path

    def get_template_path(self) -> Optional[Path]:
        """Get selected template path.

        Returns:
            Path to selected template or None.
        """
        return self.template_path
