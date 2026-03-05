"""Main entry point for Verax CV Assistant."""

import sys
from verax.utils import setup_logging, get_logger

logger = get_logger(__name__)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    setup_logging(debug=False)
    logger.info("Verax CV Assistant starting...")

    try:
        # Placeholder for UI initialization
        logger.info("App initialized successfully")
        return 0
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
