"""Main application window for Verax CV Assistant."""

from typing import Optional

import customtkinter as ctk

from verax.core.session import Session
from verax.models.config import AppConfig
from verax.ui.panels.process_panel import ProcessPanel
from verax.ui.panels.settings_panel import SettingsPanel
from verax.ui.styles import (
    COLORS,
    PADDING_STANDARD,
    TABS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from verax.utils import get_logger
from verax.utils.events import progress_queue

logger = get_logger(__name__)


class VeraxApp(ctk.CTk):
    """Main application window with tabbed interface."""

    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize the application.

        Args:
            config: AppConfig instance. If None, creates default config.
        """
        super().__init__()

        # Setup window
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(800, 600)

        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Initialize session and config
        self.config = config or AppConfig()
        self.session = Session(self.config)

        # Create UI
        self._create_widgets()

        # Start progress polling
        self.poll_progress()

        logger.info("VeraxApp initialized")

    def _create_widgets(self) -> None:
        """Create and layout all UI widgets."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        header = ctk.CTkLabel(
            main_frame,
            text="Verax CV Assistant",
            font=("Arial", 20, "bold"),
            text_color=COLORS["text_primary"],
        )
        header.pack(pady=PADDING_STANDARD, padx=PADDING_STANDARD)

        # Tabview
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=PADDING_STANDARD, pady=PADDING_STANDARD)

        # Create tabs
        self.process_panel = ProcessPanel(
            self.tabview.add(TABS["process"]),
            session=self.session,
        )
        self.settings_panel = SettingsPanel(
            self.tabview.add(TABS["settings"]),
            session=self.session,
        )

        # Status bar at bottom
        self.status_bar = ctk.CTkLabel(
            self,
            text="Ready",
            text_color=COLORS["text_secondary"],
            font=("Arial", 9),
        )
        self.status_bar.pack(fill="x", padx=PADDING_STANDARD, pady=5)

        logger.debug("UI widgets created")

    def poll_progress(self) -> None:
        """Poll progress queue and update UI.

        This runs on the main thread and is called periodically via after().
        """
        while not progress_queue.empty():
            try:
                event = progress_queue.get_nowait()
                self._handle_progress_event(event)
            except Exception:
                break

        # Schedule next poll
        self.after(50, self.poll_progress)

    def _handle_progress_event(self, event: object) -> None:  # type: ignore
        """Handle a progress event from the queue.

        Args:
            event: ProgressEvent instance.
        """
        # Update status bar
        if event.stage == "complete":  # type: ignore
            self.status_bar.configure(text=f"✓ {event.cv_filename} complete")  # type: ignore
        elif event.stage == "error":  # type: ignore
            self.status_bar.configure(text=f"✗ {event.cv_filename} failed")  # type: ignore
        else:
            self.status_bar.configure(text=f"{event.cv_filename}: {event.stage} ({event.percent}%)")  # type: ignore

        # Delegate to process panel for progress log update
        self.process_panel.update_progress(event)

    def run(self) -> None:
        """Start the application event loop."""
        logger.info("Starting application event loop")
        self.mainloop()


def create_app(config: Optional[AppConfig] = None) -> VeraxApp:
    """Factory function to create and return the app.

    Args:
        config: Optional AppConfig instance.

    Returns:
        VeraxApp instance.
    """
    return VeraxApp(config=config)
