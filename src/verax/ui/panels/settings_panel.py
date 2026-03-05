"""Settings panel for LLM provider, API keys, and privacy mode."""

from tkinter import messagebox

import customtkinter as ctk

from verax.core.session import Session
from verax.models.config import OutputFormat, PrivacyMode
from verax.ui.styles import (
    BUTTON_HEIGHT,
    BUTTON_WIDTH_STANDARD,
    COLORS,
    FONT_HEADING,
    FONT_STANDARD,
    PADDING_LARGE,
    PADDING_STANDARD,
)
from verax.utils import get_api_key, get_logger, save_config, set_api_key

logger = get_logger(__name__)


class SettingsPanel(ctk.CTkFrame):
    """Panel for application settings."""

    def __init__(self, master: object, session: Session, **kwargs):  # type: ignore
        """Initialize settings panel.

        Args:
            master: Parent widget
            session: Session instance
            **kwargs: Additional frame arguments
        """
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True)
        self.session = session

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create and layout settings panel widgets."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Settings",
            font=FONT_HEADING,
            text_color=COLORS["text_primary"],
        )
        title.pack(pady=PADDING_LARGE, padx=PADDING_STANDARD)

        # Scrollable frame for settings
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=PADDING_STANDARD)

        # LLM Provider section
        provider_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["bg_secondary"])
        provider_frame.pack(fill="x", pady=PADDING_STANDARD)

        provider_label = ctk.CTkLabel(
            provider_frame,
            text="LLM Provider:",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        provider_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.provider_var = ctk.StringVar(value=self.session.config.llm_provider)
        provider_menu = ctk.CTkOptionMenu(
            provider_frame,
            variable=self.provider_var,
            values=["openai", "anthropic", "local"],
            command=self._on_provider_changed,
        )
        provider_menu.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        # Privacy Mode section
        privacy_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["bg_secondary"])
        privacy_frame.pack(fill="x", pady=PADDING_STANDARD)

        privacy_label = ctk.CTkLabel(
            privacy_frame,
            text="Privacy Mode:",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        privacy_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.privacy_var = ctk.StringVar(value=self.session.config.privacy_mode.value)
        privacy_menu = ctk.CTkOptionMenu(
            privacy_frame,
            variable=self.privacy_var,
            values=["full", "template_only", "offline"],
            command=self._on_privacy_changed,
        )
        privacy_menu.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        privacy_info = ctk.CTkLabel(
            privacy_frame,
            text="full: All API calls | template_only: No enhancement | offline: Local only",
            font=("Arial", 8),
            text_color=COLORS["text_secondary"],
        )
        privacy_info.pack(pady=5, padx=PADDING_STANDARD)

        # OpenAI API Key section
        openai_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["bg_secondary"])
        openai_frame.pack(fill="x", pady=PADDING_STANDARD)

        openai_label = ctk.CTkLabel(
            openai_frame,
            text="OpenAI API Key:",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        openai_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.openai_key_var = ctk.StringVar(value="••••••••" if get_api_key("openai") else "")
        openai_entry = ctk.CTkEntry(
            openai_frame,
            textvariable=self.openai_key_var,
            show="•",
            placeholder_text="sk-...",
        )
        openai_entry.pack(fill="x", padx=PADDING_STANDARD, pady=5)

        # Anthropic API Key section
        anthropic_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["bg_secondary"])
        anthropic_frame.pack(fill="x", pady=PADDING_STANDARD)

        anthropic_label = ctk.CTkLabel(
            anthropic_frame,
            text="Anthropic API Key:",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        anthropic_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.anthropic_key_var = ctk.StringVar(value="••••••••" if get_api_key("anthropic") else "")
        anthropic_entry = ctk.CTkEntry(
            anthropic_frame,
            textvariable=self.anthropic_key_var,
            show="•",
            placeholder_text="sk-ant-...",
        )
        anthropic_entry.pack(fill="x", padx=PADDING_STANDARD, pady=5)

        # Output Formats section
        output_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["bg_secondary"])
        output_frame.pack(fill="x", pady=PADDING_STANDARD)

        output_label = ctk.CTkLabel(
            output_frame,
            text="Output Formats:",
            font=FONT_STANDARD,
            text_color=COLORS["text_primary"],
        )
        output_label.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        self.docx_var = ctk.BooleanVar(
            value=OutputFormat.DOCX in self.session.config.output_formats
        )
        docx_check = ctk.CTkCheckBox(
            output_frame,
            text="DOCX",
            variable=self.docx_var,
            command=self._on_format_changed,
        )
        docx_check.pack(anchor="w", padx=PADDING_STANDARD, pady=5)

        self.pdf_var = ctk.BooleanVar(
            value=OutputFormat.PDF in self.session.config.output_formats
        )
        pdf_check = ctk.CTkCheckBox(
            output_frame,
            text="PDF",
            variable=self.pdf_var,
            command=self._on_format_changed,
        )
        pdf_check.pack(anchor="w", padx=PADDING_STANDARD, pady=5)

        self.html_var = ctk.BooleanVar(
            value=OutputFormat.HTML in self.session.config.output_formats
        )
        html_check = ctk.CTkCheckBox(
            output_frame,
            text="HTML",
            variable=self.html_var,
            command=self._on_format_changed,
        )
        html_check.pack(anchor="w", padx=PADDING_STANDARD, pady=5)

        # Enhancement toggle
        enhance_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["bg_secondary"])
        enhance_frame.pack(fill="x", pady=PADDING_STANDARD)

        self.enhance_var = ctk.BooleanVar(value=self.session.config.enhance_text)
        enhance_check = ctk.CTkCheckBox(
            enhance_frame,
            text="Enhance text with LLM (improves clarity and impact)",
            variable=self.enhance_var,
            command=self._on_enhance_changed,
        )
        enhance_check.pack(anchor="w", padx=PADDING_STANDARD, pady=PADDING_STANDARD)

        # Action buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=PADDING_LARGE)

        save_button = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            command=self._save_settings,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH_STANDARD,
            fg_color=COLORS["success"],
            hover_color="#00CC00",
        )
        save_button.pack(side="left", padx=PADDING_STANDARD)

        logger.debug("Settings panel widgets created")

    def _on_provider_changed(self, value: str) -> None:
        """Handle LLM provider change.

        Args:
            value: New provider name.
        """
        self.session.config.llm_provider = value
        logger.debug(f"LLM provider changed to {value}")

    def _on_privacy_changed(self, value: str) -> None:
        """Handle privacy mode change.

        Args:
            value: New privacy mode value.
        """
        self.session.config.privacy_mode = PrivacyMode(value)
        logger.debug(f"Privacy mode changed to {value}")

    def _on_format_changed(self) -> None:
        """Handle output format changes."""
        formats = []
        if self.docx_var.get():
            formats.append(OutputFormat.DOCX)
        if self.pdf_var.get():
            formats.append(OutputFormat.PDF)
        if self.html_var.get():
            formats.append(OutputFormat.HTML)

        self.session.config.output_formats = formats
        logger.debug(f"Output formats changed to {formats}")

    def _on_enhance_changed(self) -> None:
        """Handle text enhancement toggle."""
        self.session.config.enhance_text = self.enhance_var.get()
        logger.debug(f"Text enhancement set to {self.enhance_var.get()}")

    def _save_settings(self) -> None:
        """Save settings to storage."""
        try:
            # Save API keys (only if they've been modified)
            openai_key = self.openai_key_var.get()
            if openai_key and openai_key != "••••••••":
                set_api_key("openai", openai_key)
                logger.info("OpenAI API key saved to keyring")

            anthropic_key = self.anthropic_key_var.get()
            if anthropic_key and anthropic_key != "••••••••":
                set_api_key("anthropic", anthropic_key)
                logger.info("Anthropic API key saved to keyring")

            # Persist AppConfig to disk
            save_config(self.session.config)
            logger.info("AppConfig saved to disk")

            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings:\n\n{str(e)}")
