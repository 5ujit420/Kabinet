import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure structured application logging.

    Call once at application startup. Uses a consistent format
    with timestamp, level, and logger name.

    Never log passwords, access tokens, refresh tokens,
    password-reset tokens, or API secrets.
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers on repeated calls
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Silence overly chatty third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
