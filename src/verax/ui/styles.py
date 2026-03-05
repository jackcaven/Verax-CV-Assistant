"""UI styles and color scheme for CustomTkinter."""

# Color scheme (CustomTkinter light mode)
COLORS = {
    "primary": "#0084FF",
    "primary_hover": "#0063C4",
    "success": "#00AA00",
    "error": "#DD0000",
    "warning": "#FF9900",
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F5F5F5",
    "text_primary": "#000000",
    "text_secondary": "#666666",
    "border": "#CCCCCC",
}

# Standard padding and spacing
PADDING_SMALL = 5
PADDING_STANDARD = 10
PADDING_LARGE = 20

# Window dimensions
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Verax CV Assistant"

# Font sizes
FONT_HEADING = ("Arial", 16, "bold")
FONT_SUBHEADING = ("Arial", 12, "bold")
FONT_STANDARD = ("Arial", 10)
FONT_SMALL = ("Arial", 9)

# Tab names
TABS = {
    "process": "Process",
    "settings": "Settings",
}

# Button sizes
BUTTON_HEIGHT = 40
BUTTON_WIDTH_SMALL = 100
BUTTON_WIDTH_STANDARD = 150
BUTTON_WIDTH_LARGE = 200

# Progress display
PROGRESS_HEIGHT = 5
STATUS_BAR_HEIGHT = 30

# File dialog settings
SUPPORTED_CV_FORMATS = (("CV files", "*.docx *.pdf *.doc"), ("All files", "*.*"))
SUPPORTED_TEMPLATE_FORMATS = (("Template files", "*.docx *.pdf"), ("All files", "*.*"))
