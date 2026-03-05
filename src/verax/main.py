"""Main entry point for Verax CV Assistant."""

import sys

from verax.ui.app import create_app
from verax.utils import get_logger, load_config, setup_logging

logger = get_logger(__name__)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    setup_logging(debug=False)
    logger.info("Verax CV Assistant starting...")

    try:
        # Load config from disk or use defaults
        config = load_config()
        app = create_app(config=config)
        logger.info("App initialized successfully")

        # Run app event loop
        app.run()
        return 0
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
