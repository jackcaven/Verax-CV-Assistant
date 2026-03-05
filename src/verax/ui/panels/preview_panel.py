"""Preview panel for viewing and editing structured CV."""

import customtkinter as ctk

from verax.core.session import Session
from verax.utils import get_logger
from verax.ui.styles import (
    COLORS,
    PADDING_STANDARD,
    PADDING_LARGE,
    FONT_HEADING,
    FONT_STANDARD,
    BUTTON_HEIGHT,
    BUTTON_WIDTH_STANDARD,
)

logger = get_logger(__name__)


class PreviewPanel(ctk.CTkFrame):
    """Panel for previewing and editing structured CV."""

    def __init__(self, master, session: Session, **kwargs):
        """Initialize preview panel.

        Args:
            master: Parent widget
            session: Session instance
            **kwargs: Additional frame arguments
        """
        super().__init__(master, **kwargs)
        self.session = session
        self.cv_display: ctk.CTkTextbox | None = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and layout preview panel widgets."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Preview & Edit",
            font=FONT_HEADING,
            text_color=COLORS["text_primary"],
        )
        title.pack(pady=PADDING_LARGE, padx=PADDING_STANDARD)

        # Info label
        info_label = ctk.CTkLabel(
            self,
            text="View the extracted and processed CV structure",
            font=("Arial", 9),
            text_color=COLORS["text_secondary"],
        )
        info_label.pack(pady=5, padx=PADDING_STANDARD)

        # CV display textbox
        self.cv_display = ctk.CTkTextbox(
            self,
            height=350,
            fg_color=COLORS["bg_secondary"],
            text_color=COLORS["text_primary"],
        )
        self.cv_display.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=PADDING_STANDARD)
        self.cv_display.configure(state="disabled")

        # Action buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=PADDING_LARGE)

        reload_button = ctk.CTkButton(
            button_frame,
            text="Reload",
            command=self._reload_preview,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        )
        reload_button.pack(side="left", padx=PADDING_STANDARD)

        logger.debug("Preview panel widgets created")
        self._reload_preview()

    def _reload_preview(self) -> None:
        """Reload the CV preview."""
        if not self.cv_display:
            return

        self.cv_display.configure(state="normal")
        self.cv_display.delete("1.0", "end")

        cv = self.session.get_current_cv()
        if not cv:
            self.cv_display.insert("1.0", "No CV loaded yet.\n\nUpload and process a CV to see preview.")
            self.cv_display.configure(state="disabled")
            return

        # Format and display CV
        text_parts = []

        # Contact info
        text_parts.append("=== CONTACT INFO ===\n")
        text_parts.append(f"Name: {cv.contact_info.name}\n")
        if cv.contact_info.email:
            text_parts.append(f"Email: {cv.contact_info.email}\n")
        if cv.contact_info.phone:
            text_parts.append(f"Phone: {cv.contact_info.phone}\n")
        if cv.contact_info.location:
            text_parts.append(f"Location: {cv.contact_info.location}\n")
        if cv.contact_info.website:
            text_parts.append(f"Website: {cv.contact_info.website}\n")
        if cv.contact_info.linkedin:
            text_parts.append(f"LinkedIn: {cv.contact_info.linkedin}\n")

        # Sections
        text_parts.append("\n")
        for section in cv.sections:
            text_parts.append(f"\n=== {section.title.upper()} ===\n")
            if section.entries:
                for entry in section.entries:
                    text_parts.append(f"\n{entry.title}")
                    if entry.subtitle:
                        text_parts.append(f" | {entry.subtitle}")
                    if entry.dates:
                        text_parts.append(f" ({entry.dates})")
                    text_parts.append("\n")
                    if entry.description:
                        text_parts.append(f"{entry.description}\n")
            else:
                text_parts.append("[No entries]\n")

        display_text = "".join(text_parts)
        self.cv_display.insert("1.0", display_text)
        self.cv_display.configure(state="disabled")
        logger.info("Preview reloaded")
