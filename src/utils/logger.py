from configs.settings import get_settings
import logging
import sys

_configured = False

def configure_logging() -> None:
    """Configure root logging once from application settings."""
    global _configured
    if _configured:
        return

    settings = get_settings()
    level_name = settings.log_level.upper()
    level = getattr(logging, level_name, logging.INFO)

    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            stream=sys.stdout,
        )
    else:
        root.setLevel(level)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger (e.g. pass ``__name__``)."""
    configure_logging()
    return logging.getLogger(name)